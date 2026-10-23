"""El router solo adapta HTTP -> caso de uso. No contiene reglas de negocio."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.src.application.dto import CancelBookingCommand, CreateBookingCommand
from app.src.application.use_cases.create_booking import CreateBooking
from app.src.application.use_cases.manage_booking import CancelBooking, ConfirmBooking, GetBooking, ListBookings
from app.src.domain.value_objects import BookingStatus
from app.src.presentation.api.v1.dependencies import (
    cancel_booking_use_case,
    confirm_booking_use_case,
    create_booking_use_case,
    get_booking_use_case,
    list_bookings_use_case,
)
from app.src.presentation.api.v1.schemas import (
    BookingResponse,
    CancelBookingRequest,
    CreateBookingRequest,
    ErrorResponse,
)

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse, "description": "El recurso ya está reservado en ese horario"}},
)
def create_booking(
    body: CreateBookingRequest,
    use_case: Annotated[CreateBooking, Depends(create_booking_use_case)],
) -> BookingResponse:
    booking = use_case.execute(
        CreateBookingCommand(
            user_id=body.user_id,
            resource_id=body.resource_id,
            start_at=body.start_at,
            end_at=body.end_at,
        )
    )
    return BookingResponse.from_entity(booking)


@router.get("")
def list_bookings(
    use_case: Annotated[ListBookings, Depends(list_bookings_use_case)],
    resource_id: UUID | None = None,
    user_id: UUID | None = None,
    status: BookingStatus | None = None,
) -> list[BookingResponse]:
    bookings = use_case.execute(resource_id=resource_id, user_id=user_id, status=status)
    return [BookingResponse.from_entity(booking) for booking in bookings]


@router.get("/{booking_id}", responses={404: {"model": ErrorResponse}})
def get_booking(
    booking_id: UUID,
    use_case: Annotated[GetBooking, Depends(get_booking_use_case)],
) -> BookingResponse:
    return BookingResponse.from_entity(use_case.execute(booking_id))


@router.post("/{booking_id}/confirm", responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}})
def confirm_booking(
    booking_id: UUID,
    use_case: Annotated[ConfirmBooking, Depends(confirm_booking_use_case)],
) -> BookingResponse:
    return BookingResponse.from_entity(use_case.execute(booking_id))


@router.post("/{booking_id}/cancel", responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}})
def cancel_booking(
    booking_id: UUID,
    use_case: Annotated[CancelBooking, Depends(cancel_booking_use_case)],
    body: CancelBookingRequest | None = None,
) -> BookingResponse:
    reason = body.reason if body else None
    return BookingResponse.from_entity(use_case.execute(CancelBookingCommand(booking_id, reason)))
