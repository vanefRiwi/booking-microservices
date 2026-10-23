from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.src.domain.entities.resource import Resource


class ResourceRepository(ABC):
    @abstractmethod
    def add(self, resource: Resource) -> None: ...

    @abstractmethod
    def get(self, resource_id: UUID) -> Resource | None: ...

    @abstractmethod
    def list(self, *, only_active: bool = True) -> Sequence[Resource]: ...
