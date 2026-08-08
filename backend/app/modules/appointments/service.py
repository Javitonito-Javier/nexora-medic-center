from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.appointments.models import Appointment
from app.modules.appointments.schemas import AppointmentCreate, AppointmentUpdate


def list_appointments(
    db: Session,
    patient_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[Appointment]:
    statement = select(Appointment).order_by(Appointment.scheduled_at.asc())
    if patient_id:
        statement = statement.where(Appointment.patient_id == patient_id)
    if date_from:
        statement = statement.where(Appointment.scheduled_at >= date_from)
    if date_to:
        statement = statement.where(Appointment.scheduled_at <= date_to)
    return list(db.scalars(statement))


def create_appointment(db: Session, payload: AppointmentCreate) -> Appointment:
    appointment = Appointment(
        patient_id=payload.patient_id,
        scheduled_at=payload.scheduled_at,
        reason=payload.reason,
        doctor_name=payload.doctor_name,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def get_appointment(db: Session, appointment_id: str) -> Appointment | None:
    return db.get(Appointment, appointment_id)


def update_appointment(
    db: Session, appointment: Appointment, payload: AppointmentUpdate
) -> Appointment:
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(appointment, field, value)
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
