from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.api.router import api_router
from app.core.config import settings
from app.core.event_listeners import register_listeners
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    DomainError,
    InsufficientStockError,
    NotFoundError,
    PermissionDeniedError,
)
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.modules.auth.security import decode_access_token
from app.modules.licensing.service import can_write

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
AUTH_EXEMPT_PREFIXES = (
    "/api/v1/auth",
    "/api/v1/license",
    "/health",
)
PUBLIC_GET_PATHS = {
    "/api/v1/business/settings",
}
LICENSE_EXEMPT_PREFIXES = (
    "/api/v1/auth",
    "/api/v1/license",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Inicializar base de datos
    init_db()
    # Registrar listeners de eventos para auditoría y notificaciones
    register_listeners()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def auth_guard(request, call_next):
        # Skip auth for test environment or OPTIONS requests
        if settings.app_env == "test":
            return await call_next(request)
        if request.method == "OPTIONS":
            return await call_next(request)
        if request.method == "GET" and request.url.path in PUBLIC_GET_PATHS:
            return await call_next(request)
        if not request.url.path.startswith(AUTH_EXEMPT_PREFIXES):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token de acceso requerido."},
                )
            token = auth_header.removeprefix("Bearer ")
            subject = decode_access_token(token)
            if subject is None:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token invalido o expirado."},
                )
        return await call_next(request)

    @app.middleware("http")
    async def license_write_guard(request, call_next):
        if (
            settings.license_enforcement_enabled
            and request.method in WRITE_METHODS
            and request.url.path.startswith("/api/v1")
            and not request.url.path.startswith(LICENSE_EXEMPT_PREFIXES)
        ):
            with SessionLocal() as db:
                status = can_write(db)
                if not status.can_write:
                    return JSONResponse(
                        status_code=402,
                        content={
                            "detail": status.message,
                            "license_status": status.status,
                        },
                    )
        return await call_next(request)

    app.include_router(api_router, prefix="/api/v1")

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        """Manejador central para errores de dominio."""
        status_code = 400

        if isinstance(exc, NotFoundError):
            status_code = 404
        elif isinstance(exc, ConflictError):
            status_code = 409
        elif isinstance(exc, AuthenticationError):
            status_code = 401
        elif isinstance(exc, PermissionDeniedError):
            status_code = 403
        elif isinstance(exc, InsufficientStockError):
            status_code = 422

        return JSONResponse(
            status_code=status_code,
            content={
                "detail": exc.message,
                "error_code": exc.code,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Manejador para errores de base de datos."""
        # Log error internally (in production, use proper logging)
        error_detail = "Error interno del servidor"
        status_code = 500

        if isinstance(exc, IntegrityError):
            error_detail = "Violación de integridad de datos"
            status_code = 400

        return JSONResponse(
            status_code=status_code,
            content={"detail": error_detail},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        """Manejador para errores de validación básicos."""
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()
