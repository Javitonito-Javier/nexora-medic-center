from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.security import verify_password
from app.modules.users.models import StaffUser


def authenticate_user(db: Session, username: str, password: str) -> StaffUser | None:
    statement = select(StaffUser).where(StaffUser.username == username, StaffUser.active.is_(True))
    user = db.scalar(statement)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
