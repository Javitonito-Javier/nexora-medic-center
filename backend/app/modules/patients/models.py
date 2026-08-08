from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    full_name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    identity_number: Mapped[str] = mapped_column(
        String(80), nullable=False, unique=True, index=True
    )
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[str] = mapped_column(String(20), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False, default="")
    allergies: Mapped[str] = mapped_column(Text, nullable=False, default="Ninguna registrada")
    known_conditions: Mapped[str] = mapped_column(
        Text, nullable=False, default="Sin condiciones registradas"
    )
    available_points: Mapped[float] = mapped_column(Float, nullable=False, default=0)
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
        # Nota: Los índices en identity_number y phone ya están definidos
        # directamente en las columnas con index=True. Este bloque documenta
        # la estrategia de indexación para búsquedas frecuentes de pacientes.
        # Para PostgreSQL, los índices explícitos aquí se crean automáticamente.
        {"info": {"description": "Estrategia de indexación optimizada para pacientes"}}
    )
