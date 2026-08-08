from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.licensing.schemas import LicenseActivate, LicenseStatusRead
from app.modules.licensing.service import (
    LicenseError,
    activate_license,
    get_license_status,
)

router = APIRouter()


@router.get("/status", response_model=LicenseStatusRead)
def read_license_status(db: Session = Depends(get_db)) -> LicenseStatusRead:
    return get_license_status(db)


@router.post("/activate", response_model=LicenseStatusRead)
def activate_license_endpoint(
    payload: LicenseActivate,
    db: Session = Depends(get_db),
) -> LicenseStatusRead:
    try:
        return activate_license(db, payload.license_key)
    except LicenseError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
