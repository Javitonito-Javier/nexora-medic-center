from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import model_snapshot, record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.business.schemas import BusinessSettingsRead, BusinessSettingsUpdate
from app.modules.business.service import get_business_settings, update_business_settings
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/settings", response_model=BusinessSettingsRead)
def read_business_settings(db: Session = Depends(get_db)) -> BusinessSettingsRead:
    return get_business_settings(db)


@router.put("/settings", response_model=BusinessSettingsRead)
def update_business_settings_endpoint(
    payload: BusinessSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> BusinessSettingsRead:
    current = get_business_settings(db)
    fields = [
        "trade_name",
        "legal_name",
        "rtn",
        "phone",
        "email",
        "address",
        "invoice_enabled",
        "fiscal_enabled",
        "cai",
        "invoice_range_start",
        "invoice_range_end",
        "current_invoice_number",
        "establishment_code",
        "emission_point_code",
        "thermal_paper_width",
    ]
    before = model_snapshot(current, fields)
    updated = update_business_settings(db, payload)
    after = model_snapshot(updated, fields)
    record_audit_event(
        db,
        module="business",
        action="update_settings",
        entity_type="business_settings",
        entity_id=updated.id,
        summary="Configuracion del negocio actualizada.",
        actor=current_user,
        before_data=before,
        after_data=after,
    )
    return updated
