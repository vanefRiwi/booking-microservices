"""Traduce errores de dominio/aplicación a respuestas HTTP. El dominio no sabe de HTTP."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.src.application.exceptions import (
    BookingNotFound,
    DependencyUnavailable,
    ResourceNotBookable,
    UserNotAllowed,
)
from app.src.domain.exceptions import (
    BookingAlreadyStarted,
    BookingConflict,
    DomainError,
    InvalidStatusTransition,
)

STATUS_BY_ERROR: list[tuple[type[Exception], int]] = [
    (BookingNotFound, status.HTTP_404_NOT_FOUND),
    (BookingConflict, status.HTTP_409_CONFLICT),
    (InvalidStatusTransition, status.HTTP_409_CONFLICT),
    (BookingAlreadyStarted, status.HTTP_409_CONFLICT),
    (UserNotAllowed, status.HTTP_422_UNPROCESSABLE_CONTENT),
    (ResourceNotBookable, status.HTTP_422_UNPROCESSABLE_CONTENT),
    (DependencyUnavailable, status.HTTP_503_SERVICE_UNAVAILABLE),
    (DomainError, status.HTTP_422_UNPROCESSABLE_CONTENT),
]


def register_error_handlers(app: FastAPI) -> None:
    for error_type, status_code in STATUS_BY_ERROR:

        def handler(_: Request, error: Exception, code: int = status_code) -> JSONResponse:
            return JSONResponse(status_code=code, content={"detail": str(error)})

        app.add_exception_handler(error_type, handler)
