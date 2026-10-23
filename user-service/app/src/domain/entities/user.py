"""Entidad User en Python puro: el dominio no conoce FastAPI ni SQLModel.
El modelo ORM vive en infrastructure/persistence/models.py."""

import datetime
import uuid
from dataclasses import dataclass

from app.src.domain.exceptions import InvalidUserData, UserAlreadyInactive


@dataclass
class User:
    id: uuid.UUID
    name: str
    email: str
    identification_type: str
    identification_number: str
    birth_date: datetime.date
    is_active: bool = True

    @classmethod
    def register(
        cls,
        *,
        name: str,
        email: str,
        identification_type: str,
        identification_number: str,
        birth_date: datetime.date,
        today: datetime.date,
    ) -> "User":
        name = name.strip()
        identification_type = identification_type.strip().upper()
        identification_number = identification_number.strip()
        if not name:
            raise InvalidUserData("El nombre es obligatorio.")
        if not identification_type or not identification_number:
            raise InvalidUserData("El tipo y número de identificación son obligatorios.")
        if birth_date >= today:
            raise InvalidUserData("La fecha de nacimiento debe estar en el pasado.")
        return cls(
            id=uuid.uuid4(),
            name=name,
            email=email.strip().lower(),
            identification_type=identification_type,
            identification_number=identification_number,
            birth_date=birth_date,
        )

    def deactivate(self) -> None:
        if not self.is_active:
            raise UserAlreadyInactive()
        self.is_active = False
