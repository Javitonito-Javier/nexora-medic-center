from collections.abc import Generator
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.appointments import Appointment  # noqa: F401
from app.modules.patients import Patient  # noqa: F401


def test_create_list_and_update_appointment() -> None:
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
            "full_name": "Paciente Agenda",
            "phone": "9999-4444",
            "identity_number": "0801-1995-0003",
            "birth_date": "1995-04-10",
            "sex": "female",
            "address": "Tegucigalpa",
            "allergies": "Ninguna",
            "known_conditions": "Ninguna",
        },
    )
    assert patient_response.status_code == 201
    patient_id = patient_response.json()["id"]
    scheduled_at = (datetime.now(UTC) + timedelta(days=1)).isoformat()

    create_response = client.post(
        "/api/v1/appointments/",
        json={
            "patient_id": patient_id,
            "scheduled_at": scheduled_at,
            "reason": "Control general",
            "doctor_name": "Dr. Principal",
            "status": "scheduled",
            "notes": "Primera cita",
        },
    )
    assert create_response.status_code == 201
    appointment = create_response.json()
    assert appointment["patient_id"] == patient_id
    assert appointment["reason"] == "Control general"

    list_response = client.get(f"/api/v1/appointments/?patient_id={patient_id}")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/api/v1/appointments/{appointment['id']}",
        json={"status": "confirmed"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "confirmed"

    app.dependency_overrides.clear()
