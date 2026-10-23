from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.src.infrastructure.database import get_session
from app.src.infrastructure.messaging.event_publishers import InMemoryEventPublisher
from app.src.infrastructure.persistence import models  # noqa: F401
from app.src.presentation.api.v1 import dependencies as deps
from main import app
from tests.fakes import NOW, FakeResourceCatalog, FakeUserDirectory, at


@pytest.fixture
def env():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def session_override():
        with Session(engine) as session:
            yield session

    users, resources, publisher = FakeUserDirectory(), FakeResourceCatalog(), InMemoryEventPublisher()
    app.dependency_overrides = {
        get_session: session_override,
        deps.get_user_directory: lambda: users,
        deps.get_resource_catalog: lambda: resources,
        deps.get_event_publisher: lambda: publisher,
        deps.get_clock: lambda: (lambda: NOW),
    }
    with TestClient(app) as client:
        yield client, users, resources, publisher
    app.dependency_overrides = {}


def payload(users, resources, start, end, resource_id=None):
    return {
        "user_id": str(users.register()),
        "resource_id": str(resource_id or resources.register()),
        "start_at": start.isoformat(),
        "end_at": end.isoformat(),
    }


def test_full_booking_flow(env):
    client, users, resources, publisher = env
    resource_id = resources.register(hourly_rate="30000")

    created = client.post("/api/v1/bookings", json=payload(users, resources, at(10), at(12), resource_id))
    assert created.status_code == 201, created.text
    booking = created.json()
    assert booking["status"] == "PENDING"
    assert booking["total_amount"] == "60000.00"

    conflict = client.post("/api/v1/bookings", json=payload(users, resources, at(11), at(13), resource_id))
    assert conflict.status_code == 409
    assert "ya está reservado" in conflict.json()["detail"]

    back_to_back = client.post("/api/v1/bookings", json=payload(users, resources, at(12), at(13), resource_id))
    assert back_to_back.status_code == 201

    confirmed = client.post(f"/api/v1/bookings/{booking['id']}/confirm")
    assert confirmed.json()["status"] == "CONFIRMED"

    cancelled = client.post(f"/api/v1/bookings/{booking['id']}/cancel", json={"reason": "reunión movida"})
    assert cancelled.json()["status"] == "CANCELLED"

    rebooked = client.post("/api/v1/bookings", json=payload(users, resources, at(11), at(12), resource_id))
    assert rebooked.status_code == 201

    listed = client.get("/api/v1/bookings", params={"resource_id": str(resource_id), "status": "PENDING"})
    assert {b["start_at"][11:16] for b in listed.json()} == {"11:00", "12:00"}
    assert [m["event_type"] for m in publisher.messages] == [
        "booking.created",
        "booking.created",
        "booking.confirmed",
        "booking.cancelled",
        "booking.created",
    ]


def test_validation_and_errors(env):
    client, users, resources, _ = env

    naive = payload(users, resources, at(10), at(11)) | {"start_at": "2026-11-03T10:00:00"}
    assert client.post("/api/v1/bookings", json=naive).status_code == 422

    reversed_slot = client.post("/api/v1/bookings", json=payload(users, resources, at(11), at(10)))
    assert reversed_slot.status_code == 422

    past = client.post("/api/v1/bookings", json=payload(users, resources, at(9, days=-1), at(10, days=-1)))
    assert past.status_code == 422

    unknown_resource = payload(users, resources, at(10), at(11)) | {"resource_id": str(uuid4())}
    assert client.post("/api/v1/bookings", json=unknown_resource).status_code == 422

    assert client.get(f"/api/v1/bookings/{uuid4()}").status_code == 404
    assert client.get("/health").json()["status"] == "ok"
