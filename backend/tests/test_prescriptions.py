from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.consultations import Consultation  # noqa: F401
from app.modules.patients import Patient  # noqa: F401
from app.modules.prescriptions import Prescription, PrescriptionItem  # noqa: F401


def test_create_and_list_prescriptions() -> None:
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
            "full_name": "Carlos Mejia",
            "phone": "9999-0002",
            "identity_number": "0801-1991-00002",
            "birth_date": "1991-09-02",
            "sex": "male",
            "address": "Colonia Kennedy",
            "allergies": "Ninguna registrada",
            "known_conditions": "Diabetes tipo 2",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        "/api/v1/consultations/",
        json={
            "patient_id": patient_id,
            "doctor_name": "Dr. Principal",
            "doctor_specialty": "Medicina general",
            "clinical_history": "Dolor de cabeza",
            "diagnosis": "Cefalea tensional",
            "treatment": "Analgesico y reposo",
        },
    )
    assert consultation_response.status_code == 201
    consultation_id = consultation_response.json()["id"]

    response = client.post(
        "/api/v1/prescriptions/",
        json={
            "patient_id": patient_id,
            "consultation_id": consultation_id,
            "doctor_name": "Dr. Principal",
            "doctor_specialty": "Medicina general",
            "general_notes": "Tomar con alimentos.",
            "items": [
                {
                    "medication_name": "Acetaminofen 500 mg",
                    "dose": "1 tableta",
                    "frequency": "cada 8 horas",
                    "duration": "3 dias",
                    "instructions": "Suspender si hay reaccion adversa.",
                }
            ],
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["patient_id"] == patient_id
    assert created["consultation_id"] == consultation_id
    assert created["doctor_specialty"] == "Medicina general"
    assert created["items"][0]["medication_name"] == "Acetaminofen 500 mg"

    list_response = client.get(f"/api/v1/prescriptions/?patient_id={patient_id}")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == created["id"]

    consultations_response = client.get(f"/api/v1/consultations/?patient_id={patient_id}")
    assert consultations_response.status_code == 200
    assert consultations_response.json()[0]["has_prescription"] is True

    app.dependency_overrides.clear()
