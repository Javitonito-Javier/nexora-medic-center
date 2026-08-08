from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import model_snapshot, record_audit_event
from app.modules.auth.dependencies import get_current_user_optional
from app.modules.users.models import StaffUser
from app.modules.users.schemas import StaffUserCreate, StaffUserRead, StaffUserUpdate
from app.modules.users.service import (
    create_staff_user,
    get_staff_user,
    list_staff_users,
    update_staff_user,
)

router = APIRouter()


@router.get("/", response_model=list[StaffUserRead])
def read_staff_users(
    active: bool | None = Query(default=None),
    role: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[StaffUserRead]:
    return list_staff_users(db, active=active, role=role)


@router.post("/", response_model=StaffUserRead, status_code=status.HTTP_201_CREATED)
def create_staff_user_endpoint(
    payload: StaffUserCreate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> StaffUserRead:
    staff_user = create_staff_user(db, payload)
    record_audit_event(
        db,
        module="users",
        action="create",
        entity_type="staff_user",
        entity_id=staff_user.id,
        summary=f"Usuario creado: {staff_user.full_name}.",
        actor=current_user,
        after_data=payload.model_dump(),
    )
    return staff_user


@router.patch("/{staff_user_id}", response_model=StaffUserRead)
def update_staff_user_endpoint(
    staff_user_id: str,
    payload: StaffUserUpdate,
    db: Session = Depends(get_db),
    current_user: StaffUser | None = Depends(get_current_user_optional),
) -> StaffUserRead:
    staff_user = get_staff_user(db, staff_user_id)
    if staff_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario/personal no encontrado."
        )
    fields = [
        "username",
        "full_name",
        "phone",
        "roles",
        "module_permissions",
        "area",
        "active",
        "on_shift",
    ]
    before = model_snapshot(staff_user, fields)
    updated = update_staff_user(db, staff_user, payload)
    after = model_snapshot(updated, fields)
    record_audit_event(
        db,
        module="users",
        action="update",
        entity_type="staff_user",
        entity_id=updated.id,
        summary=f"Usuario actualizado: {updated.full_name}.",
        actor=current_user,
        before_data=before,
        after_data=after,
    )
    return updated
