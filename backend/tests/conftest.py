from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app
from app.core.config import settings

# Import all models so SQLAlchemy registers them
from app.modules.users import StaffUser  # noqa: F401
from app.modules.attachments import PatientAttachment  # noqa: F401
from app.modules.audit import AuditEvent  # noqa: F401
from app.modules.patients import Patient  # noqa: F401
from app.modules.cash_registers import CashRegisterSession  # noqa: F401
from app.modules.appointments import Appointment  # noqa: F401
from app.modules.consultations import Consultation  # noqa: F401
from app.modules.prescriptions import Prescription, PrescriptionItem  # noqa: F401
from app.modules.inventory import Product, ProductPresentation, InventoryLot, InventoryLotPrice, InventoryMovement  # noqa: F401
from app.modules.pharmacy import PharmacySale, PharmacySaleItem, PharmacySaleLotAllocation  # noqa: F401
from app.modules.receipts import ClinicReceipt  # noqa: F401
from app.modules.points import PointMovement  # noqa: F401
from app.modules.business import BusinessSettings  # noqa: F401
from app.modules.licensing.models import SystemLicense  # noqa: F401

settings.app_env = "test"


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    db = testing_session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()
