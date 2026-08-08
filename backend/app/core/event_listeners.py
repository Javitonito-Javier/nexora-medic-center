"""
Listeners (Oyentes) de Eventos.

Este módulo conecta los eventos de dominio con acciones concretas del sistema.
Aquí es donde ocurre la "magia" de efectos secundarios desacoplados.

Por qué separamos esto:
- Los servicios solo publican eventos ("algo pasó").
- Los listeners deciden qué hacer ("reaccionar a lo que pasó").
- Podemos tener múltiples reacciones para un mismo evento sin acoplamiento.
"""
from app.core.events import (
    EventBus, 
    UserLoggedInEvent, 
    UserCreatedEvent, 
    SaleCompletedEvent,
    AuditEvent,
    DomainEvent
)
from app.modules.audit.service import record_audit_event
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def get_db_session() -> Session:
    """
    Obtiene una sesión de DB para los listeners.
    
    NOTA DE DISEÑO: En una arquitectura más compleja, esto vendría de inyección de dependencias.
    Aquí usamos este método simple porque los listeners son llamados asíncronamente o en el mismo hilo.
    Para producción real con hilos separados, deberíamos pasar la sesión en el contexto del evento.
    """
    # Esta es una implementación simplificada. 
    # En la integración real abajo, pasaremos la sesión explícitamente o usaremos un scope.
    from app.core.database import SessionLocal
    return SessionLocal()


# --- Handlers de Auditoría ---

def on_user_logged_in(event: UserLoggedInEvent):
    """Registra un log de auditoría cuando un usuario inicia sesión."""
    try:
        db = get_db_session()
        record_audit_event(
            db=db,
            user_id=event.user_id,
            action="LOGIN",
            entity_type="USER",
            entity_id=event.user_id,
            details={"username": event.username, "ip": event.ip_address}
        )
        db.commit()
        logger.info(f"Auditoría: Login de usuario {event.username}")
    except Exception as e:
        logger.error(f"Fallo al registrar auditoría de login: {e}")
        db.rollback()
    finally:
        db.close()


def on_user_created(event: UserCreatedEvent):
    """Registra auditoría y notifica (futuro) cuando se crea un usuario."""
    try:
        db = get_db_session()
        record_audit_event(
            db=db,
            user_id=event.user_id, # El ID de quien lo creó podría ser diferente, ajustar si es necesario
            action="CREATE",
            entity_type="USER",
            entity_id=event.user_id,
            details={"username": event.username, "role": event.role}
        )
        db.commit()
        logger.info(f"Auditoría: Usuario creado {event.username}")
    except Exception as e:
        logger.error(f"Fallo al registrar creación de usuario: {e}")
        db.rollback()
    finally:
        db.close()


def on_sale_completed(event: SaleCompletedEvent):
    """Registra auditoría de venta completada."""
    try:
        db = get_db_session()
        # Nota: El user_id aquí debería ser el del vendedor. 
        # Si el evento no lo tiene, asumimos un sistema o lo dejamos None por ahora.
        record_audit_event(
            db=db,
            user_id=None, # Deberíamos pasar el vendedor en el evento
            action="SALE_COMPLETED",
            entity_type="SALE",
            entity_id=event.sale_id,
            details={
                "total": event.total_amount,
                "items": event.items_count,
                "patient_id": event.patient_id
            }
        )
        db.commit()
        logger.info(f"Auditoría: Venta completada ID {event.sale_id}")
    except Exception as e:
        logger.error(f"Fallo al registrar auditoría de venta: {e}")
        db.rollback()
    finally:
        db.close()


def on_audit_event(event: AuditEvent):
    """Maneja eventos de auditoría genéricos directamente."""
    try:
        db = get_db_session()
        record_audit_event(
            db=db,
            user_id=event.user_id,
            action=event.action,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            details=event.details
        )
        db.commit()
    except Exception as e:
        logger.error(f"Fallo al procesar evento de auditoría genérico: {e}")
        db.rollback()
    finally:
        db.close()


# --- Registro de Suscriptores ---

def register_listeners():
    """
    Registra todos los listeners en el Bus de Eventos.
    
    Por qué una función de registro explícita:
    - Evita efectos secundarios al importar el módulo (import hell).
    - Nos permite controlar CUÁNDO se activan los listeners (ej. después de init DB).
    - Facilita tests (podemos no registrar listeners en tests unitarios).
    """
    bus = EventBus()
    
    bus.subscribe(UserLoggedInEvent, on_user_logged_in)
    bus.subscribe(UserCreatedEvent, on_user_created)
    bus.subscribe(SaleCompletedEvent, on_sale_completed)
    bus.subscribe(AuditEvent, on_audit_event)
    
    logger.info("Listeners de eventos registrados exitosamente")
