from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Clinicapharma API"
    app_env: str = "local"
    secret_key: str = Field(..., description="Clave secreta para JWT y seguridad. Debe ser única por instalación.")
    database_url: str = "postgresql+psycopg://postgres:toor@localhost:5432/clinicapharma"
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_origin_regex: str = r"http://(localhost|127\.0\.0\.1):\d+"
    license_enforcement_enabled: bool = False
    license_public_key: str = ""
    license_grace_days: int = 7
    initial_admin_username: str = "admin"
    initial_admin_password: str = "admin123"
    attachment_storage_dir: str = "local_data/attachments"
    attachment_max_size_bytes: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or v == "change-me":
            raise ValueError(
                "SECRET_KEY no configurada. Genere una clave segura con: "
                "python -c 'import secrets; print(secrets.token_urlsafe(32))' "
                "y agréguela al archivo .env"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
