from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.attachments.models import PatientAttachment
from app.modules.attachments.schemas import PatientAttachmentRead
from app.modules.attachments.service import (
    attachment_file_path,
    create_patient_attachment,
    delete_patient_attachment,
    get_patient_attachment,
    list_patient_attachments,
)
from app.modules.audit.service import record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.patients.service import get_patient
from app.modules.users.models import StaffUser

router = APIRouter()


@router.get("/patients/{patient_id}/attachments", response_model=list[PatientAttachmentRead])
def read_patient_attachments(
    patient_id: str,
    db: Session = Depends(get_db),
) -> list[PatientAttachmentRead]:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")
    return list_patient_attachments(db, patient_id)


@router.post(
    "/patients/{patient_id}/attachments",
    response_model=PatientAttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_patient_attachment(
    patient_id: str,
    category: str = Form(default="other"),
    description: str = Form(default=""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> PatientAttachmentRead:
    patient = get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado.")

    try:
        attachment = await create_patient_attachment(
            db,
            patient=patient,
            category=category,
            description=description,
            file=file,
            actor=current_user,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    record_audit_event(
        db,
        module="attachments",
        action="upload",
        entity_type="patient_attachment",
        entity_id=attachment.id,
        summary=f"Adjunto subido para paciente {patient.full_name}: {attachment.original_filename}.",
        actor=current_user,
        after_data={
            "patient_id": patient.id,
            "category": attachment.category,
            "filename": attachment.original_filename,
            "content_type": attachment.content_type,
            "size_bytes": attachment.size_bytes,
            "description": attachment.description,
        },
    )
    return attachment


@router.get("/patients/{patient_id}/attachments/{attachment_id}/download")
def download_patient_attachment(
    patient_id: str,
    attachment_id: str,
    db: Session = Depends(get_db),
) -> FileResponse:
    attachment = _attachment_for_patient(db, patient_id, attachment_id)
    path = attachment_file_path(attachment)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Archivo no encontrado.")
    return FileResponse(
        path,
        media_type=attachment.content_type or "application/octet-stream",
        filename=attachment.original_filename,
    )


@router.delete(
    "/patients/{patient_id}/attachments/{attachment_id}",
    response_model=PatientAttachmentRead,
)
def remove_patient_attachment(
    patient_id: str,
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> PatientAttachmentRead:
    attachment = _attachment_for_patient(db, patient_id, attachment_id)
    deleted = delete_patient_attachment(db, attachment)
    record_audit_event(
        db,
        module="attachments",
        action="delete",
        entity_type="patient_attachment",
        entity_id=deleted.id,
        summary=f"Adjunto eliminado: {deleted.original_filename}.",
        actor=current_user,
        before_data={
            "patient_id": deleted.patient_id,
            "category": deleted.category,
            "filename": deleted.original_filename,
            "description": deleted.description,
        },
    )
    return deleted


def _attachment_for_patient(
    db: Session, patient_id: str, attachment_id: str
) -> PatientAttachment:
    attachment = get_patient_attachment(db, attachment_id)
    if attachment is None or attachment.patient_id != patient_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Adjunto no encontrado.")
    return attachment
