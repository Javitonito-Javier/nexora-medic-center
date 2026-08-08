from datetime import date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditEvent
from app.modules.users.models import StaffUser

SENSITIVE_KEYS = {"password", "password_hash", "access_token", "token"}


def _serialize_audit_value(value: Any) -> Any:
    if isinstance(value, date | datetime):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, dict):
        return sanitize_audit_data(value)
    if isinstance(value, list):
        return [_serialize_audit_value(item) for item in value]
    return value


def sanitize_audit_data(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None
    sanitized: dict[str, Any] = {}
    for key, value in data.items():
        if key in SENSITIVE_KEYS:
            sanitized[key] = "***"
        else:
            sanitized[key] = _serialize_audit_value(value)
    return sanitized


def model_snapshot(model: Any, fields: list[str]) -> dict[str, Any]:
    return {field: getattr(model, field, None) for field in fields}


def record_audit_event(
    db: Session,
    *,
    module: str,
    action: str,
    entity_type: str,
    entity_id: str = "",
    summary: str = "",
    actor: StaffUser | None = None,
    before_data: dict[str, Any] | None = None,
    after_data: dict[str, Any] | None = None,
    reason: str = "",
) -> AuditEvent:
    event = AuditEvent(
        actor_user_id=actor.id if actor else None,
        actor_username=actor.username or "" if actor else "",
        actor_name=actor.full_name if actor else "",
        module=module,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        before_data=sanitize_audit_data(before_data),
        after_data=sanitize_audit_data(after_data),
        reason=reason,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_audit_events(
    db: Session,
    *,
    module: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = 100,
) -> list[AuditEvent]:
    statement = select(AuditEvent).order_by(AuditEvent.created_at.desc())
    if module:
        statement = statement.where(AuditEvent.module == module)
    if entity_type:
        statement = statement.where(AuditEvent.entity_type == entity_type)
    if entity_id:
        statement = statement.where(AuditEvent.entity_id == entity_id)
    statement = statement.limit(limit)
    return list(db.scalars(statement))
