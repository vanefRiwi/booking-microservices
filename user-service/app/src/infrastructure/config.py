import os

from dotenv import load_dotenv

load_dotenv()


def normalize_database_url(url: str) -> str:
    """Neon entrega URLs `postgresql://`; usamos el driver psycopg 3 instalado."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


def get_database_url() -> str:
    return normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./users.db"))
