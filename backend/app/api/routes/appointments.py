from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.appointments.schemas import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentUpdate,
)
from app.modules.appointments.service import (
    create_appointment,
    get_appointment,
    list_appointments,
    update_appointment,
)
from app.modules.audit.service import model_snapshot, record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.patients.service import get_patient
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/", response_model=list[AppointmentRead])
def read_appointments(
    patient_id: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[AppointmentRead]:
    return list_appointments(db, patient_id=patient_id, date_from=date_from, date_to=date_to)


@router.post("/", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment_endpoint(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> AppointmentRead:
    if get_patient(db, payload.patient_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
    appointment = create_appointment(db, payload)
    record_audit_event(
        db,
        module="appointments",
        action="create",
        entity_type="appointment",
        entity_id=appointment.id,
        summary=f"Cita creada para paciente {appointment.patient_id}.",
        actor=current_user,
        after_data=payload.model_dump(),
    )
    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentRead)
def update_appointment_endpoint(
    appointment_id: str,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> AppointmentRead:
    appointment = get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cita no encontrada.")
    fields = ["scheduled_at", "reason", "doctor_name", "status", "notes"]
    before = model_snapshot(appointment, fields)
    updated = update_appointment(db, appointment, payload)
    after = model_snapshot(updated, fields)
    record_audit_event(
        db,
        module="appointments",
        action="update",
        entity_type="appointment",
        entity_id=updated.id,
        summary=f"Cita actualizada para paciente {updated.patient_id}.",
        actor=current_user,
        before_data=before,
        after_data=after,
    )
    return updated
