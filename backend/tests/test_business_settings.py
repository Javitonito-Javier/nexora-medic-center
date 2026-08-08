from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.business import BusinessSettings  # noqa: F401
from app.modules.patients import Patient  # noqa: F401
from app.modules.receipts import ClinicReceipt  # noqa: F401


def test_business_settings_are_used_in_clinic_invoice_text() -> None:
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

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    settings_response = client.put(
        "/api/v1/business/settings",
        json={
            "trade_name": "Farmacia Esperanza",
            "legal_name": "Esperanza Salud S. de R.L.",
            "rtn": "08011999000000",
            "address": "Tegucigalpa",
            "phone": "2222-3333",
            "email": "info@example.com",
            "logo_url": "http://localhost/logo.png",
            "logo_data_url": "",
            "invoice_enabled": True,
            "fiscal_enabled": True,
            "fiscal_regime": "Regimen general",
            "cai": "CAI-123",
            "invoice_range_start": "000-001-01-00000001",
            "invoice_range_end": "000-001-01-00000100",
            "current_invoice_number": "000-001-01-00000001",
            "establishment_code": "000",
            "emission_point_code": "001",
            "invoice_limit_date": "2026-12-31",
            "receipt_footer": "Gracias por preferirnos",
            "invoice_footer": "Factura autorizada por SAR",
            "age_discount_note": "Descuentos legales segun corresponda",
            "thermal_paper_width": "80mm",
        },
    )
    assert settings_response.status_code == 200
    assert settings_response.json()["trade_name"] == "Farmacia Esperanza"

    patient_response = client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Paciente Fiscal",
            "phone": "9999-1111",
            "identity_number": "FISCAL-001",
            "birth_date": "1990-01-01",
            "sex": "female",
            "address": "",
        },
    )
    assert patient_response.status_code == 201
    patient = patient_response.json()

    receipt_response = client.post(
        "/api/v1/receipts/clinic",
        json={
            "patient_id": patient["id"],
            "cashier_name": "Recepcion",
            "doctor_name": "Dra Demo",
            "document_type": "invoice",
            "payment_method": "cash",
            "description": "Consulta fiscal",
            "subtotal": 500,
            "discount": 0,
        },
    )
    assert receipt_response.status_code == 201

    text_response = client.get(f"/api/v1/receipts/clinic/{receipt_response.json()['id']}/text")
    assert text_response.status_code == 200
    content = text_response.json()["content"]
    assert "Farmacia Esperanza" in content
    assert "RTN: 08011999000000" in content
    assert "CAI: CAI-123" in content
    assert "Rango: 000-001-01-00000001 al 000-001-01-00000100" in content
    assert "Factura autorizada por SAR" in content

    app.dependency_overrides.clear()


def test_invoice_document_is_blocked_when_not_enabled() -> None:
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

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    patient_response = client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Paciente Sin CAI",
            "phone": "9999-1111",
            "identity_number": "NO-CAI-001",
            "birth_date": "1990-01-01",
            "sex": "female",
            "address": "",
        },
    )
    assert patient_response.status_code == 201
    patient = patient_response.json()

    invoice_response = client.post(
        "/api/v1/receipts/clinic",
        json={
            "patient_id": patient["id"],
            "cashier_name": "Recepcion",
            "doctor_name": "Dra Demo",
            "document_type": "invoice",
            "payment_method": "cash",
            "description": "Consulta sin CAI",
            "subtotal": 500,
            "discount": 0,
        },
    )
    assert invoice_response.status_code == 400
    assert "facturas no esta autorizada" in invoice_response.json()["detail"]

    receipt_response = client.post(
        "/api/v1/receipts/clinic",
        json={
            "patient_id": patient["id"],
            "cashier_name": "Recepcion",
            "doctor_name": "Dra Demo",
            "document_type": "receipt",
            "payment_method": "cash",
            "description": "Consulta con recibo",
            "subtotal": 500,
            "discount": 0,
        },
    )
    assert receipt_response.status_code == 201

    app.dependency_overrides.clear()
