"""Verifica la restricción EXCLUDE de Postgres: la última línea de defensa contra
dos peticiones concurrentes que pasan la validación del caso de uso al mismo tiempo.

Ejecutar con una base vacía:  TEST_POSTGRES_URL=postgresql://... uv run pytest tests/integration
"""

import os
from decimal import Decimal
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from sqlmodel import Session, create_engine

from app.src.domain.entities.booking import Booking
from app.src.domain.exceptions import BookingConflict
from app.src.domain.value_objects import TimeSlot
from app.src.infrastructure.config import normalize_database_url
from app.src.infrastructure.persistence.sqlmodel_booking_repository import SQLModelBookingRepository
from tests.fakes import NOW, at

POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(not POSTGRES_URL, reason="TEST_POSTGRES_URL no configurada")


@pytest.fixture
def session(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", POSTGRES_URL)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    engine = create_engine(normalize_database_url(POSTGRES_URL))
    with Session(engine) as session:
        yield session
    command.downgrade(config, "base")
    engine.dispose()


def booking(resource_id, start, end) -> Booking:
    return Booking.create(
        user_id=uuid4(), resource_id=resource_id, slot=TimeSlot(start, end), hourly_rate=Decimal("1"), now=NOW
    )


def test_database_rejects_overlap_even_without_use_case_check(session):
    repo = SQLModelBookingRepository(session)
    resource_id = uuid4()
    repo.add(booking(resource_id, at(10), at(12)))
    repo.add(booking(resource_id, at(12), at(13)))  # contiguo: permitido
    repo.add(booking(uuid4(), at(10), at(12)))  # otro recurso: permitido

    with pytest.raises(BookingConflict):
        repo.add(booking(resource_id, at(11), at(12)))


def test_cancelled_bookings_do_not_block_in_database(session):
    repo = SQLModelBookingRepository(session)
    resource_id = uuid4()
    first = booking(resource_id, at(10), at(12))
    repo.add(first)
    first.cancel(NOW)
    repo.update(first)

    repo.add(booking(resource_id, at(10), at(12)))
    assert len(repo.find_blocking_overlaps(resource_id, TimeSlot(at(9), at(13)))) == 1
