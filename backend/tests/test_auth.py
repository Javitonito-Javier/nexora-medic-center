from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.users import StaffUser  # noqa: F401


def test_login_and_admin_password_reset() -> None:
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

    created = client.post(
        "/api/v1/users/",
        json={
            "full_name": "Dra. Reset",
            "username": "reset",
            "password": "oldpass123",
            "phone": "",
            "roles": ["doctor"],
            "area": "clinic",
            "active": True,
            "on_shift": True,
        },
    ).json()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "reset", "password": "oldpass123"},
    )
    assert login_response.status_code == 200

    reset_response = client.patch(
        f"/api/v1/users/{created['id']}",
        json={"password": "newpass123"},
    )
    assert reset_response.status_code == 200

    old_login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "reset", "password": "oldpass123"},
    )
    assert old_login_response.status_code == 401

    new_login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "reset", "password": "newpass123"},
    )
    assert new_login_response.status_code == 200

    app.dependency_overrides.clear()
