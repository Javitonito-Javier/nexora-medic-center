from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.modules.auth.security import decode_access_token
from app.modules.users.models import StaffUser


def get_current_user_optional(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> StaffUser | None:
    if settings.app_env == "test" and not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None
    subject = decode_access_token(authorization.removeprefix("Bearer "))
    if subject is None:
        return None
    return db.get(StaffUser, subject)


def get_current_user(
    user: StaffUser | None = Depends(get_current_user_optional),
) -> StaffUser:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso requerido.",
        )
    return user
