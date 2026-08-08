from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsultationBase(BaseModel):
    doctor_name: str = Field(min_length=2, max_length=180)
    doctor_specialty: str = Field(default="Medicina general", max_length=140)
    nurse_name: str = ""
    referred_by_doctor: str = Field(default="", max_length=180)
    referred_to_specialty: str = Field(default="", max_length=140)
    referral_reason: str = ""
    blood_pressure: str = ""
    heart_rate: str = ""
    oxygen_saturation: str = ""
    weight: str = ""
    temperature: str = ""
    next_appointment_date: date | None = None
    clinical_history: str = Field(min_length=2)
    diagnosis: str = "Pendiente de diagnostico"
    treatment: str = "Pendiente de tratamiento"
    follow_up_notes: str = ""
    internal_notes: str = ""
    has_prescription: bool = False


class ConsultationCreate(ConsultationBase):
    patient_id: str


class ConsultationRead(ConsultationBase):
    id: str
    patient_id: str
    date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
