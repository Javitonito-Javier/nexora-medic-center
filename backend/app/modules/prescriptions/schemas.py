from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PrescriptionItemCreate(BaseModel):
    medication_name: str = Field(min_length=2, max_length=220)
    dose: str = ""
    administration_route: str = ""
    frequency: str = ""
    duration: str = ""
    instructions: str = ""


class PrescriptionCreate(BaseModel):
    patient_id: str
    consultation_id: str | None = None
    doctor_name: str = Field(min_length=2, max_length=180)
    doctor_specialty: str = Field(default="Medicina general", max_length=140)
    general_notes: str = ""
    items: list[PrescriptionItemCreate] = Field(min_length=1)


class PrescriptionItemRead(PrescriptionItemCreate):
    id: str

    model_config = ConfigDict(from_attributes=True)


class PrescriptionRead(BaseModel):
    id: str
    patient_id: str
    consultation_id: str | None
    doctor_name: str
    doctor_specialty: str = "Medicina general"
    general_notes: str
    created_at: datetime
    items: list[PrescriptionItemRead]

    model_config = ConfigDict(from_attributes=True)
