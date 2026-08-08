from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.schemas import AuditEventRead
from app.modules.audit.service import list_audit_events

router = APIRouter()


@router.get("/", response_model=list[AuditEventRead])
def read_audit_events(
    module: str | None = Query(default=None, max_length=80),
    entity_type: str | None = Query(default=None, max_length=80),
    entity_id: str | None = Query(default=None, max_length=80),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[AuditEventRead]:
    return list_audit_events(
        db,
        module=module,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
    )
