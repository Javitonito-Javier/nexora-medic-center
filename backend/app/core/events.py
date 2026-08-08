"""
Sistema de Eventos de Dominio (Domain Events).

Este módulo implementa un patrón de eventos para desacoplar la lógica de negocio
de efectos secundarios como auditoría, notificaciones y actualizaciones de caché.

Por qué usamos esto:
- Desacoplamiento: El servicio de Ventas no necesita saber cómo se guarda un log de auditoría.
- Extensibilidad: Podemos agregar nuevos oyentes (ej. enviar email) sin tocar el código existente.
- Consistencia: Centralizamos la lógica de reacción a cambios de estado.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Type
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent:
    """Clase base para todos los eventos de dominio."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    aggregate_id: str | None = None  # ID de la entidad principal (ej. user_id, sale_id)
    
    @property
    def event_name(self) -> str:
        return self.__class__.__name__


# --- Eventos Concretos ---

@dataclass
class UserLoggedInEvent(DomainEvent):
    user_id: str = ""
    username: str = ""
    ip_address: str | None = None

@dataclass
class UserCreatedEvent(DomainEvent):
    user_id: str = ""
    username: str = ""
    role: str = ""

@dataclass
class SaleCompletedEvent(DomainEvent):
    sale_id: str = ""
    total_amount: float = 0.0
    patient_id: str | None = None
    items_count: int = 0

@dataclass
class StockLowEvent(DomainEvent):
    product_id: str = ""
    product_name: str = ""
    current_stock: int = 0
    threshold: int = 0

@dataclass
class AuditEvent(DomainEvent):
    """Evento genérico para auditoría directa."""
    action: str = ""
    entity_type: str = ""
    entity_id: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    user_id: str | None = None


# --- Bus de Eventos ---

class EventBus:
    """
    Bus centralizado de eventos.
    
    Por qué esta implementación simple:
    - No requiere dependencias externas (Redis/RabbitMQ) para empezar.
    - Suficiente para monolito modular.
    - Fácil de migrar a un bus externo luego si escalamos.
    """
    _instance: 'EventBus | None' = None
    _listeners: Dict[Type[DomainEvent], List[Callable]] = {}

    def __new__(cls) -> 'EventBus':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable):
        """Suscribe un handler a un tipo de evento."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(handler)
        logger.debug(f"Suscriptor registrado para {event_type.__name__}")

    def publish(self, event: DomainEvent):
        """Publica un evento y notifica a todos los suscriptores."""
        event_type = type(event)
        handlers = self._listeners.get(event_type, [])
        
        # También buscar handlers para clases padre (polimorfismo)
        for base_type in event_type.__mro__:
            if base_type in self._listeners and base_type != DomainEvent:
                handlers.extend(self._listeners[base_type])

        if not handlers:
            logger.debug(f"No hay suscriptores para {event.event_name}")
            return

        logger.info(f"Publicando evento: {event.event_name} (ID: {event.aggregate_id})")
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # CRÍTICO: Un fallo en un listener no debe romper la operación principal
                # Pero debemos loggearlo urgentemente.
                logger.error(f"Error en handler {handler.__name__} para evento {event.event_name}: {e}", exc_info=True)
                # Aquí podríamos guardar el error en una tabla de "fallos de eventos" para reintentar luego


# Instancia global única
event_bus = EventBus()


def publish_event(event: DomainEvent):
    """Función helper para publicar eventos desde cualquier parte del código."""
    event_bus.publish(event)
