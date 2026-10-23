"""Composición: único lugar donde Presentation conoce las implementaciones concretas.
Las pruebas sustituyen estos proveedores con app.dependency_overrides."""

from collections.abc import Callable
from datetime import UTC, datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.src.application.ports import BookingRepository, EventPublisher, ResourceCatalog, UserDirectory
from app.src.application.use_cases.create_booking import CreateBooking
from app.src.application.use_cases.manage_booking import CancelBooking, ConfirmBooking, GetBooking, ListBookings
from app.src.infrastructure.clients.http_clients import (
    DevModeResourceCatalog,
    DevModeUserDirectory,
    HttpResourceCatalog,
    HttpUserDirectory,
)
from app.src.infrastructure.config import get_settings
from app.src.infrastructure.database import get_session
from app.src.infrastructure.messaging.event_publishers import LoggingEventPublisher
from app.src.infrastructure.persistence.sqlmodel_booking_repository import SQLModelBookingRepository


def get_clock() -> Callable[[], datetime]:
    return lambda: datetime.now(UTC)


def get_booking_repository(session: Annotated[Session, Depends(get_session)]) -> BookingRepository:
    return SQLModelBookingRepository(session)


def get_user_directory() -> UserDirectory:
    settings = get_settings()
    if settings.users_service_url:
        return HttpUserDirectory(settings.users_service_url, settings.http_timeout_seconds)
    return DevModeUserDirectory()


def get_resource_catalog() -> ResourceCatalog:
    settings = get_settings()
    if settings.resources_service_url:
        return HttpResourceCatalog(settings.resources_service_url, settings.http_timeout_seconds)
    return DevModeResourceCatalog(settings.dev_default_hourly_rate)


@lru_cache
def get_event_publisher() -> EventPublisher:
    return LoggingEventPublisher()


Repository = Annotated[BookingRepository, Depends(get_booking_repository)]
Publisher = Annotated[EventPublisher, Depends(get_event_publisher)]
Clock = Annotated[Callable[[], datetime], Depends(get_clock)]


def create_booking_use_case(
    bookings: Repository,
    users: Annotated[UserDirectory, Depends(get_user_directory)],
    resources: Annotated[ResourceCatalog, Depends(get_resource_catalog)],
    publisher: Publisher,
    clock: Clock,
) -> CreateBooking:
    return CreateBooking(bookings, users, resources, publisher, clock)


def get_booking_use_case(bookings: Repository) -> GetBooking:
    return GetBooking(bookings)


def list_bookings_use_case(bookings: Repository) -> ListBookings:
    return ListBookings(bookings)


def confirm_booking_use_case(bookings: Repository, publisher: Publisher, clock: Clock) -> ConfirmBooking:
    return ConfirmBooking(bookings, publisher, clock)


def cancel_booking_use_case(bookings: Repository, publisher: Publisher, clock: Clock) -> CancelBooking:
    return CancelBooking(bookings, publisher, clock)
