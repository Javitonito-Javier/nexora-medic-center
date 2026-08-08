from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ClinicReceipt(Base):
    __tablename__ = "clinic_receipts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    patient_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("patients.id"), nullable=False, index=True
    )
    consultation_id: Mapped[str | None] = mapped_column(
        String(64), ForeignKey("consultations.id"), nullable=True, index=True
    )
    patient_name: Mapped[str] = mapped_column(String(180), nullable=False)
    cashier_name: Mapped[str] = mapped_column(String(180), nullable=False, default="")
    doctor_name: Mapped[str] = mapped_column(String(180), nullable=False, default="")
    document_type: Mapped[str] = mapped_column(String(40), nullable=False, default="receipt")
    payment_method: Mapped[str] = mapped_column(String(40), nullable=False, default="cash")
    payment_reference: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    bank_name: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="Consulta medica")
    subtotal: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    discount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    total: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )
