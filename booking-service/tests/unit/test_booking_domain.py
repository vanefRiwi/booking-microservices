from decimal import Decimal
from uuid import uuid4

import pytest

from app.src.domain.entities.booking import Booking
from app.src.domain.exceptions import (
    BookingAlreadyStarted,
    BookingConflict,
    BookingInThePast,
    InvalidStatusTransition,
    InvalidTimeSlot,
)
from app.src.domain.services.availability import ensure_slot_is_available
from app.src.domain.value_objects import BookingStatus, TimeSlot
from tests.fakes import NOW, at


def new_booking(start, end, resource_id=None, rate="40000") -> Booking:
    return Booking.create(
        user_id=uuid4(),
        resource_id=resource_id or uuid4(),
        slot=TimeSlot(start, end),
        hourly_rate=Decimal(rate),
        now=NOW,
    )


class TestTimeSlot:
    def test_end_must_be_after_start(self):
        with pytest.raises(InvalidTimeSlot):
            TimeSlot(at(10), at(10))

    def test_requires_timezone(self):
        with pytest.raises(InvalidTimeSlot):
            TimeSlot(at(9).replace(tzinfo=None), at(10).replace(tzinfo=None))

    @pytest.mark.parametrize(
        ("other_start", "other_end", "expected"),
        [
            (9, 10, False),  # termina justo cuando empieza: no choca
            (12, 13, False),  # empieza justo cuando termina: no choca
            (9, 11, True),
            (11, 13, True),
            (10, 12, True),
            (10.5, 11.5, True),  # contenida
            (8, 14, True),  # la contiene
        ],
    )
    def test_overlaps_uses_half_open_intervals(self, other_start, other_end, expected):
        def hour(value):
            return at(int(value), 30 if value % 1 else 0)

        slot = TimeSlot(at(10), at(12))
        assert slot.overlaps(TimeSlot(hour(other_start), hour(other_end))) is expected


class TestBookingLifecycle:
    def test_new_booking_is_pending_with_frozen_price_and_event(self):
        booking = new_booking(at(10), at(11, 30), rate="40000")

        assert booking.status is BookingStatus.PENDING
        assert booking.total_amount == Decimal("60000.00")
        assert [event.name for event in booking.pull_events()] == ["booking.created"]
        assert booking.pull_events() == []

    def test_cannot_book_in_the_past(self):
        with pytest.raises(BookingInThePast):
            new_booking(at(9, days=-1), at(10, days=-1))

    def test_confirm_only_from_pending(self):
        booking = new_booking(at(10), at(11))
        booking.confirm(NOW)
        assert booking.status is BookingStatus.CONFIRMED
        with pytest.raises(InvalidStatusTransition):
            booking.confirm(NOW)

    def test_cancel_releases_the_slot(self):
        booking = new_booking(at(10), at(11))
        booking.cancel(NOW, "cambio de planes")
        assert booking.status is BookingStatus.CANCELLED
        assert not booking.blocks_availability
        with pytest.raises(InvalidStatusTransition):
            booking.cancel(NOW)

    def test_cannot_cancel_once_started(self):
        booking = new_booking(at(10), at(11))
        with pytest.raises(BookingAlreadyStarted):
            booking.cancel(at(10, 15))


class TestAvailabilityRule:
    def test_overlapping_active_booking_on_same_resource_conflicts(self):
        resource_id = uuid4()
        existing = new_booking(at(10), at(12), resource_id)
        candidate = new_booking(at(11), at(13), resource_id)

        with pytest.raises(BookingConflict) as error:
            ensure_slot_is_available(candidate, [existing])
        assert error.value.conflicting_ids == [existing.id]

    def test_confirmed_bookings_also_block(self):
        resource_id = uuid4()
        existing = new_booking(at(10), at(12), resource_id)
        existing.confirm(NOW)
        with pytest.raises(BookingConflict):
            ensure_slot_is_available(new_booking(at(9), at(10, 30), resource_id), [existing])

    def test_cancelled_booking_does_not_block(self):
        resource_id = uuid4()
        existing = new_booking(at(10), at(12), resource_id)
        existing.cancel(NOW)
        ensure_slot_is_available(new_booking(at(10), at(12), resource_id), [existing])

    def test_other_resource_or_back_to_back_does_not_conflict(self):
        resource_id = uuid4()
        existing = new_booking(at(10), at(12), resource_id)
        ensure_slot_is_available(new_booking(at(10), at(12)), [existing])
        ensure_slot_is_available(new_booking(at(12), at(13), resource_id), [existing])
