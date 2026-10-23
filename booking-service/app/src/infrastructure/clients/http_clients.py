"""Adaptadores síncronos (HTTP/REST) hacia users-service y resources-service.
Solo leen los campos del contrato (docs/contracts/rest.md); ignoran el resto."""

import logging
from decimal import Decimal
from uuid import UUID

import httpx

from app.src.application.exceptions import DependencyUnavailable
from app.src.application.ports import ResourceCatalog, ResourceInfo, UserDirectory, UserInfo

logger = logging.getLogger(__name__)


def _get_json(base_url: str, path: str, timeout: float) -> dict | None:
    try:
        response = httpx.get(f"{base_url.rstrip('/')}{path}", timeout=timeout)
    except httpx.HTTPError as error:
        raise DependencyUnavailable(f"No se pudo contactar {base_url}: {error}") from error
    if response.status_code == 404:
        return None
    if response.is_error:
        raise DependencyUnavailable(f"{base_url} respondió {response.status_code}")
    return response.json()


class HttpUserDirectory(UserDirectory):
    def __init__(self, base_url: str, timeout: float) -> None:
        self._base_url = base_url
        self._timeout = timeout

    def get_user(self, user_id: UUID) -> UserInfo | None:
        data = _get_json(self._base_url, f"/api/v1/users/{user_id}", self._timeout)
        return UserInfo(id=UUID(data["id"]), is_active=data["is_active"]) if data else None


class HttpResourceCatalog(ResourceCatalog):
    def __init__(self, base_url: str, timeout: float) -> None:
        self._base_url = base_url
        self._timeout = timeout

    def get_resource(self, resource_id: UUID) -> ResourceInfo | None:
        data = _get_json(self._base_url, f"/api/v1/resources/{resource_id}", self._timeout)
        if not data:
            return None
        return ResourceInfo(
            id=UUID(data["id"]),
            is_active=data["is_active"],
            hourly_rate=Decimal(str(data["hourly_rate"])),
        )


class DevModeUserDirectory(UserDirectory):
    """Se usa solo si USERS_SERVICE_URL no está configurada, para poder ejecutar
    bookings-service de forma aislada mientras los demás servicios evolucionan."""

    def get_user(self, user_id: UUID) -> UserInfo | None:
        logger.warning("USERS_SERVICE_URL no configurada: se asume que el usuario %s existe", user_id)
        return UserInfo(id=user_id, is_active=True)


class DevModeResourceCatalog(ResourceCatalog):
    def __init__(self, hourly_rate: Decimal) -> None:
        self._hourly_rate = hourly_rate

    def get_resource(self, resource_id: UUID) -> ResourceInfo | None:
        logger.warning("RESOURCES_SERVICE_URL no configurada: se asume que el recurso %s existe", resource_id)
        return ResourceInfo(id=resource_id, is_active=True, hourly_rate=self._hourly_rate)
