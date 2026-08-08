from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class PatientSex(StrEnum):
    female = "female"
    male = "male"
    other = "other"


class PatientBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=180)
    phone: str = Field(min_length=4, max_length=40)
    identity_number: str = Field(min_length=4, max_length=80)
    birth_date: date
    sex: PatientSex
    address: str = ""
    allergies: str = "Ninguna registrada"
    known_conditions: str = "Sin condiciones registradas"


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=180)
    phone: str | None = Field(default=None, min_length=4, max_length=40)
    identity_number: str | None = Field(default=None, min_length=4, max_length=80)
    birth_date: date | None = None
    sex: PatientSex | None = None
    address: str | None = None
    allergies: str | None = None
    known_conditions: str | None = None


class PatientRead(PatientBase):
    id: str
    available_points: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
