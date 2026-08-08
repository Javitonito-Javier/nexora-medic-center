import logging

from sqlalchemy import inspect, select, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.db.session import Base, SessionLocal, engine

# Import models so SQLAlchemy registers their metadata before create_all.
from app.modules.appointments import Appointment  # noqa: F401
from app.modules.attachments import PatientAttachment  # noqa: F401
from app.modules.audit import AuditEvent  # noqa: F401
from app.modules.auth.security import hash_password
from app.modules.business import BusinessSettings  # noqa: F401
from app.modules.cash_registers import CashRegisterSession  # noqa: F401
from app.modules.consultations import Consultation  # noqa: F401
from app.modules.inventory import (
    InventoryLot,  # noqa: F401
    InventoryLotPrice,  # noqa: F401
    InventoryMovement,  # noqa: F401
    Product,  # noqa: F401
    ProductPresentation,  # noqa: F401
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

logger = logging.getLogger(__name__)


def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        _ensure_staff_user_auth_columns()
        _ensure_inventory_product_columns()
        _ensure_business_settings_columns()
        _ensure_consultation_columns()
        _ensure_pharmacy_sale_columns()
        _ensure_clinic_receipt_columns()
        _ensure_prescription_item_columns()
        _ensure_prescription_columns()
        _seed_default_admin()
    except SQLAlchemyError:
        logger.exception("Could not initialize database tables.")


def _ensure_staff_user_auth_columns() -> None:
    inspector = inspect(engine)
    if "staff_users" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("staff_users")}
    statements = []
    if "username" not in columns:
        statements.append("ALTER TABLE staff_users ADD COLUMN username VARCHAR(80)")
    if "password_hash" not in columns:
        statements.append(
            "ALTER TABLE staff_users ADD COLUMN password_hash TEXT DEFAULT '' NOT NULL"
        )
    if "module_permissions" not in columns:
        statements.append(
            "ALTER TABLE staff_users ADD COLUMN module_permissions JSON DEFAULT '[]' NOT NULL"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _ensure_inventory_product_columns() -> None:
    inspector = inspect(engine)
    if "products" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("products")}
    statements = []
    if "base_unit_name" not in columns:
        statements.append(
            "ALTER TABLE products ADD COLUMN base_unit_name VARCHAR(60) DEFAULT 'unidad' NOT NULL"
        )
    if "barcode" not in columns:
        statements.append(
            "ALTER TABLE products ADD COLUMN barcode VARCHAR(120) DEFAULT '' NOT NULL"
        )
    if "laboratory_name" not in columns:
        statements.append(
            "ALTER TABLE products ADD COLUMN laboratory_name VARCHAR(160) DEFAULT '' NOT NULL"
        )
    if "supplier_name" not in columns:
        statements.append(
            "ALTER TABLE products ADD COLUMN supplier_name VARCHAR(160) DEFAULT '' NOT NULL"
        )

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))

    lot_statements = []
    if "inventory_lots" in inspector.get_table_names():
        lot_columns = {column["name"] for column in inspector.get_columns("inventory_lots")}
        if "lot_barcode" not in lot_columns:
            lot_statements.append(
                "ALTER TABLE inventory_lots ADD COLUMN lot_barcode VARCHAR(120) DEFAULT '' NOT NULL"
            )
        if "shelf_location" not in lot_columns:
            lot_statements.append(
                "ALTER TABLE inventory_lots ADD COLUMN shelf_location VARCHAR(120) DEFAULT '' NOT NULL"
            )

    if lot_statements:
        with engine.begin() as connection:
            for statement in lot_statements:
                connection.execute(text(statement))

    presentation_statements = []
    if "product_presentations" in inspector.get_table_names():
        presentation_columns = {
            column["name"] for column in inspector.get_columns("product_presentations")
        }
        if "label_price" not in presentation_columns:
            presentation_statements.append(
                "ALTER TABLE product_presentations ADD COLUMN label_price FLOAT DEFAULT 0 NOT NULL"
            )

    if presentation_statements:
        with engine.begin() as connection:
            for statement in presentation_statements:
                connection.execute(text(statement))

    lot_price_statements = []
    if "inventory_lot_prices" in inspector.get_table_names():
        lot_price_columns = {
            column["name"] for column in inspector.get_columns("inventory_lot_prices")
        }
        if "label_price" not in lot_price_columns:
            lot_price_statements.append(
                "ALTER TABLE inventory_lot_prices ADD COLUMN label_price FLOAT DEFAULT 0 NOT NULL"
            )

    if lot_price_statements:
        with engine.begin() as connection:
            for statement in lot_price_statements:
                connection.execute(text(statement))


def _ensure_business_settings_columns() -> None:
    inspector = inspect(engine)
    if "business_settings" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("business_settings")}
    statements = []
    if "invoice_enabled" not in columns:
        statements.append(
            "ALTER TABLE business_settings ADD COLUMN invoice_enabled BOOLEAN DEFAULT FALSE NOT NULL"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def _ensure_pharmacy_sale_columns() -> None:
    inspector = inspect(engine)
    if "pharmacy_sales" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("pharmacy_sales")}
    statements = []
    if "cashier_name" not in columns:
        statements.append(
            "ALTER TABLE pharmacy_sales ADD COLUMN cashier_name VARCHAR(180) DEFAULT '' NOT NULL"
        )
    if "document_type" not in columns:
        statements.append(
            "ALTER TABLE pharmacy_sales ADD COLUMN document_type VARCHAR(40) DEFAULT 'receipt' NOT NULL"
        )
    if "payment_reference" not in columns:
        statements.append(
            "ALTER TABLE pharmacy_sales ADD COLUMN payment_reference VARCHAR(160) DEFAULT '' NOT NULL"
        )
    if "bank_name" not in columns:
        statements.append(
            "ALTER TABLE pharmacy_sales ADD COLUMN bank_name VARCHAR(120) DEFAULT '' NOT NULL"
        )
    if "status" not in columns:
        statements.append(
            "ALTER TABLE pharmacy_sales ADD COLUMN status VARCHAR(40) DEFAULT 'active' NOT NULL"
        )
    if "patient_id" not in columns:
        statements.append("ALTER TABLE pharmacy_sales ADD COLUMN patient_id VARCHAR(64)")
    if "discount_type" not in columns:
        statements.append(
            "ALTER TABLE pharmacy_sales ADD COLUMN discount_type VARCHAR(40) DEFAULT 'none' NOT NULL"
        )
    if "discount_base_total" not in columns:
        statements.append(
            "ALTER TABLE pharmacy_sales ADD COLUMN discount_base_total FLOAT DEFAULT 0 NOT NULL"
        )
    if "discount_evidence_note" not in columns:
        statements.append(
            "ALTER TABLE pharmacy_sales ADD COLUMN discount_evidence_note VARCHAR(260) DEFAULT '' NOT NULL"
        )

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))

    item_statements = []
    if "pharmacy_sale_items" in inspector.get_table_names():
        item_columns = {column["name"] for column in inspector.get_columns("pharmacy_sale_items")}
        if "cost_total" not in item_columns:
            item_statements.append(
                "ALTER TABLE pharmacy_sale_items ADD COLUMN cost_total FLOAT DEFAULT 0 NOT NULL"
            )
        if "profit_total" not in item_columns:
            item_statements.append(
                "ALTER TABLE pharmacy_sale_items ADD COLUMN profit_total FLOAT DEFAULT 0 NOT NULL"
            )
        if "label_unit_price" not in item_columns:
            item_statements.append(
                "ALTER TABLE pharmacy_sale_items ADD COLUMN label_unit_price FLOAT DEFAULT 0 NOT NULL"
            )
        if "label_line_total" not in item_columns:
            item_statements.append(
                "ALTER TABLE pharmacy_sale_items ADD COLUMN label_line_total FLOAT DEFAULT 0 NOT NULL"
            )

    if item_statements:
        with engine.begin() as connection:
            for statement in item_statements:
                connection.execute(text(statement))


def _ensure_clinic_receipt_columns() -> None:
    inspector = inspect(engine)
    if "clinic_receipts" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("clinic_receipts")}
    statements = []
    if "payment_reference" not in columns:
        statements.append(
            "ALTER TABLE clinic_receipts ADD COLUMN payment_reference VARCHAR(160) DEFAULT '' NOT NULL"
        )
    if "bank_name" not in columns:
        statements.append(
            "ALTER TABLE clinic_receipts ADD COLUMN bank_name VARCHAR(120) DEFAULT '' NOT NULL"
        )

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))


def _ensure_consultation_columns() -> None:
    inspector = inspect(engine)
    if "consultations" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("consultations")}
    statements = []
    if "doctor_specialty" not in columns:
        statements.append(
            "ALTER TABLE consultations "
            "ADD COLUMN doctor_specialty VARCHAR(140) DEFAULT 'Medicina general' NOT NULL"
        )
    if "referred_by_doctor" not in columns:
        statements.append(
            "ALTER TABLE consultations "
            "ADD COLUMN referred_by_doctor VARCHAR(180) DEFAULT '' NOT NULL"
        )
    if "referred_to_specialty" not in columns:
        statements.append(
            "ALTER TABLE consultations "
            "ADD COLUMN referred_to_specialty VARCHAR(140) DEFAULT '' NOT NULL"
        )
    if "referral_reason" not in columns:
        statements.append(
            "ALTER TABLE consultations ADD COLUMN referral_reason TEXT DEFAULT '' NOT NULL"
        )
    if "follow_up_notes" not in columns:
        statements.append(
            "ALTER TABLE consultations ADD COLUMN follow_up_notes TEXT DEFAULT '' NOT NULL"
        )

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))


def _ensure_prescription_columns() -> None:
    inspector = inspect(engine)
    if "prescriptions" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("prescriptions")}
    if "doctor_specialty" in columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE prescriptions "
                "ADD COLUMN doctor_specialty VARCHAR(140) DEFAULT 'Medicina general' NOT NULL"
            )
        )


def _ensure_prescription_item_columns() -> None:
    inspector = inspect(engine)
    if "prescription_items" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("prescription_items")}
    if "administration_route" in columns:
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE prescription_items "
                "ADD COLUMN administration_route VARCHAR(120) DEFAULT '' NOT NULL"
            )
        )


def _seed_default_admin() -> None:
    db = SessionLocal()
    try:
        has_staff = db.scalar(select(StaffUser.id).limit(1))
        if has_staff:
            return

        admin = StaffUser(
            username=settings.initial_admin_username,
            password_hash=hash_password(settings.initial_admin_password),
            full_name="Administrador",
            phone="",
            roles=["admin", "doctor", "receptionist", "cashier"],
            module_permissions=[
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
            ],
            area="both",
            active=True,
            on_shift=True,
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()
