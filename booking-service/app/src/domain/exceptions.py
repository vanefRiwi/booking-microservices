"""Excepciones de dominio: expresan reglas de negocio violadas, no errores HTTP."""

from uuid import UUID


class DomainError(Exception):
    """Base de todos los errores de reglas de negocio."""


class InvalidTimeSlot(DomainError):
    pass


class BookingInThePast(DomainError):
    def __init__(self) -> None:
        super().__init__("No se puede reservar un horario que ya empezó o pasó.")


class InvalidStatusTransition(DomainError):
    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"No se puede pasar una reserva de {current} a {target}.")


class BookingAlreadyStarted(DomainError):
    def __init__(self) -> None:
        super().__init__("No se puede cancelar una reserva que ya empezó.")


class BookingConflict(DomainError):
    """Regla clave del sistema: un recurso no puede tener dos reservas activas solapadas."""

    def __init__(self, resource_id: UUID, conflicting_ids: list[UUID] | None = None) -> None:
        self.resource_id = resource_id
        self.conflicting_ids = conflicting_ids or []
        super().__init__(f"El recurso {resource_id} ya está reservado en ese horario.")
