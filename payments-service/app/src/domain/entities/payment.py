"""Entidad Payment en Python puro. Un pago pertenece a una reserva por su id
(booking_id); payments-service no lee la base de bookings."""

import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class InvalidPayment(Exception):
    pass


@dataclass
class Payment:
    """Invariantes: monto > 0; un pago solo se resuelve una vez (integridad de la
    transacción). idempotency_key evita cobrar dos veces el mismo intento."""

    id: uuid.UUID
    booking_id: uuid.UUID
    amount: Decimal
    idempotency_key: str
    status: PaymentStatus
    created_at: datetime
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise InvalidPayment("El monto debe ser mayor que cero.")

    def succeed(self) -> None:
        self._ensure_pending()
        self.status = PaymentStatus.SUCCEEDED

    def fail(self, reason: str) -> None:
        self._ensure_pending()
        self.status = PaymentStatus.FAILED
        self.failure_reason = reason

    def _ensure_pending(self) -> None:
        if self.status is not PaymentStatus.PENDING:
            raise InvalidPayment(f"El pago ya fue resuelto ({self.status}).")
