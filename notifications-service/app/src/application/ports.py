from abc import ABC, abstractmethod
from uuid import UUID

from app.src.domain.entities.notification import Notification


class NotificationRepository(ABC):
    @abstractmethod
    def add(self, notification: Notification) -> None: ...

    @abstractmethod
    def exists_for_event(self, source_event_id: UUID) -> bool: ...


class RecipientDirectory(ABC):
    """Obtiene el email del usuario desde users-service (REST)."""

    @abstractmethod
    def get_email(self, user_id: UUID) -> str | None: ...


class NotificationSender(ABC):
    @abstractmethod
    def send(self, to: str, template: str, data: dict) -> None: ...
