from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.patients.service import get_patient
from app.modules.prescriptions.schemas import PrescriptionCreate, PrescriptionRead
from app.modules.prescriptions.service import create_prescription, list_prescriptions
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/", response_model=list[PrescriptionRead])
def read_prescriptions(
    patient_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PrescriptionRead]:
    return list_prescriptions(db, patient_id=patient_id)


@router.post("/", response_model=PrescriptionRead, status_code=status.HTTP_201_CREATED)
def create_prescription_endpoint(
    payload: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> PrescriptionRead:
    if get_patient(db, payload.patient_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
    try:
        prescription = create_prescription(db, payload)
        record_audit_event(
            db,
            module="prescriptions",
            action="create",
            entity_type="prescription",
            entity_id=prescription.id,
            summary=f"Receta creada para paciente {prescription.patient_id}.",
            actor=current_user,
            after_data=payload.model_dump(),
        )
        return prescription
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
