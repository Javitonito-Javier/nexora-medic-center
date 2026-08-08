from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class AttachmentCategory(StrEnum):
    identity = "identity"
    prescription = "prescription"
    lab_result = "lab_result"
    discount_evidence = "discount_evidence"
    consent = "consent"
    other = "other"


class PatientAttachmentRead(BaseModel):
    id: str
    patient_id: str
    category: str
    original_filename: str
    content_type: str
    size_bytes: int
    description: str
    uploaded_by_user_id: str | None
    uploaded_by_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
