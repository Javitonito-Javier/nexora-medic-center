from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.patients.models import Patient
from app.modules.points.models import PointMovement
from app.modules.points.schemas import PatientPointsRead

POINTS_STEP_AMOUNT = 25
POINTS_VALUE_PER_STEP = 0.05
MIN_REDEMPTION_POINTS = 50


def calculate_earned_points(total: float) -> float:
    if total <= 0:
        return 0
    steps = int(total // POINTS_STEP_AMOUNT)
    return round(steps * POINTS_VALUE_PER_STEP, 2)


def list_patient_points(db: Session, search: str | None = None) -> list[PatientPointsRead]:
    statement = select(Patient).order_by(Patient.full_name.asc())
    if search:
        pattern = f"%{search.lower()}%"
        statement = statement.where(
            Patient.full_name.ilike(pattern)
            | Patient.identity_number.ilike(pattern)
            | Patient.phone.ilike(pattern)
        )
    patients = list(db.scalars(statement))
    return [
        PatientPointsRead(
            patient_id=patient.id,
            full_name=patient.full_name,
            identity_number=patient.identity_number,
            phone=patient.phone,
            available_points=round(patient.available_points, 2),
        )
        for patient in patients
    ]


def list_movements(db: Session, patient_id: str | None = None) -> list[PointMovement]:
    statement = select(PointMovement).order_by(PointMovement.created_at.desc())
    if patient_id:
        statement = statement.where(PointMovement.patient_id == patient_id)
    return list(db.scalars(statement.limit(200)))


def redeem_points(db: Session, patient: Patient, sale_id: str, amount: float) -> float:
    amount = round(max(amount, 0), 2)
    if amount <= 0:
        return 0
    if patient.available_points < MIN_REDEMPTION_POINTS:
        raise ValueError("El cliente necesita al menos L 50.00 en puntos para redimir.")
    if amount > patient.available_points:
        raise ValueError("El descuento por puntos supera el saldo disponible.")

    patient.available_points = round(patient.available_points - amount, 2)
    db.add(patient)
    db.add(
        PointMovement(
            patient_id=patient.id,
            sale_id=sale_id,
            movement_type="redeem",
            points=-amount,
            balance_after=patient.available_points,
            note="Redencion de puntos en Farmacia POS.",
        )
    )
    return amount


def earn_points(db: Session, patient: Patient, sale_id: str, sale_total: float) -> float:
    earned = calculate_earned_points(sale_total)
    if earned <= 0:
        return 0

    patient.available_points = round(patient.available_points + earned, 2)
    db.add(patient)
    db.add(
        PointMovement(
            patient_id=patient.id,
            sale_id=sale_id,
            movement_type="earn",
            points=earned,
            balance_after=patient.available_points,
            note=f"Puntos por compra de farmacia: L {sale_total:.2f}.",
        )
    )
    return earned
