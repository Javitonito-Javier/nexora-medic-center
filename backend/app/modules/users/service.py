from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.events import UserCreatedEvent, publish_event
from app.core.exceptions import ConflictError, NotFoundError
from app.core.transactions import transactional
from app.modules.auth.security import hash_password
from app.modules.users.models import StaffUser
from app.modules.users.schemas import StaffUserCreate, StaffUserUpdate


def list_staff_users(
    db: Session, active: bool | None = None, role: str | None = None
) -> list[StaffUser]:
    statement = select(StaffUser).order_by(StaffUser.full_name.asc())
    if active is not None:
        statement = statement.where(StaffUser.active == active)
    users = list(db.scalars(statement))
    if role:
        users = [user for user in users if role in user.roles]
    return users


@transactional
def create_staff_user(db: Session, payload: StaffUserCreate) -> StaffUser:
    # Verificar si el username ya existe (solo si se proporciona username)
    if payload.username:
        existing = db.scalar(select(StaffUser).where(StaffUser.username == payload.username))
        if existing is not None:
            raise ConflictError(f"El usuario '{payload.username}' ya está registrado.")

    staff_user = StaffUser(
        username=payload.username,
        password_hash=hash_password(payload.password) if payload.password else "",
        full_name=payload.full_name,
        phone=payload.phone,
        roles=list(payload.roles),
        module_permissions=list(payload.module_permissions),
        area=payload.area,
        active=payload.active,
        on_shift=payload.on_shift,
    )
    db.add(staff_user)
    # El commit y rollback los maneja el decorador @transactional
    
    # PUBLICAR EVENTO: Usuario creado
    # Esto dispara auditoría automática
    if staff_user.id and payload.username:
        publish_event(
            UserCreatedEvent(
                aggregate_id=staff_user.id,
                user_id=staff_user.id,
                username=payload.username,
                role=", ".join(payload.roles) if payload.roles else "user"
            )
        )
    
    return staff_user


def get_staff_user(db: Session, staff_user_id: str) -> StaffUser:
    user = db.get(StaffUser, staff_user_id)
    if user is None:
        raise NotFoundError("Usuario", staff_user_id)
    return user


@transactional
def update_staff_user(db: Session, staff_user: StaffUser, payload: StaffUserUpdate) -> StaffUser:
    updates = payload.model_dump(exclude_unset=True)
    password = updates.pop("password", None)

    # Verificar conflicto de username si se está actualizando
    if "username" in updates and updates["username"] != staff_user.username:
        existing = db.scalar(
            select(StaffUser).where(
                StaffUser.username == updates["username"],
                StaffUser.id != staff_user.id
            )
        )
        if existing is not None:
            raise ConflictError(f"El usuario '{updates['username']}' ya está registrado.")

    if password:
        staff_user.password_hash = hash_password(password)
    for field, value in updates.items():
        setattr(staff_user, field, value)

    db.add(staff_user)
    # El commit y rollback los maneja el decorador @transactional
    return staff_user
