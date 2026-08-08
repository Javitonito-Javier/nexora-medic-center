"""Utilidades para manejo seguro de transacciones de base de datos.

Este módulo proporciona decoradores y context managers para garantizar
que las operaciones de base de datos se completen atómicamente o se
reviertan completamente en caso de error.
"""

from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

P = ParamSpec("P")
R = TypeVar("R")


class TransactionError(Exception):
    """Excepción personalizada para errores de transacción."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


def transactional(func: Callable[P, R]) -> Callable[P, R]:
    """Decorador para manejar transacciones automáticamente.

    Este decorador envuelve la función decorada para:
    1. Ejecutar la función
    2. Hacer commit si no hay errores
    3. Hacer rollback si ocurre alguna excepción
    4. Relanzar la excepción con información contextual

    Args:
        func: Función que recibe un Session como primer argumento

    Returns:
        La función envuelta con manejo automático de transacciones

    Example:
        @transactional
        def create_user(db: Session, data: UserData) -> User:
            user = User(**data)
            db.add(user)
            return user
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if not args or not isinstance(args[0], Session):
            raise TransactionError(
                "La primera argumento debe ser una sesión de SQLAlchemy"
            )

        db = args[0]
        try:
            result = func(*args, **kwargs)
            db.commit()
            return result
        except (SQLAlchemyError, ValueError, TransactionError):
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise TransactionError(f"Error inesperado en transacción: {str(e)}", e) from e

    return wrapper


class TransactionContext:
    """Context manager para manejo explícito de transacciones.

    Proporciona control más fino sobre el comportamiento de la transacción,
    permitiendo rollbacks condicionales o múltiples operaciones relacionadas.

    Attributes:
        db: Sesión de SQLAlchemy a utilizar
        commit_on_exit: Si True, hace commit al salir del contexto (default: True)

    Example:
        with TransactionContext(db) as tx:
            user = create_user(db, user_data)
            profile = create_profile(db, user.id, profile_data)
            # Commit automático al salir del bloque
    """

    def __init__(self, db: Session, commit_on_exit: bool = True):
        self.db = db
        self.commit_on_exit = commit_on_exit
        self._should_rollback = False

    def __enter__(self) -> "TransactionContext":
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> bool:
        if exc_type is not None:
            # Siempre rollback si hay excepción
            self.db.rollback()
            return False  # Relanzar la excepción

        if self._should_rollback:
            self.db.rollback()
            return False

        if self.commit_on_exit:
            try:
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise TransactionError(f"Error al hacer commit: {str(e)}", e) from e

        return False

    def mark_for_rollback(self) -> None:
        """Marca la transacción para rollback al salir del contexto."""
        self._should_rollback = True


def atomic_operation(db: Session, operation: Callable[[], Any], operation_name: str = "operación") -> Any:
    """Ejecuta una operación atómica con manejo de errores.

    Función de utilidad para ejecutar operaciones individuales con
    rollback automático en caso de fallo.

    Args:
        db: Sesión de SQLAlchemy
        operation: Función callable que ejecuta la operación
        operation_name: Nombre descriptivo de la operación para logging

    Returns:
        El resultado de ejecutar la operación

    Raises:
        TransactionError: Si la operación falla

    Example:
        result = atomic_operation(
            db,
            lambda: db.query(User).filter_by(id=user_id).first(),
            "consulta de usuario"
        )
    """
    try:
        result = operation()
        db.commit()
        return result
    except (SQLAlchemyError, ValueError) as e:
        db.rollback()
        raise TransactionError(f"Error en {operation_name}: {str(e)}", e) from e
    except Exception as e:
        db.rollback()
        raise TransactionError(f"Error inesperado en {operation_name}: {str(e)}", e) from e
