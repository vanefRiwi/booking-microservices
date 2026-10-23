from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from app.src.domain.entities.payment import Payment


class PaymentRepository(ABC):
    @abstractmethod
    def add(self, payment: Payment) -> None: ...

    @abstractmethod
    def get_by_idempotency_key(self, key: str) -> Payment | None: ...


class PaymentGateway(ABC):
    """Hoy un simulador; mañana una pasarela real sin cambiar el dominio."""

    @abstractmethod
    def charge(self, booking_id: UUID, amount: Decimal) -> tuple[bool, str | None]: ...


class EventPublisher(ABC):
    """Publica payment.succeeded / payment.failed (docs/contracts/events.md)."""

    @abstractmethod
    def publish(self, event_type: str, data: dict) -> None: ...
