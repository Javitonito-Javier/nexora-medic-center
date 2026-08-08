"""Current application schema

Revision ID: 20260623_current_schema
Revises: faa6b0a39848
Create Date: 2026-06-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

from app.db.session import Base

# Import all models so the migration reflects the deployable metadata.
from app.modules.appointments import Appointment  # noqa: F401
from app.modules.attachments import PatientAttachment  # noqa: F401
from app.modules.audit import AuditEvent  # noqa: F401
from app.modules.business import BusinessSettings  # noqa: F401
from app.modules.cash_registers import CashRegisterSession  # noqa: F401
from app.modules.consultations import Consultation  # noqa: F401
from app.modules.inventory import (  # noqa: F401
    InventoryLot,
    InventoryLotPrice,
    InventoryMovement,
    Product,
    ProductPresentation,
)
from app.modules.licensing.models import SystemLicense  # noqa: F401
from app.modules.patients import Patient  # noqa: F401
from app.modules.pharmacy import (  # noqa: F401
    PharmacySale,
    PharmacySaleItem,
    PharmacySaleLotAllocation,
)
from app.modules.points import PointMovement  # noqa: F401
from app.modules.prescriptions import Prescription, PrescriptionItem  # noqa: F401
from app.modules.receipts import ClinicReceipt  # noqa: F401
from app.modules.users import StaffUser  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = "20260623_current_schema"
down_revision: Union[str, Sequence[str], None] = "faa6b0a39848"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create any application tables missing from the target database."""
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    """Drop application tables for development rollback."""
    Base.metadata.drop_all(bind=op.get_bind())
