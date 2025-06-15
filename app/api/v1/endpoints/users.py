from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.core.deps import get_user_service
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
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
    email: Optional[str] = Query(
        None,
        description="Filtrar usuarios por email exacto",
        example="ejemplo@correo.com"
    ),
    is_active: Optional[bool] = Query(
        None,
        description="Filtrar por estado activo (True o False)",
        example=True
    ),
    user_service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    users = await user_service.get_users(email=email, is_active=is_active)
    return [UserResponse(id=u.id, email=u.email, full_name=u.full_name) for u in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
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
    user_service: UserService = Depends(get_user_service),
) -> None:
    await user_service.delete_user(user_id)
    return None
