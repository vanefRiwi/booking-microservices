"""Eventos de dominio. Su forma serializada es el contrato documentado en
docs/contracts/events.md; el transporte (RabbitMQ) vive en Infrastructure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

if TYPE_CHECKING:
    from app.src.domain.entities.booking import Booking


@dataclass(frozen=True)
class DomainEvent:
    name: ClassVar[str]
    booking_id: UUID
    user_id: UUID
    resource_id: UUID
    start_at: datetime
    end_at: datetime
    occurred_at: datetime

    @classmethod
    def _base_fields(cls, booking: Booking, occurred_at: datetime) -> dict:
        return {
            "booking_id": booking.id,
            "user_id": booking.user_id,
            "resource_id": booking.resource_id,
            "start_at": booking.slot.start_at,
            "end_at": booking.slot.end_at,
            "occurred_at": occurred_at,
        }


@dataclass(frozen=True)
class BookingCreated(DomainEvent):
    name: ClassVar[str] = "booking.created"
    total_amount: Decimal = Decimal("0")

    @classmethod
    def from_booking(cls, booking: Booking, occurred_at: datetime) -> BookingCreated:
        return cls(**cls._base_fields(booking, occurred_at), total_amount=booking.total_amount)


@dataclass(frozen=True)
class BookingConfirmed(DomainEvent):
    name: ClassVar[str] = "booking.confirmed"

    @classmethod
    def from_booking(cls, booking: Booking, occurred_at: datetime) -> BookingConfirmed:
        return cls(**cls._base_fields(booking, occurred_at))


@dataclass(frozen=True)
class BookingCancelled(DomainEvent):
    name: ClassVar[str] = "booking.cancelled"
    reason: str | None = None

    @classmethod
    def from_booking(cls, booking: Booking, occurred_at: datetime) -> BookingCancelled:
        return cls(**cls._base_fields(booking, occurred_at), reason=booking.cancellation_reason)
