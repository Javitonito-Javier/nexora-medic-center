"""
Excepciones personalizadas para el dominio de la aplicación.

Estas excepciones permiten separar la lógica de negocio (servicios)
de la capa HTTP (rutas FastAPI), facilitando un manejo de errores
consistente y testeable.
"""


class DomainError(Exception):
    """
    Excepción base para errores de dominio/negocio.

    Se usa cuando una operación viola reglas de negocio,
    pero no es un error técnico del sistema.

    Ejemplos:
        - Stock insuficiente para una venta
        - Paciente ya existe con ese número de identidad
        - Usuario inactivo intentando acceder
    """
    def __init__(self, message: str, code: str | None = None):
        self.message = message
        self.code = code or "DOMAIN_ERROR"
        super().__init__(self.message)


class NotFoundError(DomainError):
    """
    Recurso no encontrado.

    Ejemplos:
        - Paciente con ID específico no existe
        - Producto buscado no está en inventario
    """
    def __init__(self, resource: str, identifier: str | None = None):
        message = f"{resource} no encontrado"
        if identifier:
            message += f": {identifier}"
        super().__init__(message=message, code="NOT_FOUND")


class ValidationError(DomainError):
    """
    Error de validación de datos de entrada.

    Diferente a HTTP 422 de Pydantic, esta se usa para
    validaciones de negocio que ocurren después del parsing.

    Ejemplos:
        - Fecha de vencimiento ya pasó
        - Precio negativo no permitido
        - Cantidad solicitada mayor a stock disponible
    """
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.field = field


class ConflictError(DomainError):
    """
    Conflicto por estado actual del recurso.

    Ejemplos:
        - Usuario ya está activo/inactivo
        - Lote ya fue retirado
        - Caja ya fue cerrada
    """
    def __init__(self, message: str):
        super().__init__(message=message, code="CONFLICT")


class InsufficientStockError(ValidationError):
    """
    Stock insuficiente para completar operación.

    Caso especial de ValidationError para manejo específico
    en inventario y farmacia.
    """
    def __init__(
        self,
        product_name: str,
        requested: int,
        available: int,
        location: str | None = None
    ):
        location_msg = f" en {location}" if location else ""
        message = (
            f"Stock insuficiente para '{product_name}': "
            f"solicitado {requested}, disponible {available}{location_msg}."
        )
        super().__init__(message=message, field="stock")
        self.product_name = product_name
        self.requested = requested
        self.available = available


class AuthenticationError(DomainError):
    """
    Error de autenticación.

    Ejemplos:
        - Credenciales inválidas
        - Token expirado
        - Usuario desactivado
    """
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(message=message, code="AUTHENTICATION_ERROR")


class PermissionDeniedError(DomainError):
    """
    Usuario sin permisos para realizar acción.

    Ejemplos:
        - Intenta acceder a módulo sin rol adecuado
        - Intenta aprobar operación sin autorización
    """
    def __init__(self, action: str, resource: str | None = None):
        message = f"Permiso denegado para {action}"
        if resource:
            message += f" en {resource}"
        super().__init__(message=message, code="PERMISSION_DENIED")
