from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.modules.business.models import BusinessSettings
from app.modules.business.schemas import BusinessSettingsUpdate

SETTINGS_ID = "main"


def get_business_settings(db: Session) -> BusinessSettings:
    settings = db.get(BusinessSettings, SETTINGS_ID)
    if settings is not None:
        return settings

    settings = BusinessSettings(id=SETTINGS_ID)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def update_business_settings(db: Session, payload: BusinessSettingsUpdate) -> BusinessSettings:
    settings = get_business_settings(db)
    for field, value in payload.model_dump().items():
        setattr(settings, field, value)
    settings.updated_at = datetime.now(UTC)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


def ensure_invoice_allowed(db: Session, *, document_type: str) -> None:
    if document_type != "invoice":
        return
    settings = get_business_settings(db)
    if not settings.invoice_enabled:
        raise ValueError(
            "La emision de facturas no esta autorizada en configuracion. Use recibo o active facturas como administrador."
        )


def business_header_lines(db: Session) -> list[str]:
    settings = get_business_settings(db)
    lines = [settings.trade_name or "Clinicapharma"]
    if settings.legal_name:
        lines.append(settings.legal_name)
    if settings.rtn:
        lines.append(f"RTN: {settings.rtn}")
    if settings.address:
        lines.append(settings.address)
    if settings.phone:
        lines.append(f"Tel: {settings.phone}")
    if settings.email:
        lines.append(settings.email)
    return lines


def fiscal_lines(db: Session, *, document_type: str) -> list[str]:
    settings = get_business_settings(db)
    if not settings.fiscal_enabled or document_type != "invoice":
        return []

    lines = []
    if settings.fiscal_regime:
        lines.append(f"Regimen: {settings.fiscal_regime}")
    if settings.cai:
        lines.append(f"CAI: {settings.cai}")
    if settings.invoice_range_start or settings.invoice_range_end:
        lines.append(f"Rango: {settings.invoice_range_start} al {settings.invoice_range_end}")
    if settings.current_invoice_number:
        lines.append(f"Correlativo: {settings.current_invoice_number}")
    if settings.establishment_code or settings.emission_point_code:
        lines.append(
            f"Est/Pto: {settings.establishment_code or 'N/A'}-{settings.emission_point_code or 'N/A'}"
        )
    if settings.invoice_limit_date:
        lines.append(f"Fecha limite emision: {settings.invoice_limit_date.strftime('%d/%m/%Y')}")
    if settings.invoice_footer:
        lines.append(settings.invoice_footer)
    return lines


def footer_line(db: Session, *, document_type: str) -> str:
    settings = get_business_settings(db)
    if document_type == "invoice" and settings.invoice_footer:
        return settings.invoice_footer
    return settings.receipt_footer or "Gracias por su visita"
