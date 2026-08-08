from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import JSON, Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class StaffUser(Base):
    __tablename__ = "staff_users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: str(uuid4()))
    username: Mapped[str | None] = mapped_column(String(80), nullable=True, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False, default="")
    full_name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    roles: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    module_permissions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    area: Mapped[str] = mapped_column(String(40), nullable=False, default="clinic")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    on_shift: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
