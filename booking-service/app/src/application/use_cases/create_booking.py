from collections.abc import Callable
from datetime import datetime

from app.src.application.dto import CreateBookingCommand
from app.src.application.exceptions import ResourceNotBookable, UserNotAllowed
from app.src.application.ports import BookingRepository, EventPublisher, ResourceCatalog, UserDirectory
from app.src.domain.entities.booking import Booking
from app.src.domain.services.availability import ensure_slot_is_available
from app.src.domain.value_objects import TimeSlot


class CreateBooking:
    def __init__(
        self,
        bookings: BookingRepository,
        users: UserDirectory,
        resources: ResourceCatalog,
        publisher: EventPublisher,
        clock: Callable[[], datetime],
    ) -> None:
        self._bookings = bookings
        self._users = users
        self._resources = resources
        self._publisher = publisher
        self._clock = clock

    def execute(self, command: CreateBookingCommand) -> Booking:
        user = self._users.get_user(command.user_id)
        if user is None or not user.is_active:
            raise UserNotAllowed(command.user_id)

        resource = self._resources.get_resource(command.resource_id)
        if resource is None or not resource.is_active:
            raise ResourceNotBookable(command.resource_id)

        booking = Booking.create(
            user_id=command.user_id,
            resource_id=command.resource_id,
            slot=TimeSlot(command.start_at, command.end_at),
            hourly_rate=resource.hourly_rate,
            now=self._clock(),
        )

        ensure_slot_is_available(booking, self._bookings.find_blocking_overlaps(booking.resource_id, booking.slot))
        self._bookings.add(booking)
        self._publisher.publish(booking.pull_events())
        return booking
