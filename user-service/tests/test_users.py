import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.src.domain.entities.user import User
from app.src.domain.exceptions import InvalidUserData
from app.src.infrastructure.database import get_session
from app.src.infrastructure.persistence import models  # noqa: F401
from app.src.presentation.api.v1 import dependencies as deps
from main import app

TODAY = datetime.date(2026, 10, 23)


def test_domain_normalizes_and_validates():
    user = User.register(
        name="  Ana  ",
        email="ANA@Mail.com",
        identification_type="cc",
        identification_number="123",
        birth_date=datetime.date(2000, 1, 1),
        today=TODAY,
    )
    assert (user.name, user.email, user.identification_type) == ("Ana", "ana@mail.com", "CC")
    with pytest.raises(InvalidUserData):
        User.register(
            name="Ana",
            email="a@b.co",
            identification_type="CC",
            identification_number="1",
            birth_date=TODAY,
            today=TODAY,
        )


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides = {get_session: session_override, deps.get_today: lambda: (lambda: TODAY)}
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}


def test_user_api_flow(client):
    body = {
        "name": "Vane",
        "email": "vane@example.com",
        "identification_type": "CC",
        "identification_number": "1001",
        "birth_date": "1999-05-10",
    }
    created = client.post("/api/v1/users", json=body)
    assert created.status_code == 201, created.text
    user = created.json()
    assert user["is_active"] is True

    assert client.post("/api/v1/users", json=body | {"email": "VANE@example.com"}).status_code == 409
    assert client.get(f"/api/v1/users/{user['id']}").json()["email"] == "vane@example.com"

    deactivated = client.post(f"/api/v1/users/{user['id']}/deactivate")
    assert deactivated.json()["is_active"] is False
    assert client.post(f"/api/v1/users/{user['id']}/deactivate").status_code == 409
    assert client.get("/api/v1/users", params={"only_active": True}).json() == []

    assert client.get("/api/v1/users/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.post("/api/v1/users", json=body | {"email": "no-es-email"}).status_code == 422
