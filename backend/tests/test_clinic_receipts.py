from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.patients import Patient  # noqa: F401
from app.modules.receipts import ClinicReceipt  # noqa: F401


def test_create_clinic_receipt_and_text() -> None:
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
            "full_name": "Paciente Recibo",
            "phone": "9999-1111",
            "identity_number": "REC-001",
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
            "document_type": "receipt",
            "payment_method": "transfer",
            "payment_reference": "TRX-CLINICA-001",
            "bank_name": "Ficohsa",
            "description": "Consulta general",
            "subtotal": 500,
            "discount": 50,
        },
    )
    assert receipt_response.status_code == 201
    receipt = receipt_response.json()
    assert receipt["total"] == 450
    assert receipt["patient_name"] == "Paciente Recibo"
    assert receipt["payment_reference"] == "TRX-CLINICA-001"
    assert receipt["bank_name"] == "Ficohsa"

    text_response = client.get(f"/api/v1/receipts/clinic/{receipt['id']}/text")
    assert text_response.status_code == 200
    assert "RECIBO" in text_response.json()["content"]
    assert "Consulta general" in text_response.json()["content"]
    assert "Banco: Ficohsa" in text_response.json()["content"]
    assert "Comprobante: TRX-CLINICA-001" in text_response.json()["content"]

    app.dependency_overrides.clear()
