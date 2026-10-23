import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.src.domain.entities.user import User


class RegisterUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    identification_type: str = Field(min_length=1, max_length=10, examples=["CC"])
    identification_number: str = Field(min_length=1, max_length=30)
    birth_date: datetime.date


class UserResponse(BaseModel):
    """Contrato público de users-service (docs/contracts/rest.md)."""

    id: UUID
    name: str
    email: str
    identification_type: str
    identification_number: str
    birth_date: datetime.date
    is_active: bool

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            name=user.name,
            email=user.email,
            identification_type=user.identification_type,
            identification_number=user.identification_number,
            birth_date=user.birth_date,
            is_active=user.is_active,
        )


class ErrorResponse(BaseModel):
    detail: str
