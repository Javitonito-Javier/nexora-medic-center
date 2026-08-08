from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.receipts.schemas import (
    ClinicReceiptCreate,
    ClinicReceiptRead,
    ReceiptText,
)
from app.modules.receipts.service import (
    build_clinic_receipt_text,
    create_clinic_receipt,
    list_clinic_receipts,
)
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/clinic", response_model=list[ClinicReceiptRead])
def read_clinic_receipts(
    patient_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ClinicReceiptRead]:
    return list_clinic_receipts(db, patient_id=patient_id)


@router.post("/clinic", response_model=ClinicReceiptRead, status_code=status.HTTP_201_CREATED)
def create_clinic_receipt_endpoint(
    payload: ClinicReceiptCreate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> ClinicReceiptRead:
    try:
        receipt = create_clinic_receipt(db, payload)
        record_audit_event(
            db,
            module="receipts",
            action="create_clinic_receipt",
            entity_type="clinic_receipt",
            entity_id=receipt.id,
            summary=f"Recibo clinico creado por L {receipt.total:.2f}.",
            actor=current_user,
            after_data=payload.model_dump(),
        )
        return receipt
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/clinic/{receipt_id}/text", response_model=ReceiptText)
def read_clinic_receipt_text(receipt_id: str, db: Session = Depends(get_db)) -> ReceiptText:
    receipt = build_clinic_receipt_text(db, receipt_id)
    if receipt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recibo no encontrado.")
    return receipt
