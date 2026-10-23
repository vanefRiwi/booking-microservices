import os
from dataclasses import dataclass
from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()


def normalize_database_url(url: str) -> str:
    """Neon entrega URLs `postgresql://`; usamos el driver psycopg 3 instalado."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


@dataclass(frozen=True)
class Settings:
    database_url: str
    users_service_url: str | None
    resources_service_url: str | None
    http_timeout_seconds: float
    dev_default_hourly_rate: Decimal


def get_settings() -> Settings:
    return Settings(
        database_url=normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./bookings.db")),
        users_service_url=os.getenv("USERS_SERVICE_URL") or None,
        resources_service_url=os.getenv("RESOURCES_SERVICE_URL") or None,
        http_timeout_seconds=float(os.getenv("HTTP_TIMEOUT_SECONDS", "3")),
        dev_default_hourly_rate=Decimal(os.getenv("DEV_DEFAULT_HOURLY_RATE", "0")),
    )
