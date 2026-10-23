from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from app.src.domain.events import BookingCancelled, BookingConfirmed, BookingCreated, DomainEvent
from app.src.domain.exceptions import (
    BookingAlreadyStarted,
    BookingInThePast,
    DomainError,
    InvalidStatusTransition,
)
from app.src.domain.value_objects import BookingStatus, TimeSlot

SECONDS_PER_HOUR = Decimal(3600)
CENTS = Decimal("0.01")


@dataclass
class Booking:
    """Reserva de un recurso (sala, equipo...) por un usuario.

    Invariantes:
    - El horario es válido (fin > inicio) y no está en el pasado al crearse.
    - Solo se permiten las transiciones PENDING -> CONFIRMED, PENDING|CONFIRMED -> CANCELLED.
    - El precio se congela al crear la reserva (copia del dato de resources-service).
    """

    id: UUID
    user_id: UUID
    resource_id: UUID
    slot: TimeSlot
    status: BookingStatus
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    cancellation_reason: str | None = None
    _events: list[DomainEvent] = field(default_factory=list, repr=False, compare=False)

    @classmethod
    def create(
        cls,
        *,
        user_id: UUID,
        resource_id: UUID,
        slot: TimeSlot,
        hourly_rate: Decimal,
        now: datetime,
    ) -> "Booking":
        if slot.start_at <= now:
            raise BookingInThePast()
        if hourly_rate < 0:
            raise DomainError("La tarifa del recurso no puede ser negativa.")

        hours = Decimal(int(slot.duration.total_seconds())) / SECONDS_PER_HOUR
        booking = cls(
            id=uuid4(),
            user_id=user_id,
            resource_id=resource_id,
            slot=slot,
            status=BookingStatus.PENDING,
            total_amount=(hourly_rate * hours).quantize(CENTS, rounding=ROUND_HALF_UP),
            created_at=now,
            updated_at=now,
        )
        booking._record(BookingCreated.from_booking(booking, occurred_at=now))
        return booking

    @property
    def blocks_availability(self) -> bool:
        return self.status.blocks_availability

    def conflicts_with(self, other: "Booking") -> bool:
        return (
            self.id != other.id
            and self.resource_id == other.resource_id
            and self.blocks_availability
            and other.blocks_availability
            and self.slot.overlaps(other.slot)
        )

    def confirm(self, now: datetime) -> None:
        if self.status is not BookingStatus.PENDING:
            raise InvalidStatusTransition(self.status, BookingStatus.CONFIRMED)
        self.status = BookingStatus.CONFIRMED
        self.updated_at = now
        self._record(BookingConfirmed.from_booking(self, occurred_at=now))

    def cancel(self, now: datetime, reason: str | None = None) -> None:
        if self.status is BookingStatus.CANCELLED:
            raise InvalidStatusTransition(self.status, BookingStatus.CANCELLED)
        if self.slot.start_at <= now:
            raise BookingAlreadyStarted()
        self.status = BookingStatus.CANCELLED
        self.cancellation_reason = reason
        self.updated_at = now
        self._record(BookingCancelled.from_booking(self, occurred_at=now))

    def pull_events(self) -> list[DomainEvent]:
        """Devuelve y limpia los eventos pendientes de publicar."""
        events, self._events = self._events, []
        return events

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)
