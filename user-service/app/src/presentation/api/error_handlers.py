"""Traduce errores de dominio/aplicación a respuestas HTTP. El dominio no sabe de HTTP."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.src.application.exceptions import EmailAlreadyRegistered, UserNotFound
from app.src.domain.exceptions import DomainError, UserAlreadyInactive

STATUS_BY_ERROR: list[tuple[type[Exception], int]] = [
    (UserNotFound, status.HTTP_404_NOT_FOUND),
    (EmailAlreadyRegistered, status.HTTP_409_CONFLICT),
    (UserAlreadyInactive, status.HTTP_409_CONFLICT),
    (DomainError, status.HTTP_422_UNPROCESSABLE_CONTENT),
]


def register_error_handlers(app: FastAPI) -> None:
    for error_type, status_code in STATUS_BY_ERROR:

        def handler(_: Request, error: Exception, code: int = status_code) -> JSONResponse:
            return JSONResponse(status_code=code, content={"detail": str(error)})

        app.add_exception_handler(error_type, handler)
