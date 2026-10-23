"""El router solo adapta HTTP -> caso de uso. No contiene reglas de negocio."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.src.application.dto import RegisterUserCommand
from app.src.application.use_cases.users import DeactivateUser, GetUser, ListUsers, RegisterUser
from app.src.presentation.api.v1.dependencies import (
    deactivate_user_use_case,
    get_user_use_case,
    list_users_use_case,
    register_user_use_case,
)
from app.src.presentation.api.v1.schemas import ErrorResponse, RegisterUserRequest, UserResponse

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED, responses={409: {"model": ErrorResponse}})
def register_user(
    body: RegisterUserRequest,
    use_case: Annotated[RegisterUser, Depends(register_user_use_case)],
) -> UserResponse:
    user = use_case.execute(RegisterUserCommand(**body.model_dump()))
    return UserResponse.from_entity(user)


@router.get("")
def list_users(
    use_case: Annotated[ListUsers, Depends(list_users_use_case)],
    only_active: bool = False,
) -> list[UserResponse]:
    return [UserResponse.from_entity(user) for user in use_case.execute(only_active=only_active)]


@router.get("/{user_id}", responses={404: {"model": ErrorResponse}})
def get_user(user_id: UUID, use_case: Annotated[GetUser, Depends(get_user_use_case)]) -> UserResponse:
    return UserResponse.from_entity(use_case.execute(user_id))


@router.post("/{user_id}/deactivate", responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}})
def deactivate_user(
    user_id: UUID, use_case: Annotated[DeactivateUser, Depends(deactivate_user_use_case)]
) -> UserResponse:
    return UserResponse.from_entity(use_case.execute(user_id))
