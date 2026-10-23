from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.src.infrastructure.config import get_settings


@lru_cache
def get_engine() -> Engine:
    url = get_settings().database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)


def create_local_schema() -> None:
    """Solo para SQLite local. En Postgres (Neon) el esquema lo maneja Alembic."""
    engine = get_engine()
    if engine.dialect.name == "sqlite":
        from app.src.infrastructure.persistence import models  # noqa: F401  registra la tabla

        SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
