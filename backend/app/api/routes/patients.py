from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import model_snapshot, record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.patients.schemas import PatientCreate, PatientRead, PatientUpdate
from app.modules.patients.service import (
    create_patient,
    get_patient,
    list_patients,
    update_patient,
)
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/", response_model=list[PatientRead])
def read_patients(
    search: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
) -> list[PatientRead]:
    return list_patients(db, search=search)


@router.post("/", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient_endpoint(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> PatientRead:
    try:
        patient = create_patient(db, payload)
        record_audit_event(
            db,
            module="patients",
            action="create",
            entity_type="patient",
            entity_id=patient.id,
            summary=f"Paciente creado: {patient.full_name}.",
            actor=current_user,
            after_data=payload.model_dump(),
        )
        return patient
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un paciente con esa identidad/RTN.",
        ) from exc


@router.get("/{patient_id}", response_model=PatientRead)
def read_patient(patient_id: str, db: Session = Depends(get_db)) -> PatientRead:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
    return patient


@router.patch("/{patient_id}", response_model=PatientRead)
def update_patient_endpoint(
    patient_id: str,
    payload: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> PatientRead:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")

    try:
        before = model_snapshot(
            patient,
            [
                "full_name",
                "phone",
                "identity_number",
                "birth_date",
                "sex",
                "address",
                "allergies",
                "known_conditions",
            ],
        )
        updated = update_patient(db, patient, payload)
        after = model_snapshot(updated, list(before.keys()))
        record_audit_event(
            db,
            module="patients",
            action="update",
            entity_type="patient",
            entity_id=updated.id,
            summary=f"Paciente actualizado: {updated.full_name}.",
            actor=current_user,
            before_data=before,
            after_data=after,
        )
        return updated
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un paciente con esa identidad/RTN.",
        ) from exc
