import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.attachments.models import PatientAttachment
from app.modules.attachments.schemas import AttachmentCategory
from app.modules.patients.models import Patient
from app.modules.users.models import StaffUser

ALLOWED_CONTENT_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def list_patient_attachments(db: Session, patient_id: str) -> list[PatientAttachment]:
    statement = (
        select(PatientAttachment)
        .where(PatientAttachment.patient_id == patient_id)
        .where(PatientAttachment.deleted_at.is_(None))
        .order_by(PatientAttachment.created_at.desc())
    )
    return list(db.scalars(statement))


def get_patient_attachment(db: Session, attachment_id: str) -> PatientAttachment | None:
    attachment = db.get(PatientAttachment, attachment_id)
    if attachment is None or attachment.deleted_at is not None:
        return None
    return attachment


async def create_patient_attachment(
    db: Session,
    *,
    patient: Patient,
    category: str,
    description: str,
    file: UploadFile,
    actor: StaffUser | None = None,
) -> PatientAttachment:
    normalized_category = _normalize_category(category)
    original_filename = _safe_original_filename(file.filename or "adjunto")
    content_type = file.content_type or ""
    extension = _extension_for(content_type, original_filename)
    data = await file.read()
    _validate_file(content_type, len(data))

    stored_filename = f"{uuid4()}{extension}"
    patient_dir = _patient_storage_dir(patient.id)
    patient_dir.mkdir(parents=True, exist_ok=True)
    (patient_dir / stored_filename).write_bytes(data)

    attachment = PatientAttachment(
        patient_id=patient.id,
        category=normalized_category,
        original_filename=original_filename,
        stored_filename=stored_filename,
        content_type=content_type,
        size_bytes=len(data),
        description=description.strip(),
        uploaded_by_user_id=actor.id if actor else None,
        uploaded_by_name=actor.full_name if actor else "",
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def delete_patient_attachment(db: Session, attachment: PatientAttachment) -> PatientAttachment:
    attachment.deleted_at = datetime.now(UTC)
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def attachment_file_path(attachment: PatientAttachment) -> Path:
    return _patient_storage_dir(attachment.patient_id) / attachment.stored_filename


def _normalize_category(category: str) -> str:
    value = category.strip() or AttachmentCategory.other.value
    allowed = {item.value for item in AttachmentCategory}
    if value not in allowed:
        raise ValueError("Categoria de adjunto no permitida.")
    return value


def _extension_for(content_type: str, filename: str) -> str:
    if content_type in ALLOWED_CONTENT_TYPES:
        return ALLOWED_CONTENT_TYPES[content_type]
    suffix = Path(filename).suffix.lower()
    allowed_suffixes = set(ALLOWED_CONTENT_TYPES.values())
    if suffix in allowed_suffixes:
        return suffix
    raise ValueError("Tipo de archivo no permitido. Usa PDF, JPG, PNG o WEBP.")


def _validate_file(content_type: str, size_bytes: int) -> None:
    if size_bytes <= 0:
        raise ValueError("El archivo esta vacio.")
    if size_bytes > settings.attachment_max_size_bytes:
        raise ValueError("El archivo supera el tamano maximo permitido.")
    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Tipo de archivo no permitido. Usa PDF, JPG, PNG o WEBP.")


def _safe_original_filename(filename: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._ -]", "_", filename).strip()
    return safe[:240] or "adjunto"


def _patient_storage_dir(patient_id: str) -> Path:
    return Path(settings.attachment_storage_dir) / patient_id
