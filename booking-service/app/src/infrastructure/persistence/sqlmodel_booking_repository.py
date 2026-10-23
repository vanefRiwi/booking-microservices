from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, select

from app.src.application.ports import BookingRepository
from app.src.domain.entities.booking import Booking
from app.src.domain.exceptions import BookingConflict
from app.src.domain.value_objects import BLOCKING_STATUSES, BookingStatus, TimeSlot
from app.src.infrastructure.persistence.models import NO_OVERLAP_CONSTRAINT, BookingModel


def _aware(value: datetime) -> datetime:
    # SQLite no guarda la zona horaria; todo se almacena en UTC.
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def to_domain(row: BookingModel) -> Booking:
    return Booking(
        id=row.id,
        user_id=row.user_id,
        resource_id=row.resource_id,
        slot=TimeSlot(_aware(row.start_at), _aware(row.end_at)),
        status=BookingStatus(row.status),
        total_amount=row.total_amount,
        cancellation_reason=row.cancellation_reason,
        created_at=_aware(row.created_at),
        updated_at=_aware(row.updated_at),
    )


def to_row(booking: Booking) -> BookingModel:
    return BookingModel(
        id=booking.id,
        user_id=booking.user_id,
        resource_id=booking.resource_id,
        start_at=booking.slot.start_at.astimezone(UTC),
        end_at=booking.slot.end_at.astimezone(UTC),
        status=booking.status.value,
        total_amount=booking.total_amount,
        cancellation_reason=booking.cancellation_reason,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )


class SQLModelBookingRepository(BookingRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, booking: Booking) -> None:
        self._session.add(to_row(booking))
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            if NO_OVERLAP_CONSTRAINT in str(error.orig):
                raise BookingConflict(booking.resource_id) from error
            raise

    def update(self, booking: Booking) -> None:
        self._session.merge(to_row(booking))
        self._session.commit()

    def get(self, booking_id: UUID) -> Booking | None:
        row = self._session.get(BookingModel, booking_id)
        return to_domain(row) if row else None

    def list(
        self,
        *,
        resource_id: UUID | None = None,
        user_id: UUID | None = None,
        status: BookingStatus | None = None,
    ) -> Sequence[Booking]:
        query = select(BookingModel)
        if resource_id:
            query = query.where(BookingModel.resource_id == resource_id)
        if user_id:
            query = query.where(BookingModel.user_id == user_id)
        if status:
            query = query.where(BookingModel.status == status.value)
        query = query.order_by(col(BookingModel.start_at))
        return [to_domain(row) for row in self._session.exec(query)]

    def find_blocking_overlaps(self, resource_id: UUID, slot: TimeSlot) -> Sequence[Booking]:
        query = select(BookingModel).where(
            BookingModel.resource_id == resource_id,
            col(BookingModel.status).in_([status.value for status in BLOCKING_STATUSES]),
            col(BookingModel.start_at) < slot.end_at.astimezone(UTC),
            col(BookingModel.end_at) > slot.start_at.astimezone(UTC),
        )
        return [to_domain(row) for row in self._session.exec(query)]
