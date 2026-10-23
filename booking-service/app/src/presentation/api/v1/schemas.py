from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field

from app.src.domain.entities.booking import Booking
from app.src.domain.value_objects import BookingStatus


class CreateBookingRequest(BaseModel):
    user_id: UUID
    resource_id: UUID
    start_at: AwareDatetime = Field(examples=["2026-11-03T09:00:00-05:00"])
    end_at: AwareDatetime = Field(examples=["2026-11-03T11:00:00-05:00"])


class CancelBookingRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    resource_id: UUID
    start_at: datetime
    end_at: datetime
    status: BookingStatus
    total_amount: Decimal
    cancellation_reason: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, booking: Booking) -> "BookingResponse":
        return cls(
            id=booking.id,
            user_id=booking.user_id,
            resource_id=booking.resource_id,
            start_at=booking.slot.start_at,
            end_at=booking.slot.end_at,
            status=booking.status,
            total_amount=booking.total_amount,
            cancellation_reason=booking.cancellation_reason,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )


class ErrorResponse(BaseModel):
    detail: str
