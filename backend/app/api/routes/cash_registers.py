from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import model_snapshot, record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.cash_registers.schemas import (
    CashRegisterClose,
    CashRegisterOpen,
    CashRegisterSessionRead,
)
from app.modules.cash_registers.service import (
    close_cash_session,
    get_cash_session,
    list_cash_sessions,
    open_cash_session,
)
from app.modules.pharmacy.schemas import PharmacyCashSummary
from app.modules.pharmacy.service import summarize_pharmacy_cash
from app.modules.receipts.schemas import ClinicCashSummary
from app.modules.receipts.service import summarize_clinic_cash
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/")
def list_cash_registers() -> dict[str, object]:
    return {"module": "cash registers", "items": ["clinic", "pharmacy"]}


@router.get("/sessions", response_model=list[CashRegisterSessionRead])
def read_cash_sessions(
    module: str | None = Query(default=None, pattern="^(clinic|pharmacy)$"),
    status_filter: str | None = Query(default=None, alias="status", pattern="^(open|closed)$"),
    cashier_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[CashRegisterSessionRead]:
    return list_cash_sessions(
        db,
        module=module,
        status=status_filter,
        cashier_name=cashier_name,
    )


@router.post(
    "/sessions/open",
    response_model=CashRegisterSessionRead,
    status_code=status.HTTP_201_CREATED,
)
def open_cash_register_session(
    payload: CashRegisterOpen,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> CashRegisterSessionRead:
    try:
        session = open_cash_session(db, payload, actor=current_user)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    record_audit_event(
        db,
        module="cash_registers",
        action="open",
        entity_type="cash_register_session",
        entity_id=session.id,
        summary=f"Caja {session.module} abierta por {session.cashier_name}.",
        actor=current_user,
        after_data=payload.model_dump(),
    )
    return session


@router.post("/sessions/{session_id}/close", response_model=CashRegisterSessionRead)
def close_cash_register_session(
    session_id: str,
    payload: CashRegisterClose,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> CashRegisterSessionRead:
    session = get_cash_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caja no encontrada.")
    before = model_snapshot(
        session,
        ["status", "opening_amount", "expected_total", "counted_total", "difference"],
    )
    try:
        closed = close_cash_session(db, session, payload, actor=current_user)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    after = model_snapshot(
        closed,
        [
            "status",
            "opening_amount",
            "expected_cash",
            "expected_card",
            "expected_transfer",
            "expected_total",
            "counted_cash",
            "counted_card",
            "counted_transfer",
            "counted_total",
            "difference",
        ],
    )
    record_audit_event(
        db,
        module="cash_registers",
        action="close",
        entity_type="cash_register_session",
        entity_id=closed.id,
        summary=f"Caja {closed.module} cerrada por {closed.cashier_name}.",
        actor=current_user,
        before_data=before,
        after_data=after,
        reason=payload.notes,
    )
    return closed


@router.get("/pharmacy/summary", response_model=PharmacyCashSummary)
def pharmacy_cash_summary(
    summary_date: date = Query(default_factory=date.today),
    cashier_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> PharmacyCashSummary:
    return summarize_pharmacy_cash(db, summary_date=summary_date, cashier_name=cashier_name)


@router.get("/clinic/summary", response_model=ClinicCashSummary)
def clinic_cash_summary(
    summary_date: date = Query(default_factory=date.today),
    cashier_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> ClinicCashSummary:
    return summarize_clinic_cash(db, summary_date=summary_date, cashier_name=cashier_name)
