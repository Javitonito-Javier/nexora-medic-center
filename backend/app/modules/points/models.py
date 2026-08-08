from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class PointMovement(Base):
    __tablename__ = "point_movements"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    patient_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sale_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("pharmacy_sales.id"), nullable=False, default="", index=True
    )
    movement_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    points: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    balance_after: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    note: Mapped[str] = mapped_column(String(260), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )
