from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SystemLicense(Base):
    __tablename__ = "system_licenses"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default="main")
    customer_name: Mapped[str] = mapped_column(String(180), nullable=False, default="")
    installation_id: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    license_key: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="missing")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
