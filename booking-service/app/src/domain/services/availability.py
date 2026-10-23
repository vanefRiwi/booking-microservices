from collections.abc import Iterable

from app.src.domain.entities.booking import Booking
from app.src.domain.exceptions import BookingConflict


def ensure_slot_is_available(candidate: Booking, existing: Iterable[Booking]) -> None:
    """Regla clave: evitar conflictos de disponibilidad.

    Falla si alguna reserva activa (PENDING o CONFIRMED) del mismo recurso se solapa
    con la candidata. La base de datos repite la regla con una restricción EXCLUDE
    para cubrir las carreras entre peticiones concurrentes.
    """
    conflicting = [booking.id for booking in existing if candidate.conflicts_with(booking)]
    if conflicting:
        raise BookingConflict(candidate.resource_id, conflicting)
