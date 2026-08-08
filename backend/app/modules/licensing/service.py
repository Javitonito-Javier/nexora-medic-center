import base64
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.licensing.models import SystemLicense
from app.modules.licensing.schemas import LicenseStatusRead

LICENSE_ID = "main"
WRITE_ALLOWED_STATUSES = {"disabled", "active", "grace"}


class LicenseError(ValueError):
    pass


def activate_license(db: Session, license_key: str) -> LicenseStatusRead:
    payload = _decode_and_verify(license_key)
    expires_at = _parse_datetime(payload.get("expires_at"))
    if expires_at is None:
        raise LicenseError("La licencia no contiene una fecha de vencimiento valida.")

    license_row = db.get(SystemLicense, LICENSE_ID)
    if license_row is None:
        license_row = SystemLicense(id=LICENSE_ID, license_key=license_key)

    license_row.license_key = license_key
    license_row.customer_name = str(payload.get("customer_name", ""))
    license_row.installation_id = str(payload.get("installation_id", ""))
    license_row.payload_json = json.dumps(payload, ensure_ascii=True, sort_keys=True)
    license_row.expires_at = expires_at
    license_row.activated_at = datetime.now(UTC)
    license_row.last_checked_at = None
    db.add(license_row)
    db.commit()
    db.refresh(license_row)
    return get_license_status(db)


def get_license_status(db: Session, *, update_check: bool = True) -> LicenseStatusRead:
    if not settings.license_enforcement_enabled:
        return LicenseStatusRead(
            enforcement_enabled=False,
            status="disabled",
            message="Control de licencia desactivado para este entorno.",
            can_write=True,
        )

    license_row = db.get(SystemLicense, LICENSE_ID)
    if license_row is None:
        return LicenseStatusRead(
            enforcement_enabled=True,
            status="missing",
            message="No hay licencia cargada. Cargue una licencia valida para registrar operaciones nuevas.",
            can_write=False,
        )

    now = datetime.now(UTC)
    status = "active"
    message = "Licencia activa."
    days_remaining: int | None = None

    try:
        payload = _decode_and_verify(license_row.license_key)
        expires_at = _parse_datetime(payload.get("expires_at"))
        if expires_at is None:
            raise LicenseError("Fecha de vencimiento invalida.")
        if license_row.last_checked_at is not None and now < _as_utc(
            license_row.last_checked_at
        ) - timedelta(days=1):
            status = "invalid_clock"
            message = (
                "El reloj del servidor parece haber retrocedido. Revise fecha y hora del equipo."
            )
        else:
            days_remaining = (expires_at.date() - now.date()).days
            if now <= expires_at:
                status = "active"
                message = f"Licencia activa. Restan {days_remaining} dias."
            elif now <= expires_at + timedelta(days=settings.license_grace_days):
                grace_left = (expires_at + timedelta(days=settings.license_grace_days) - now).days
                status = "grace"
                message = f"Licencia vencida en periodo de gracia. Restan {max(grace_left, 0)} dias de gracia."
            else:
                status = "expired"
                message = "Licencia vencida. Renueve para registrar operaciones nuevas."

        license_row.customer_name = str(payload.get("customer_name", license_row.customer_name))
        license_row.installation_id = str(
            payload.get("installation_id", license_row.installation_id)
        )
        license_row.payload_json = json.dumps(payload, ensure_ascii=True, sort_keys=True)
        license_row.expires_at = expires_at
    except Exception as exc:
        status = "invalid"
        message = f"Licencia invalida: {exc}"
        days_remaining = None

    license_row.status = status
    if update_check:
        license_row.last_checked_at = now
    db.add(license_row)
    db.commit()

    return LicenseStatusRead(
        enforcement_enabled=True,
        status=status,
        customer_name=license_row.customer_name,
        installation_id=license_row.installation_id,
        expires_at=license_row.expires_at,
        days_remaining=days_remaining,
        message=message,
        can_write=status in WRITE_ALLOWED_STATUSES,
    )


def can_write(db: Session) -> LicenseStatusRead:
    return get_license_status(db, update_check=True)


def _decode_and_verify(license_key: str) -> dict[str, Any]:
    if not settings.license_public_key:
        raise LicenseError("No hay clave publica de licencia configurada.")

    parts = license_key.strip().split(".")
    if len(parts) != 2:
        raise LicenseError("Formato de licencia invalido.")

    payload_part, signature_part = parts
    payload_bytes = _b64decode(payload_part)
    signature = _b64decode(signature_part)
    public_key = Ed25519PublicKey.from_public_bytes(_b64decode(settings.license_public_key))
    try:
        public_key.verify(signature, payload_part.encode("ascii"))
    except InvalidSignature as exc:
        raise LicenseError("La firma no coincide con los datos de la licencia.") from exc

    payload = json.loads(payload_bytes.decode("utf-8"))
    if not isinstance(payload, dict):
        raise LicenseError("Contenido de licencia invalido.")
    return payload


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return _as_utc(parsed)


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))
