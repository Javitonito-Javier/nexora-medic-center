from datetime import UTC, datetime

from sqlalchemy import Boolean, Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class BusinessSettings(Base):
    __tablename__ = "business_settings"

    id: Mapped[str] = mapped_column(String(40), primary_key=True, default="main")
    trade_name: Mapped[str] = mapped_column(String(180), nullable=False, default="Clinicapharma")
    legal_name: Mapped[str] = mapped_column(String(220), nullable=False, default="")
    rtn: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    address: Mapped[str] = mapped_column(Text, nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    logo_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    logo_data_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    invoice_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fiscal_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fiscal_regime: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    cai: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    invoice_range_start: Mapped[str] = mapped_column(String(60), nullable=False, default="")
    invoice_range_end: Mapped[str] = mapped_column(String(60), nullable=False, default="")
    current_invoice_number: Mapped[str] = mapped_column(String(60), nullable=False, default="")
    establishment_code: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    emission_point_code: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    invoice_limit_date = mapped_column(Date, nullable=True)
    receipt_footer: Mapped[str] = mapped_column(
        Text, nullable=False, default="Gracias por su visita"
    )
    invoice_footer: Mapped[str] = mapped_column(Text, nullable=False, default="")
    age_discount_note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    thermal_paper_width: Mapped[str] = mapped_column(String(20), nullable=False, default="80mm")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
