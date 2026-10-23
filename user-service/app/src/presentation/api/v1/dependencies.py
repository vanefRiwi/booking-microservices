"""Composición: único lugar donde Presentation conoce las implementaciones concretas."""

import datetime
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.src.application.ports import UserRepository
from app.src.application.use_cases.users import DeactivateUser, GetUser, ListUsers, RegisterUser
from app.src.infrastructure.database import get_session
from app.src.infrastructure.persistence.sqlmodel_user_repository import SQLModelUserRepository


def get_today() -> Callable[[], datetime.date]:
    return lambda: datetime.datetime.now(datetime.UTC).date()


def get_user_repository(session: Annotated[Session, Depends(get_session)]) -> UserRepository:
    return SQLModelUserRepository(session)


Repository = Annotated[UserRepository, Depends(get_user_repository)]


def register_user_use_case(
    users: Repository, today: Annotated[Callable[[], datetime.date], Depends(get_today)]
) -> RegisterUser:
    return RegisterUser(users, today)


def get_user_use_case(users: Repository) -> GetUser:
    return GetUser(users)


def list_users_use_case(users: Repository) -> ListUsers:
    return ListUsers(users)


def deactivate_user_use_case(users: Repository) -> DeactivateUser:
    return DeactivateUser(users)
