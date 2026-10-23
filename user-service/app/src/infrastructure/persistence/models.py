"""Modelo ORM de users-service (tabla usr_users). Es privado de este servicio:
ningún otro servicio lo importa; los demás consultan la API REST."""

import datetime
import uuid

from sqlmodel import Field, SQLModel


class UserModel(SQLModel, table=True):
    __tablename__ = "usr_users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    identification_type: str
    identification_number: str
    birth_date: datetime.date
    is_active: bool = True
