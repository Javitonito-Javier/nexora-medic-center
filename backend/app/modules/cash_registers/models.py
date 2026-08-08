from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CashRegisterSession(Base):
    __tablename__ = "cash_register_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    module: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    cashier_name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="open", index=True)
    opening_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    expected_cash: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    expected_card: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    expected_transfer: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    expected_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    counted_cash: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    counted_card: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    counted_transfer: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    counted_total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    difference: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    opened_by_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    closed_by_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
