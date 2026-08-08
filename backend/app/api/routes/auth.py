from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.audit.service import record_audit_event
from app.modules.auth.schemas import LoginRequest, LoginResponse
from app.modules.auth.security import create_access_token
from app.modules.auth.service import authenticate_user

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = authenticate_user(db, payload.username, payload.password)
    if user is None:
        record_audit_event(
            db,
            module="auth",
            action="login_failed",
            entity_type="staff_user",
            summary=f"Intento fallido de login para {payload.username}.",
            after_data={"username": payload.username},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contrasena incorrectos.",
        )
    record_audit_event(
        db,
        module="auth",
        action="login_success",
        entity_type="staff_user",
        entity_id=user.id,
        summary=f"Login exitoso de {user.full_name}.",
        actor=user,
        after_data={"username": user.username, "roles": user.roles},
    )
    return LoginResponse(access_token=create_access_token(user.id), user=user)
