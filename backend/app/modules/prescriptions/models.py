from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    patient_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consultation_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("consultations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    doctor_name: Mapped[str] = mapped_column(String(180), nullable=False)
    doctor_specialty: Mapped[str] = mapped_column(
        String(140), nullable=False, default="Medicina general"
    )
    general_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    items: Mapped[list["PrescriptionItem"]] = relationship(
        back_populates="prescription",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    prescription_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("prescriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    medication_name: Mapped[str] = mapped_column(String(220), nullable=False)
    dose: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    administration_route: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    frequency: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    duration: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    prescription: Mapped[Prescription] = relationship(back_populates="items")
