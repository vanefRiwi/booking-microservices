"""Entidad Resource en Python puro. resources-service es el dueño del catálogo:
bookings-service solo consulta id, is_active y hourly_rate por REST."""

import uuid
from dataclasses import dataclass, field
from datetime import time
from decimal import Decimal
from enum import StrEnum


class ResourceKind(StrEnum):
    ROOM = "ROOM"
    EQUIPMENT = "EQUIPMENT"
    DESK = "DESK"


class InvalidResource(Exception):
    pass


@dataclass(frozen=True)
class AvailabilityWindow:
    """Horario en que el recurso se puede reservar (p. ej. lunes 07:00-19:00).
    Es disponibilidad operativa; la ocupación (reservas) es de bookings-service."""

    weekday: int  # 0 = lunes ... 6 = domingo
    opens_at: time
    closes_at: time

    def __post_init__(self) -> None:
        if not 0 <= self.weekday <= 6:
            raise InvalidResource("El día de la semana debe estar entre 0 y 6.")
        if self.closes_at <= self.opens_at:
            raise InvalidResource("La hora de cierre debe ser posterior a la de apertura.")


@dataclass
class Resource:
    id: uuid.UUID
    name: str
    kind: ResourceKind
    capacity: int
    hourly_rate: Decimal
    features: list[str] = field(default_factory=list)
    availability: list[AvailabilityWindow] = field(default_factory=list)
    is_active: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidResource("El nombre es obligatorio.")
        if self.capacity < 1:
            raise InvalidResource("La capacidad debe ser al menos 1.")
        if self.hourly_rate < 0:
            raise InvalidResource("La tarifa no puede ser negativa.")

    def deactivate(self) -> None:
        self.is_active = False
