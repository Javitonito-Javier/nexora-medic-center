from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.core.config import settings
from app.db.session import Base

# Import all models so they register with Base.metadata
from app.modules.appointments import Appointment  # noqa: F401
from app.modules.attachments import PatientAttachment  # noqa: F401
from app.modules.audit import AuditEvent  # noqa: F401
from app.modules.business import BusinessSettings  # noqa: F401
from app.modules.cash_registers import CashRegisterSession  # noqa: F401
from app.modules.consultations import Consultation  # noqa: F401
from app.modules.inventory import InventoryLot, InventoryLotPrice, InventoryMovement, Product, ProductPresentation  # noqa: F401
from app.modules.licensing.models import SystemLicense  # noqa: F401
from app.modules.patients import Patient  # noqa: F401
from app.modules.pharmacy import PharmacySale, PharmacySaleItem, PharmacySaleLotAllocation  # noqa: F401
from app.modules.points import PointMovement  # noqa: F401
from app.modules.prescriptions import Prescription, PrescriptionItem  # noqa: F401
from app.modules.receipts import ClinicReceipt  # noqa: F401
from app.modules.users import StaffUser  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.database_url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
