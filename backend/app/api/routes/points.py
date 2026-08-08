from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.points.schemas import PatientPointsRead, PointMovementRead
from app.modules.points.service import list_movements, list_patient_points

router = APIRouter()


@router.get("/", response_model=list[PatientPointsRead])
def read_patient_points(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PatientPointsRead]:
    return list_patient_points(db, search=search)


@router.get("/movements", response_model=list[PointMovementRead])
def read_point_movements(
    patient_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PointMovementRead]:
    return list_movements(db, patient_id=patient_id)
