"""Adaptadores de salida para eventos. Hoy se registran en el log con el mismo
formato que tendrán en RabbitMQ (exchange `booking.events`, routing key = nombre
del evento). En la sesión de mensajería se agrega un RabbitMQEventPublisher que
implementa el mismo puerto, sin tocar dominio ni casos de uso."""

import json
import logging
from collections.abc import Sequence
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.src.application.ports import EventPublisher
from app.src.domain.events import DomainEvent

logger = logging.getLogger(__name__)

EXCHANGE = "booking.events"


def _default(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (UUID, Decimal)):
        return str(value)
    raise TypeError(f"Tipo no serializable: {type(value)}")


def to_message(event: DomainEvent) -> dict:
    """Sobre del mensaje definido en docs/contracts/events.md."""
    payload = asdict(event)
    occurred_at = payload.pop("occurred_at")
    return {
        "event_id": str(uuid4()),
        "event_type": event.name,
        "event_version": 1,
        "occurred_at": occurred_at.isoformat(),
        "producer": "bookings-service",
        "data": json.loads(json.dumps(payload, default=_default)),
    }


class LoggingEventPublisher(EventPublisher):
    def publish(self, events: Sequence[DomainEvent]) -> None:
        for event in events:
            logger.info("[%s] %s %s", EXCHANGE, event.name, json.dumps(to_message(event)))


class InMemoryEventPublisher(EventPublisher):
    """Útil en pruebas para verificar qué se publicó."""

    def __init__(self) -> None:
        self.messages: list[dict] = []

    def publish(self, events: Sequence[DomainEvent]) -> None:
        self.messages.extend(to_message(event) for event in events)
