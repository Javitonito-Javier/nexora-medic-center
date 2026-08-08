from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.consultations.schemas import ConsultationCreate, ConsultationRead
from app.modules.consultations.service import create_consultation, list_consultations
from app.modules.patients.service import get_patient
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/", response_model=list[ConsultationRead])
def read_consultations(
    patient_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ConsultationRead]:
    return list_consultations(db, patient_id=patient_id)


@router.post("/", response_model=ConsultationRead, status_code=status.HTTP_201_CREATED)
def create_consultation_endpoint(
    payload: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> ConsultationRead:
    if get_patient(db, payload.patient_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
    consultation = create_consultation(db, payload)
    record_audit_event(
        db,
        module="consultations",
        action="create",
        entity_type="consultation",
        entity_id=consultation.id,
        summary=f"Consulta creada para paciente {consultation.patient_id}.",
        actor=current_user,
        after_data=payload.model_dump(),
    )
    return consultation
