from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.cash_registers.models import CashRegisterSession
from app.modules.cash_registers.schemas import CashRegisterClose, CashRegisterOpen
from app.modules.pharmacy.service import summarize_pharmacy_cash
from app.modules.receipts.service import summarize_clinic_cash
from app.modules.users.models import StaffUser


def list_cash_sessions(
    db: Session,
    *,
    module: str | None = None,
    status: str | None = None,
    cashier_name: str | None = None,
) -> list[CashRegisterSession]:
    statement = select(CashRegisterSession).order_by(CashRegisterSession.opened_at.desc())
    if module:
        statement = statement.where(CashRegisterSession.module == module)
    if status:
        statement = statement.where(CashRegisterSession.status == status)
    if cashier_name:
        statement = statement.where(CashRegisterSession.cashier_name == cashier_name)
    return list(db.scalars(statement.limit(200)))


def get_cash_session(db: Session, session_id: str) -> CashRegisterSession | None:
    return db.get(CashRegisterSession, session_id)


def open_cash_session(
    db: Session,
    payload: CashRegisterOpen,
    actor: StaffUser | None = None,
) -> CashRegisterSession:
    existing = db.scalar(
        select(CashRegisterSession).where(
            CashRegisterSession.module == payload.module,
            CashRegisterSession.cashier_name == payload.cashier_name,
            CashRegisterSession.status == "open",
        )
    )
    if existing is not None:
        raise ValueError("Ya existe una caja abierta para ese modulo y cajero.")

    session = CashRegisterSession(
        module=payload.module,
        cashier_name=payload.cashier_name,
        opening_amount=round(payload.opening_amount, 2),
        opened_by_user_id=actor.id if actor else None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def close_cash_session(
    db: Session,
    cash_session: CashRegisterSession,
    payload: CashRegisterClose,
    actor: StaffUser | None = None,
) -> CashRegisterSession:
    if cash_session.status == "closed":
        raise ValueError("La caja ya esta cerrada.")

    summary_date = cash_session.opened_at.date()
    expected_cash, expected_card, expected_transfer = _expected_payment_totals(
        db,
        module=cash_session.module,
        summary_date=summary_date,
        cashier_name=cash_session.cashier_name,
    )
    expected_cash = round(cash_session.opening_amount + expected_cash, 2)
    expected_total = round(expected_cash + expected_card + expected_transfer, 2)
    counted_total = round(
        payload.counted_cash + payload.counted_card + payload.counted_transfer, 2
    )
    difference = round(counted_total - expected_total, 2)
    if difference != 0 and not payload.notes.strip():
        raise ValueError("Agrega una nota para explicar la diferencia de caja.")

    cash_session.status = "closed"
    cash_session.closed_at = datetime.now(UTC)
    cash_session.expected_cash = expected_cash
    cash_session.expected_card = round(expected_card, 2)
    cash_session.expected_transfer = round(expected_transfer, 2)
    cash_session.expected_total = expected_total
    cash_session.counted_cash = round(payload.counted_cash, 2)
    cash_session.counted_card = round(payload.counted_card, 2)
    cash_session.counted_transfer = round(payload.counted_transfer, 2)
    cash_session.counted_total = counted_total
    cash_session.difference = difference
    cash_session.notes = payload.notes
    cash_session.closed_by_user_id = actor.id if actor else None
    db.add(cash_session)
    db.commit()
    db.refresh(cash_session)
    return cash_session


def _expected_payment_totals(
    db: Session,
    *,
    module: str,
    summary_date: date,
    cashier_name: str,
) -> tuple[float, float, float]:
    if module == "pharmacy":
        summary = summarize_pharmacy_cash(
            db, summary_date=summary_date, cashier_name=cashier_name
        )
    else:
        summary = summarize_clinic_cash(
            db, summary_date=summary_date, cashier_name=cashier_name
        )
    payments = summary.by_payment_method
    return payments.cash, payments.card, payments.transfer
