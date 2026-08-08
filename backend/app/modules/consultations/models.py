from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    patient_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    doctor_name: Mapped[str] = mapped_column(String(180), nullable=False)
    doctor_specialty: Mapped[str] = mapped_column(
        String(140), nullable=False, default="Medicina general"
    )
    nurse_name: Mapped[str] = mapped_column(String(180), nullable=False, default="")
    referred_by_doctor: Mapped[str] = mapped_column(String(180), nullable=False, default="")
    referred_to_specialty: Mapped[str] = mapped_column(String(140), nullable=False, default="")
    referral_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    blood_pressure: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    heart_rate: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    oxygen_saturation: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    weight: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    temperature: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    next_appointment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    clinical_history: Mapped[str] = mapped_column(Text, nullable=False)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=False, default="Pendiente de diagnostico")
    treatment: Mapped[str] = mapped_column(Text, nullable=False, default="Pendiente de tratamiento")
    follow_up_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    internal_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    has_prescription: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
