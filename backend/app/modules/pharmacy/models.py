from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class PharmacySale(Base):
    __tablename__ = "pharmacy_sales"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    patient_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("patients.id"), nullable=True, index=True
    )
    customer_name: Mapped[str] = mapped_column(
        String(180), nullable=False, default="Consumidor final"
    )
    cashier_name: Mapped[str] = mapped_column(String(180), nullable=False, default="")
    document_type: Mapped[str] = mapped_column(String(40), nullable=False, default="receipt")
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False, default="cash")
    payment_reference: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    bank_name: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    subtotal: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    discount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    discount_type: Mapped[str] = mapped_column(String(40), nullable=False, default="none")
    discount_base_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    discount_evidence_note: Mapped[str] = mapped_column(String(260), nullable=False, default="")
    total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )


class PharmacySaleItem(Base):
    __tablename__ = "pharmacy_sale_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    sale_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("pharmacy_sales.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.id"), nullable=False, index=True
    )
    product_name: Mapped[str] = mapped_column(String(220), nullable=False)
    presentation: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    units_deducted: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    line_total: Mapped[float] = mapped_column(Float, nullable=False)
    label_unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    label_line_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    cost_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    profit_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)


class PharmacySaleLotAllocation(Base):
    __tablename__ = "pharmacy_sale_lot_allocations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    sale_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("pharmacy_sales.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sale_item_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("pharmacy_sale_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.id"), nullable=False, index=True
    )
    lot_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("inventory_lots.id"), nullable=False, index=True
    )
    lot_number: Mapped[str] = mapped_column(String(120), nullable=False)
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    sale_unit_value: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    cost_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    revenue_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    profit_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
