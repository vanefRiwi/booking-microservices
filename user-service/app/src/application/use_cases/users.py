import datetime
from collections.abc import Callable, Sequence
from uuid import UUID

from app.src.application.dto import RegisterUserCommand
from app.src.application.exceptions import EmailAlreadyRegistered, UserNotFound
from app.src.application.ports import UserRepository
from app.src.domain.entities.user import User


class RegisterUser:
    def __init__(self, users: UserRepository, today: Callable[[], datetime.date]) -> None:
        self._users = users
        self._today = today

    def execute(self, command: RegisterUserCommand) -> User:
        user = User.register(
            name=command.name,
            email=command.email,
            identification_type=command.identification_type,
            identification_number=command.identification_number,
            birth_date=command.birth_date,
            today=self._today(),
        )
        if self._users.get_by_email(user.email):
            raise EmailAlreadyRegistered(user.email)
        self._users.add(user)
        return user


class GetUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: UUID) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise UserNotFound(user_id)
        return user


class ListUsers:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, *, only_active: bool = False) -> Sequence[User]:
        return self._users.list(only_active=only_active)


class DeactivateUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: UUID) -> User:
        user = GetUser(self._users).execute(user_id)
        user.deactivate()
        self._users.update(user)
        return user
