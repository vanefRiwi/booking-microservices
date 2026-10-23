"""Contratos que Application necesita; Infrastructure los implementa."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.src.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> None: ...

    @abstractmethod
    def update(self, user: User) -> None: ...

    @abstractmethod
    def get(self, user_id: UUID) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def list(self, *, only_active: bool = False) -> Sequence[User]: ...
