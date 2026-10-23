from uuid import UUID


class ApplicationError(Exception):
    pass


class UserNotFound(ApplicationError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"El usuario {user_id} no existe.")


class EmailAlreadyRegistered(ApplicationError):
    def __init__(self, email: str) -> None:
        super().__init__(f"Ya existe un usuario con el email {email}.")
