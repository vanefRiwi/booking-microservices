from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from sqlmodel import SQLModel

from dotenv import load_dotenv

load_dotenv()

from app.src.infrastructure.config import normalize_database_url

# import the models to ensure they are registered with SQLAlchemy's metadata
from app.src.infrastructure.persistence.models import BookingModel  # noqa: F401

# Tabla de versiones propia: así cada servicio lleva su historial de migraciones
# aunque en desarrollo compartan la misma base de Neon.
VERSION_TABLE = "alembic_version_bookings"

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set.")
    return normalize_database_url(database_url)


def include_object(object, name, type_, reflected, compare_to):
    # Solo las tablas de este servicio (prefijo bkg_)
    if type_ == "table":
        return name.startswith("bkg_")
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (genera el SQL sin conectarse)."""
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table=VERSION_TABLE,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {"sqlalchemy.url": get_database_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=VERSION_TABLE,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
