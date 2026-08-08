from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.consultations.models import Consultation
from app.modules.consultations.schemas import ConsultationCreate


def list_consultations(db: Session, patient_id: str | None = None) -> list[Consultation]:
    statement = select(Consultation).order_by(Consultation.date.desc())
    if patient_id:
        statement = statement.where(Consultation.patient_id == patient_id)
    return list(db.scalars(statement))


def create_consultation(db: Session, payload: ConsultationCreate) -> Consultation:
    consultation = Consultation(
        patient_id=payload.patient_id,
        doctor_name=payload.doctor_name,
        doctor_specialty=payload.doctor_specialty or "Medicina general",
        nurse_name=payload.nurse_name,
        referred_by_doctor=payload.referred_by_doctor,
        referred_to_specialty=payload.referred_to_specialty,
        referral_reason=payload.referral_reason,
        blood_pressure=payload.blood_pressure,
        heart_rate=payload.heart_rate,
        oxygen_saturation=payload.oxygen_saturation,
        weight=payload.weight,
        temperature=payload.temperature,
        next_appointment_date=payload.next_appointment_date,
        clinical_history=payload.clinical_history,
        diagnosis=payload.diagnosis or "Pendiente de diagnostico",
        treatment=payload.treatment or "Pendiente de tratamiento",
        follow_up_notes=payload.follow_up_notes,
        internal_notes=payload.internal_notes,
        has_prescription=payload.has_prescription,
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation
