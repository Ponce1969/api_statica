from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import get_user_service, get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.domain.models.user import User as UserDomain

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    user_service: Annotated[UserService, Depends(get_user_service)],  # noqa: B008
) -> UserResponse:
    try:
        user = await user_service.create_user_with_hashed_password(user_in)
        # Convertir el modelo de dominio a esquema de respuesta
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name if hasattr(user, 'full_name') else None,
            is_active=user.is_active if hasattr(user, 'is_active') else True
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.get("/", response_model=list[UserResponse])
async def list_users(
    user_service: Annotated[UserService, Depends(get_user_service)],  # noqa: B008
    email: str | None = Query(
        None,
        description="Filtrar usuarios por email exacto",
        example="ejemplo@correo.com"
    ),
    is_active: bool | None = Query(
        None,
        description="Filtrar por estado activo (True o False)",
        example=True
    ),
) -> list[UserResponse]:
    users = await user_service.get_users(email=email, is_active=is_active)
    return [UserResponse(id=u.id, email=u.email, full_name=u.full_name) for u in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],  # noqa: B008
) -> UserResponse:
    user = await user_service.get_user(user_id)
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name if hasattr(user, 'full_name') else None,
        is_active=user.is_active if hasattr(user, 'is_active') else True
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    user_service: Annotated[UserService, Depends(get_user_service)],  # noqa: B008
) -> None:
    await user_service.delete_user(user_id)
    return None


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: Annotated[UserDomain, Depends(get_current_user)],  # noqa: B008
) -> UserResponse:
    """Devuelve los datos del usuario autenticado."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=getattr(current_user, "full_name", None),
        is_active=getattr(current_user, "is_active", True),
    )
