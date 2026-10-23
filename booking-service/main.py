import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.src.infrastructure.database import create_local_schema
from app.src.presentation.api.error_handlers import register_error_handlers
from app.src.presentation.api.v1.bookings_router import router as bookings_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_local_schema()
    yield


app = FastAPI(
    title="bookings-service",
    description="Reglas de reserva, detección de conflictos y estados de las reservas.",
    version="0.1.0",
    lifespan=lifespan,
)
register_error_handlers(app)
app.include_router(bookings_router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "bookings-service"}
