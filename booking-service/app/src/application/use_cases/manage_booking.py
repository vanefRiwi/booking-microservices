from collections.abc import Callable, Sequence
from datetime import datetime
from uuid import UUID

from app.src.application.dto import CancelBookingCommand
from app.src.application.exceptions import BookingNotFound
from app.src.application.ports import BookingRepository, EventPublisher
from app.src.domain.entities.booking import Booking
from app.src.domain.value_objects import BookingStatus


class GetBooking:
    def __init__(self, bookings: BookingRepository) -> None:
        self._bookings = bookings

    def execute(self, booking_id: UUID) -> Booking:
        booking = self._bookings.get(booking_id)
        if booking is None:
            raise BookingNotFound(booking_id)
        return booking


class ListBookings:
    def __init__(self, bookings: BookingRepository) -> None:
        self._bookings = bookings

    def execute(
        self,
        *,
        resource_id: UUID | None = None,
        user_id: UUID | None = None,
        status: BookingStatus | None = None,
    ) -> Sequence[Booking]:
        return self._bookings.list(resource_id=resource_id, user_id=user_id, status=status)


class ConfirmBooking:
    """Hoy lo dispara un endpoint interno; cuando llegue la sesión de mensajería
    lo invocará el consumidor del evento payment.succeeded sin cambiar este código."""

    def __init__(self, bookings: BookingRepository, publisher: EventPublisher, clock: Callable[[], datetime]) -> None:
        self._bookings = bookings
        self._publisher = publisher
        self._clock = clock

    def execute(self, booking_id: UUID) -> Booking:
        booking = GetBooking(self._bookings).execute(booking_id)
        booking.confirm(self._clock())
        self._bookings.update(booking)
        self._publisher.publish(booking.pull_events())
        return booking


class CancelBooking:
    def __init__(self, bookings: BookingRepository, publisher: EventPublisher, clock: Callable[[], datetime]) -> None:
        self._bookings = bookings
        self._publisher = publisher
        self._clock = clock

    def execute(self, command: CancelBookingCommand) -> Booking:
        booking = GetBooking(self._bookings).execute(command.booking_id)
        booking.cancel(self._clock(), command.reason)
        self._bookings.update(booking)
        self._publisher.publish(booking.pull_events())
        return booking
