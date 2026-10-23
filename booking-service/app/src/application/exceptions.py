from uuid import UUID


class ApplicationError(Exception):
    pass


class BookingNotFound(ApplicationError):
    def __init__(self, booking_id: UUID) -> None:
        super().__init__(f"La reserva {booking_id} no existe.")


class UserNotAllowed(ApplicationError):
    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"El usuario {user_id} no existe o está inactivo.")


class ResourceNotBookable(ApplicationError):
    def __init__(self, resource_id: UUID) -> None:
        super().__init__(f"El recurso {resource_id} no existe o no está disponible para reservas.")


class DependencyUnavailable(ApplicationError):
    """Un servicio externo (users/resources) no respondió."""
