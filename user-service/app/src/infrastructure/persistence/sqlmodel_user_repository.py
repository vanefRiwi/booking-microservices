from collections.abc import Sequence
from uuid import UUID

from sqlmodel import Session, col, select

from app.src.application.ports import UserRepository
from app.src.domain.entities.user import User
from app.src.infrastructure.persistence.models import UserModel


def to_domain(row: UserModel) -> User:
    return User(
        id=row.id,
        name=row.name,
        email=row.email,
        identification_type=row.identification_type,
        identification_number=row.identification_number,
        birth_date=row.birth_date,
        is_active=row.is_active,
    )


def to_row(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        name=user.name,
        email=user.email,
        identification_type=user.identification_type,
        identification_number=user.identification_number,
        birth_date=user.birth_date,
        is_active=user.is_active,
    )


class SQLModelUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(to_row(user))
        self._session.commit()

    def update(self, user: User) -> None:
        self._session.merge(to_row(user))
        self._session.commit()

    def get(self, user_id: UUID) -> User | None:
        row = self._session.get(UserModel, user_id)
        return to_domain(row) if row else None

    def get_by_email(self, email: str) -> User | None:
        row = self._session.exec(select(UserModel).where(UserModel.email == email)).first()
        return to_domain(row) if row else None

    def list(self, *, only_active: bool = False) -> Sequence[User]:
        query = select(UserModel).order_by(col(UserModel.name))
        if only_active:
            query = query.where(col(UserModel.is_active).is_(True))
        return [to_domain(row) for row in self._session.exec(query)]
