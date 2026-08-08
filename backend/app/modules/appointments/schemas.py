from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AppointmentStatus = Literal["scheduled", "confirmed", "checked_in", "completed", "cancelled"]


class AppointmentBase(BaseModel):
    scheduled_at: datetime
    reason: str = Field(default="", max_length=500)
    doctor_name: str = Field(default="", max_length=180)
    status: AppointmentStatus = "scheduled"
    notes: str = ""


class AppointmentCreate(AppointmentBase):
    patient_id: str


class AppointmentUpdate(BaseModel):
    scheduled_at: datetime | None = None
    reason: str | None = Field(default=None, max_length=500)
    doctor_name: str | None = Field(default=None, max_length=180)
    status: AppointmentStatus | None = None
    notes: str | None = None


class AppointmentRead(AppointmentBase):
    id: str
    patient_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
