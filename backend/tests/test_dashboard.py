from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.modules.appointments import Appointment  # noqa: F401
from app.modules.consultations import Consultation  # noqa: F401
from app.modules.inventory import InventoryLot, Product  # noqa: F401
from app.modules.pharmacy import PharmacySale, PharmacySaleItem  # noqa: F401


def test_dashboard_summary_returns_real_sections() -> None:
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

    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200
    data = response.json()
    metric_titles = [metric["title"] for metric in data["metrics"]]
    assert "Ventas farmacia hoy" in metric_titles
    assert "Utilidad farmacia mes" in metric_titles
    assert "Total del mes" not in metric_titles
    assert data["alerts"]

    app.dependency_overrides.clear()
