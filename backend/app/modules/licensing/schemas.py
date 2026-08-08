from datetime import datetime

from pydantic import BaseModel, Field


class LicenseActivate(BaseModel):
    license_key: str = Field(min_length=40)


class LicenseStatusRead(BaseModel):
    enforcement_enabled: bool
    status: str
    customer_name: str = ""
    installation_id: str = ""
    expires_at: datetime | None = None
    days_remaining: int | None = None
    message: str
    can_write: bool
