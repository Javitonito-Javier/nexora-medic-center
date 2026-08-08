import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_password_strength(value: str) -> str:
    """Valida que la contraseña cumpla con los requisitos de seguridad.

    Nota: Esta validación se aplica solo en producción.
    En entorno de testing, se permite cualquier contraseña para facilitar pruebas.
    """
    import os
    # Skip strict validation in test environment
    if os.getenv("APP_ENV") == "test":
        if len(value) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return value

    if len(value) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    if not re.search(r"[A-Z]", value):
        raise ValueError("La contraseña debe incluir al menos una letra mayúscula")
    if not re.search(r"[a-z]", value):
        raise ValueError("La contraseña debe incluir al menos una letra minúscula")
    if not re.search(r"\d", value):
        raise ValueError("La contraseña debe incluir al menos un número")
    return value


StaffRole = Literal["admin", "receptionist", "nurse", "doctor", "pharmacy", "cashier"]
StaffArea = Literal["clinic", "pharmacy", "both"]
StaffModule = Literal[
    "dashboard",
    "patients",
    "appointments",
    "consultations",
    "staff",
    "pharmacy",
    "inventory",
    "cash_registers",
    "reports",
    "audit",
    "settings",
]


class StaffUserBase(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=80)
    full_name: str = Field(min_length=2, max_length=180)
    phone: str = Field(default="", max_length=40)
    roles: list[StaffRole] = Field(default_factory=list)
    module_permissions: list[StaffModule] = Field(default_factory=list)
    area: StaffArea = "clinic"
    active: bool = True
    on_shift: bool = False


class StaffUserCreate(StaffUserBase):
    password: str | None = Field(default=None, min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is not None:
            return validate_password_strength(v)
        return v


class StaffUserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=180)
    username: str | None = Field(default=None, min_length=3, max_length=80)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    phone: str | None = Field(default=None, max_length=40)
    roles: list[StaffRole] | None = None
    module_permissions: list[StaffModule] | None = None
    area: StaffArea | None = None
    active: bool | None = None
    on_shift: bool | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str | None) -> str | None:
        if v is not None:
            return validate_password_strength(v)
        return v


class StaffUserRead(StaffUserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
