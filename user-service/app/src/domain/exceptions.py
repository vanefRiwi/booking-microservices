"""Excepciones de dominio: reglas de negocio violadas, no errores HTTP."""


class DomainError(Exception):
    pass


class InvalidUserData(DomainError):
    pass


class UserAlreadyInactive(DomainError):
    def __init__(self) -> None:
        super().__init__("El usuario ya está inactivo.")
