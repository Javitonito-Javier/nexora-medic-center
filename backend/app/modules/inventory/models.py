from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(220), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(80), nullable=False, default="", index=True)
    barcode: Mapped[str] = mapped_column(String(120), nullable=False, default="", index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    base_unit_name: Mapped[str] = mapped_column(String(60), nullable=False, default="unidad")
    laboratory_name: Mapped[str] = mapped_column(
        String(160), nullable=False, default="", index=True
    )
    supplier_name: Mapped[str] = mapped_column(String(160), nullable=False, default="", index=True)
    units_per_blister: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    blisters_per_box: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    blister_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    box_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    min_stock_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    __table_args__ = (
        # Índices compuestos para búsquedas frecuentes
        # Búsqueda por nombre de laboratorio y proveedor
        # Útil para reportes de inventario por laboratorio/proveedor
        {"info": {"description": "Índices optimizados para búsquedas de productos"}}
    )


class ProductPresentation(Base):
    __tablename__ = "product_presentations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    product_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    units_per_sale: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    default_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    label_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class InventoryLot(Base):
    __tablename__ = "inventory_lots"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    product_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lot_number: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    lot_barcode: Mapped[str] = mapped_column(String(120), nullable=False, default="", index=True)
    shelf_location: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    purchase_unit_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    warehouse_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    store_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class InventoryLotPrice(Base):
    __tablename__ = "inventory_lot_prices"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    lot_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("inventory_lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    presentation_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("product_presentations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sale_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    label_price: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    lot_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("inventory_lots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.id"), nullable=False, index=True
    )
    movement_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    from_location: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    to_location: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    units: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(220), nullable=False, default="")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )
