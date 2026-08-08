from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.users import StaffUser  # noqa: F401


def test_create_list_and_update_staff_user() -> None:
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

    create_response = client.post(
        "/api/v1/users/",
        json={
            "full_name": "Dra. Ana Martinez",
            "phone": "9999-1111",
            "roles": ["doctor", "receptionist"],
            "area": "clinic",
            "active": True,
            "on_shift": True,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["full_name"] == "Dra. Ana Martinez"
    assert "doctor" in created["roles"]

    list_response = client.get("/api/v1/users/?active=true&role=doctor")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    update_response = client.patch(
        f"/api/v1/users/{created['id']}",
        json={"on_shift": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["on_shift"] is False

    # Regresion: los permisos que init_db otorga al admin inicial deben ser
    # validos para StaffModule; si el schema queda desfasado, el login del
    # admin sembrado devuelve 500 en una instalacion limpia.
    admin_permissions = [
        "dashboard",
        "patients",
        "appointments",
        "consultations",
        "staff",
        "pharmacy",
        "inventory",
        "cash_registers",
        "reports",
        "audit",
        "settings",
    ]
    admin_response = client.post(
        "/api/v1/users/",
        json={
            "full_name": "Admin Completo",
            "roles": ["admin"],
            "module_permissions": admin_permissions,
            "area": "both",
            "active": True,
            "on_shift": True,
        },
    )
    assert admin_response.status_code == 201
    assert admin_response.json()["module_permissions"] == admin_permissions

    app.dependency_overrides.clear()
