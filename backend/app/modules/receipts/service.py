from datetime import UTC, date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.business.service import (
    business_header_lines,
    ensure_invoice_allowed,
    fiscal_lines,
    footer_line,
)
from app.modules.patients.models import Patient
from app.modules.receipts.models import ClinicReceipt
from app.modules.receipts.schemas import (
    ClinicCashSummary,
    ClinicPaymentTotals,
    ClinicReceiptCreate,
    ReceiptText,
)


def create_clinic_receipt(db: Session, payload: ClinicReceiptCreate) -> ClinicReceipt:
    ensure_invoice_allowed(db, document_type=payload.document_type)
    patient = db.get(Patient, payload.patient_id)
    if patient is None:
        raise ValueError("Paciente no encontrado para el recibo.")

    subtotal = round(payload.subtotal, 2)
    discount = min(round(payload.discount, 2), subtotal)
    receipt = ClinicReceipt(
        patient_id=patient.id,
        consultation_id=payload.consultation_id,
        patient_name=patient.full_name,
        cashier_name=payload.cashier_name,
        doctor_name=payload.doctor_name,
        document_type=payload.document_type,
        payment_method=payload.payment_method,
        payment_reference=payload.payment_reference,
        bank_name=payload.bank_name,
        description=payload.description,
        subtotal=subtotal,
        discount=discount,
        total=round(subtotal - discount, 2),
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def list_clinic_receipts(db: Session, patient_id: str | None = None) -> list[ClinicReceipt]:
    statement = select(ClinicReceipt).order_by(ClinicReceipt.created_at.desc())
    if patient_id:
        statement = statement.where(ClinicReceipt.patient_id == patient_id)
    return list(db.scalars(statement.limit(200)))


def get_clinic_receipt(db: Session, receipt_id: str) -> ClinicReceipt | None:
    return db.get(ClinicReceipt, receipt_id)


def build_clinic_receipt_text(db: Session, receipt_id: str) -> ReceiptText | None:
    receipt = get_clinic_receipt(db, receipt_id)
    if receipt is None:
        return None
    created = receipt.created_at.strftime("%Y%m%d_%H%M")
    lines = [
        *business_header_lines(db),
        "Clinica",
        f"{'FACTURA' if receipt.document_type == 'invoice' else 'RECIBO'}: {receipt.id[:8].upper()}",
        f"Fecha: {receipt.created_at.strftime('%d/%m/%Y %H:%M')}",
        f"Cajero: {receipt.cashier_name or 'N/A'}",
        f"Doctor: {receipt.doctor_name or 'N/A'}",
        f"Paciente: {receipt.patient_name}",
        "-" * 32,
    ]
    sar_lines = fiscal_lines(db, document_type=receipt.document_type)
    if sar_lines:
        lines.extend([*sar_lines, "-" * 32])
    lines.extend(
        [
            receipt.description[:60],
            f"Subtotal: L {receipt.subtotal:.2f}",
            f"Descuento: L {receipt.discount:.2f}",
            f"Total: L {receipt.total:.2f}",
            f"Pago: {receipt.payment_method}",
            f"Banco: {receipt.bank_name or 'N/A'}",
            f"Comprobante: {receipt.payment_reference or 'N/A'}",
            "",
            footer_line(db, document_type=receipt.document_type),
        ]
    )
    safe_patient = "".join(
        char
        for char in receipt.patient_name.lower().replace(" ", "_")
        if char.isalnum() or char == "_"
    )
    return ReceiptText(
        receipt_id=receipt.id,
        filename=f"recibo_clinica_{safe_patient or 'paciente'}_{created}.txt",
        content="\n".join(lines),
    )


def summarize_clinic_cash(
    db: Session,
    summary_date: date,
    cashier_name: str | None = None,
) -> ClinicCashSummary:
    start = datetime.combine(summary_date, time.min, tzinfo=UTC)
    end = datetime.combine(summary_date, time.max, tzinfo=UTC)
    statement = select(ClinicReceipt).where(
        ClinicReceipt.created_at >= start,
        ClinicReceipt.created_at <= end,
    )
    if cashier_name:
        statement = statement.where(ClinicReceipt.cashier_name == cashier_name)

    receipts = list(db.scalars(statement))
    payment_totals = {"cash": 0.0, "card": 0.0, "transfer": 0.0}
    for receipt in receipts:
        payment_totals[receipt.payment_method] = (
            payment_totals.get(receipt.payment_method, 0.0) + receipt.total
        )

    return ClinicCashSummary(
        date=summary_date.isoformat(),
        cashier_name=cashier_name,
        receipts_count=len(receipts),
        subtotal=round(sum(receipt.subtotal for receipt in receipts), 2),
        discount=round(sum(receipt.discount for receipt in receipts), 2),
        total=round(sum(receipt.total for receipt in receipts), 2),
        by_payment_method=ClinicPaymentTotals(
            cash=round(payment_totals.get("cash", 0), 2),
            card=round(payment_totals.get("card", 0), 2),
            transfer=round(payment_totals.get("transfer", 0), 2),
        ),
    )
