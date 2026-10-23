"""Contratos (puertos) que Application necesita. Infrastructure los implementa:
las dependencias apuntan hacia el núcleo, nunca al revés."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.src.domain.entities.booking import Booking
from app.src.domain.events import DomainEvent
from app.src.domain.value_objects import BookingStatus, TimeSlot


class BookingRepository(ABC):
    @abstractmethod
    def add(self, booking: Booking) -> None:
        """Persiste una reserva nueva. Debe lanzar BookingConflict si la base de datos
        detecta un solapamiento que se coló por una carrera."""

    @abstractmethod
    def update(self, booking: Booking) -> None: ...

    @abstractmethod
    def get(self, booking_id: UUID) -> Booking | None: ...

    @abstractmethod
    def list(
        self,
        *,
        resource_id: UUID | None = None,
        user_id: UUID | None = None,
        status: BookingStatus | None = None,
    ) -> Sequence[Booking]: ...

    @abstractmethod
    def find_blocking_overlaps(self, resource_id: UUID, slot: TimeSlot) -> Sequence[Booking]:
        """Reservas PENDING/CONFIRMED del recurso que se solapan con el horario."""


@dataclass(frozen=True)
class UserInfo:
    """Lo único que bookings necesita saber de un usuario (no es el modelo de users-service)."""

    id: UUID
    is_active: bool


@dataclass(frozen=True)
class ResourceInfo:
    """Lo único que bookings necesita saber de un recurso (no es el modelo de resources-service)."""

    id: UUID
    is_active: bool
    hourly_rate: Decimal


class UserDirectory(ABC):
    @abstractmethod
    def get_user(self, user_id: UUID) -> UserInfo | None: ...


class ResourceCatalog(ABC):
    @abstractmethod
    def get_resource(self, resource_id: UUID) -> ResourceInfo | None: ...


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, events: Sequence[DomainEvent]) -> None: ...
