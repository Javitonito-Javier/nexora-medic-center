from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.consultations import Consultation  # noqa: F401
from app.modules.patients import Patient  # noqa: F401


def test_create_and_list_patient_consultations() -> None:
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
            "full_name": "Maria Lopez",
            "phone": "9999-0001",
            "identity_number": "0801-1970-00001",
            "birth_date": "1970-04-18",
            "sex": "female",
            "address": "Barrio El Centro",
            "allergies": "Penicilina",
            "known_conditions": "Hipertension",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        "/api/v1/consultations/",
        json={
            "patient_id": patient_id,
            "doctor_name": "Dr. Principal",
            "doctor_specialty": "Medicina general",
            "nurse_name": "",
            "referred_by_doctor": "",
            "referred_to_specialty": "Medicina interna",
            "referral_reason": "Evaluar control metabolico",
            "blood_pressure": "125/80",
            "heart_rate": "76",
            "oxygen_saturation": "98",
            "weight": "145 lb",
            "temperature": "36.7",
            "next_appointment_date": "2026-07-01",
            "clinical_history": "Control de presion arterial",
            "diagnosis": "Hipertension controlada",
            "treatment": "Continuar tratamiento",
            "follow_up_notes": "Revisar respuesta a interconsulta.",
            "internal_notes": "",
            "has_prescription": False,
        },
    )

    assert consultation_response.status_code == 201
    created = consultation_response.json()
    assert created["patient_id"] == patient_id
    assert created["clinical_history"] == "Control de presion arterial"
    assert created["doctor_specialty"] == "Medicina general"
    assert created["referred_to_specialty"] == "Medicina interna"
    assert created["follow_up_notes"] == "Revisar respuesta a interconsulta."

    list_response = client.get(f"/api/v1/consultations/?patient_id={patient_id}")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == created["id"]

    app.dependency_overrides.clear()
