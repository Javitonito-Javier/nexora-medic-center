from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PointMovementRead(BaseModel):
    id: str
    patient_id: str
    sale_id: str
    movement_type: str
    points: float
    balance_after: float
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientPointsRead(BaseModel):
    patient_id: str
    full_name: str
    identity_number: str
    phone: str
    available_points: float
