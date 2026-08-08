from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.patients import Patient  # noqa: F401


def test_create_and_list_patients() -> None:
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

    response = client.post(
        "/api/v1/patients/",
        json={
            "full_name": "Javier Oliva",
            "phone": "92398074",
            "identity_number": "93232",
            "birth_date": "1926-01-01",
            "sex": "female",
            "address": "No registrada",
            "allergies": "ninguna",
            "known_conditions": "ninguna",
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["full_name"] == "Javier Oliva"
    assert created["identity_number"] == "93232"

    list_response = client.get("/api/v1/patients/?search=Javier")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == created["id"]

    app.dependency_overrides.clear()
