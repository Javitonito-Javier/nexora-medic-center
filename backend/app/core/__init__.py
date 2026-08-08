"""
Módulo core de la aplicación.

Contiene configuración, excepciones y utilidades compartidas.
"""

from app.core.config import Settings, settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    DomainError,
    InsufficientStockError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.core.transactions import TransactionContext, TransactionError, atomic_operation, transactional

__all__ = [
    "Settings",
    "settings",
    "DomainError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "InsufficientStockError",
    "AuthenticationError",
    "PermissionDeniedError",
    "TransactionError",
    "transactional",
    "TransactionContext",
    "atomic_operation",
]
