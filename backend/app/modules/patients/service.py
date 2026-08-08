from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.transactions import transactional
from app.modules.patients.models import Patient
from app.modules.patients.schemas import PatientCreate, PatientUpdate


def list_patients(db: Session, search: str | None = None) -> list[Patient]:
    statement = select(Patient).order_by(Patient.created_at.desc())
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            Patient.full_name.ilike(pattern)
            | Patient.phone.ilike(pattern)
            | Patient.identity_number.ilike(pattern)
        )
    return list(db.scalars(statement))


def get_patient(db: Session, patient_id: str) -> Patient:
    patient = db.get(Patient, patient_id)
    if patient is None:
        raise NotFoundError("Paciente", patient_id)
    return patient


@transactional
def create_patient(db: Session, payload: PatientCreate) -> Patient:
    # Verificar si el número de identidad ya existe
    if payload.identity_number:
        existing = db.scalar(
            select(Patient).where(Patient.identity_number == payload.identity_number)
        )
        if existing is not None:
            raise ConflictError(
                f"Ya existe un paciente con el número de identidad '{payload.identity_number}'."
            )

    patient = Patient(
        full_name=payload.full_name,
        phone=payload.phone,
        identity_number=payload.identity_number,
        birth_date=payload.birth_date,
        sex=payload.sex.value,
        address=payload.address,
        allergies=payload.allergies or "Ninguna registrada",
        known_conditions=payload.known_conditions or "Sin condiciones registradas",
    )
    db.add(patient)
    # El commit y rollback los maneja el decorador @transactional
    return patient


@transactional
def update_patient(db: Session, patient: Patient, payload: PatientUpdate) -> Patient:
    data = payload.model_dump(exclude_unset=True)
    if "sex" in data and data["sex"] is not None:
        data["sex"] = data["sex"].value

    # Verificar conflicto de identity_number si se está actualizando
    if "identity_number" in data and data["identity_number"] != patient.identity_number:
        existing = db.scalar(
            select(Patient).where(
                Patient.identity_number == data["identity_number"],
                Patient.id != patient.id
            )
        )
        if existing is not None:
            raise ConflictError(
                f"Ya existe un paciente con el número de identidad '{data['identity_number']}'."
            )

    for field, value in data.items():
        setattr(patient, field, value)

    db.add(patient)
    # El commit y rollback los maneja el decorador @transactional
    return patient
