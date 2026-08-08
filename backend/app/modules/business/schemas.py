from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class BusinessSettingsUpdate(BaseModel):
    trade_name: str = Field(default="Clinicapharma", max_length=180)
    legal_name: str = Field(default="", max_length=220)
    rtn: str = Field(default="", max_length=40)
    address: str = ""
    phone: str = Field(default="", max_length=80)
    email: str = Field(default="", max_length=160)
    logo_url: str = ""
    logo_data_url: str = ""
    invoice_enabled: bool = False
    fiscal_enabled: bool = False
    fiscal_regime: str = Field(default="", max_length=160)
    cai: str = Field(default="", max_length=120)
    invoice_range_start: str = Field(default="", max_length=60)
    invoice_range_end: str = Field(default="", max_length=60)
    current_invoice_number: str = Field(default="", max_length=60)
    establishment_code: str = Field(default="", max_length=20)
    emission_point_code: str = Field(default="", max_length=20)
    invoice_limit_date: date | None = None
    receipt_footer: str = "Gracias por su visita"
    invoice_footer: str = ""
    age_discount_note: str = ""
    thermal_paper_width: str = Field(default="80mm", max_length=20)


class BusinessSettingsRead(BusinessSettingsUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    updated_at: datetime
