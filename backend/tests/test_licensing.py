import base64
import json
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.main as main_module
from app.core.config import settings
from app.db.session import Base, get_db
from app.main import app
from app.modules.licensing import SystemLicense  # noqa: F401
from app.modules.patients import Patient  # noqa: F401


def test_license_blocks_writes_until_valid_license_is_activated() -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )
    original_enabled = settings.license_enforcement_enabled
    original_public_key = settings.license_public_key
    original_session_local = main_module.SessionLocal
    settings.license_enforcement_enabled = True
    settings.license_public_key = _b64encode(public_key)
    main_module.SessionLocal = testing_session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    try:
        blocked_response = client.post(
            "/api/v1/patients/",
            json={
                "full_name": "Paciente Bloqueado",
                "phone": "9999-9999",
                "identity_number": "LIC-BLOCK",
                "birth_date": "1990-01-01",
                "sex": "female",
                "address": "",
            },
        )
        assert blocked_response.status_code == 402

        license_key = _make_license(private_key)
        activate_response = client.post(
            "/api/v1/license/activate",
            json={"license_key": license_key},
        )
        assert activate_response.status_code == 200
        assert activate_response.json()["status"] == "active"
        assert activate_response.json()["can_write"] is True

        patient_response = client.post(
            "/api/v1/patients/",
            json={
                "full_name": "Paciente Licenciado",
                "phone": "9999-9999",
                "identity_number": "LIC-OK",
                "birth_date": "1990-01-01",
                "sex": "female",
                "address": "",
            },
        )
        assert patient_response.status_code == 201
    finally:
        settings.license_enforcement_enabled = original_enabled
        settings.license_public_key = original_public_key
        main_module.SessionLocal = original_session_local
        app.dependency_overrides.clear()


def _make_license(private_key: Ed25519PrivateKey) -> str:
    payload = {
        "customer_name": "Cliente QA",
        "installation_id": "QA-LOCAL",
        "issued_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "expires_at": (datetime.now(UTC) + timedelta(days=30)).replace(microsecond=0).isoformat(),
        "modules": ["clinic", "pharmacy"],
    }
    payload_json = json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    payload_part = _b64encode(payload_json.encode("utf-8"))
    signature = private_key.sign(payload_part.encode("ascii"))
    return payload_part + "." + _b64encode(signature)


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")
