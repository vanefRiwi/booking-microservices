"""Value objects del dominio de reservas. Python puro: sin FastAPI, SQLModel ni RabbitMQ."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum

from app.src.domain.exceptions import InvalidTimeSlot


class BookingStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

    @property
    def blocks_availability(self) -> bool:
        """Una reserva pendiente (esperando pago) o confirmada ocupa el recurso."""
        return self in BLOCKING_STATUSES


BLOCKING_STATUSES = frozenset({BookingStatus.PENDING, BookingStatus.CONFIRMED})


@dataclass(frozen=True)
class TimeSlot:
    """Intervalo semiabierto [start_at, end_at): una reserva que termina a las 10:00
    no choca con otra que empieza a las 10:00."""

    start_at: datetime
    end_at: datetime

    def __post_init__(self) -> None:
        if self.start_at.tzinfo is None or self.end_at.tzinfo is None:
            raise InvalidTimeSlot("Las fechas deben incluir zona horaria (ISO 8601 con offset).")
        if self.end_at <= self.start_at:
            raise InvalidTimeSlot("La hora de fin debe ser posterior a la hora de inicio.")

    @property
    def duration(self) -> timedelta:
        return self.end_at - self.start_at

    def overlaps(self, other: "TimeSlot") -> bool:
        return self.start_at < other.end_at and other.start_at < self.end_at
