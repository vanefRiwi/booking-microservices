from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from app.src.application.ports import (
    BookingRepository,
    ResourceCatalog,
    ResourceInfo,
    UserDirectory,
    UserInfo,
)
from app.src.domain.entities.booking import Booking
from app.src.domain.value_objects import BookingStatus, TimeSlot

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)


def at(hour: int, minute: int = 0, days: int = 1) -> datetime:
    """Hora del día siguiente a NOW (por defecto), en UTC."""
    return (NOW + timedelta(days=days)).replace(hour=hour, minute=minute)


class InMemoryBookingRepository(BookingRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Booking] = {}

    def add(self, booking: Booking) -> None:
        self.items[booking.id] = booking

    def update(self, booking: Booking) -> None:
        self.items[booking.id] = booking

    def get(self, booking_id: UUID) -> Booking | None:
        return self.items.get(booking_id)

    def list(self, *, resource_id=None, user_id=None, status: BookingStatus | None = None) -> Sequence[Booking]:
        return [
            b
            for b in self.items.values()
            if (resource_id is None or b.resource_id == resource_id)
            and (user_id is None or b.user_id == user_id)
            and (status is None or b.status == status)
        ]

    def find_blocking_overlaps(self, resource_id: UUID, slot: TimeSlot) -> Sequence[Booking]:
        return [
            b
            for b in self.items.values()
            if b.resource_id == resource_id and b.blocks_availability and b.slot.overlaps(slot)
        ]


class FakeUserDirectory(UserDirectory):
    def __init__(self) -> None:
        self.users: dict[UUID, UserInfo] = {}

    def register(self, is_active: bool = True) -> UUID:
        user_id = uuid4()
        self.users[user_id] = UserInfo(id=user_id, is_active=is_active)
        return user_id

    def get_user(self, user_id: UUID) -> UserInfo | None:
        return self.users.get(user_id)


class FakeResourceCatalog(ResourceCatalog):
    def __init__(self) -> None:
        self.resources: dict[UUID, ResourceInfo] = {}

    def register(self, is_active: bool = True, hourly_rate: str = "50000") -> UUID:
        resource_id = uuid4()
        self.resources[resource_id] = ResourceInfo(id=resource_id, is_active=is_active, hourly_rate=Decimal(hourly_rate))
        return resource_id

    def get_resource(self, resource_id: UUID) -> ResourceInfo | None:
        return self.resources.get(resource_id)
