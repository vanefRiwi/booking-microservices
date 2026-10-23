from uuid import uuid4

import pytest

from app.src.application.dto import CancelBookingCommand, CreateBookingCommand
from app.src.application.exceptions import BookingNotFound, ResourceNotBookable, UserNotAllowed
from app.src.application.use_cases.create_booking import CreateBooking
from app.src.application.use_cases.manage_booking import CancelBooking, ConfirmBooking
from app.src.domain.exceptions import BookingConflict
from app.src.domain.value_objects import BookingStatus
from app.src.infrastructure.messaging.event_publishers import InMemoryEventPublisher
from tests.fakes import NOW, FakeResourceCatalog, FakeUserDirectory, InMemoryBookingRepository, at


@pytest.fixture
def ctx():
    class Ctx:
        repo = InMemoryBookingRepository()
        users = FakeUserDirectory()
        resources = FakeResourceCatalog()
        publisher = InMemoryEventPublisher()

        def clock(self):
            return NOW

    c = Ctx()
    c.create = CreateBooking(c.repo, c.users, c.resources, c.publisher, c.clock)
    c.confirm = ConfirmBooking(c.repo, c.publisher, c.clock)
    c.cancel = CancelBooking(c.repo, c.publisher, c.clock)
    return c


def command(ctx, start, end, user_id=None, resource_id=None):
    return CreateBookingCommand(
        user_id=user_id or ctx.users.register(),
        resource_id=resource_id or ctx.resources.register(),
        start_at=start,
        end_at=end,
    )


def test_creates_pending_booking_and_publishes_event(ctx):
    booking = ctx.create.execute(command(ctx, at(10), at(12)))

    assert ctx.repo.get(booking.id) is booking
    assert booking.status is BookingStatus.PENDING
    [message] = ctx.publisher.messages
    assert message["event_type"] == "booking.created"
    assert message["data"]["booking_id"] == str(booking.id)
    assert message["data"]["total_amount"] == "100000.00"


def test_rejects_overlapping_booking_and_does_not_publish(ctx):
    resource_id = ctx.resources.register()
    ctx.create.execute(command(ctx, at(10), at(12), resource_id=resource_id))

    with pytest.raises(BookingConflict):
        ctx.create.execute(command(ctx, at(11), at(13), resource_id=resource_id))
    assert len(ctx.repo.items) == 1
    assert len(ctx.publisher.messages) == 1


def test_cancelling_frees_the_slot(ctx):
    resource_id = ctx.resources.register()
    first = ctx.create.execute(command(ctx, at(10), at(12), resource_id=resource_id))
    ctx.cancel.execute(CancelBookingCommand(first.id, "ya no la necesito"))

    second = ctx.create.execute(command(ctx, at(10), at(12), resource_id=resource_id))
    assert second.status is BookingStatus.PENDING
    assert [m["event_type"] for m in ctx.publisher.messages] == [
        "booking.created",
        "booking.cancelled",
        "booking.created",
    ]


def test_confirm_publishes_booking_confirmed(ctx):
    booking = ctx.create.execute(command(ctx, at(10), at(12)))
    ctx.confirm.execute(booking.id)
    assert ctx.repo.get(booking.id).status is BookingStatus.CONFIRMED
    assert ctx.publisher.messages[-1]["event_type"] == "booking.confirmed"


def test_rejects_inactive_or_unknown_user(ctx):
    with pytest.raises(UserNotAllowed):
        ctx.create.execute(command(ctx, at(10), at(12), user_id=ctx.users.register(is_active=False)))
    with pytest.raises(UserNotAllowed):
        ctx.create.execute(command(ctx, at(10), at(12), user_id=uuid4()))


def test_rejects_inactive_or_unknown_resource(ctx):
    with pytest.raises(ResourceNotBookable):
        ctx.create.execute(command(ctx, at(10), at(12), resource_id=ctx.resources.register(is_active=False)))
    with pytest.raises(ResourceNotBookable):
        ctx.create.execute(command(ctx, at(10), at(12), resource_id=uuid4()))


def test_unknown_booking(ctx):
    with pytest.raises(BookingNotFound):
        ctx.confirm.execute(uuid4())
