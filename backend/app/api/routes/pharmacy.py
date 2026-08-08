from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.pharmacy.schemas import ReceiptText, SaleCreate, SaleRead
from app.modules.pharmacy.service import (
    build_receipt_text,
    create_sale,
    get_sale,
    list_sales,
)
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/sales", response_model=list[SaleRead])
def read_sales(db: Session = Depends(get_db)) -> list[SaleRead]:
    return list_sales(db)


@router.post("/sales", response_model=SaleRead, status_code=status.HTTP_201_CREATED)
def create_sale_endpoint(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> SaleRead:
    try:
        sale = create_sale(db, payload)
        record_audit_event(
            db,
            module="pharmacy",
            action="create_sale",
            entity_type="pharmacy_sale",
            entity_id=sale.id,
            summary=f"Venta farmacia creada por L {sale.total:.2f}.",
            actor=current_user,
            after_data=payload.model_dump(),
        )
        return sale
    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.get("/sales/{sale_id}", response_model=SaleRead)
def read_sale(sale_id: str, db: Session = Depends(get_db)) -> SaleRead:
    sale = get_sale(db, sale_id)
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada.")
    return sale


@router.get("/sales/{sale_id}/receipt", response_model=ReceiptText)
def read_sale_receipt(sale_id: str, db: Session = Depends(get_db)) -> ReceiptText:
    receipt = build_receipt_text(db, sale_id)
    if receipt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada.")
    return receipt
