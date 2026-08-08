from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.transactions import transactional
from app.modules.consultations.models import Consultation
from app.modules.prescriptions.models import Prescription, PrescriptionItem
from app.modules.prescriptions.schemas import PrescriptionCreate


def list_prescriptions(db: Session, patient_id: str | None = None) -> list[Prescription]:
    statement = select(Prescription).order_by(Prescription.created_at.desc())
    if patient_id:
        statement = statement.where(Prescription.patient_id == patient_id)
    return list(db.scalars(statement))


@transactional
def create_prescription(db: Session, payload: PrescriptionCreate) -> Prescription:
    consultation: Consultation | None = None
    if payload.consultation_id:
        consultation = db.get(Consultation, payload.consultation_id)
        if consultation is None or consultation.patient_id != payload.patient_id:
            raise ValueError("La consulta indicada no pertenece al paciente.")

    prescription = Prescription(
        patient_id=payload.patient_id,
        consultation_id=payload.consultation_id,
        doctor_name=payload.doctor_name,
        doctor_specialty=payload.doctor_specialty or "Medicina general",
        general_notes=payload.general_notes,
    )
    db.add(prescription)
    db.flush()

    for item in payload.items:
        db.add(
            PrescriptionItem(
                prescription_id=prescription.id,
                medication_name=item.medication_name,
                dose=item.dose,
                administration_route=item.administration_route,
                frequency=item.frequency,
                duration=item.duration,
                instructions=item.instructions,
            )
        )

    if consultation is not None:
        consultation.has_prescription = True
        db.add(consultation)

    # El commit lo maneja automáticamente el decorador @transactional
    db.refresh(prescription)
    return prescription
