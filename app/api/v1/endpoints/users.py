from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.deps import get_user_service

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = await user_service.create_user_with_hashed_password(user_in)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=list[UserResponse])
async def list_users(user_service: UserService = Depends(get_user_service)):
    users = await user_service.get_users()
    # Adaptar a schema UserResponse
    return [UserResponse(id=u.id, email=u.email, full_name=u.full_name) for u in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, user_service: UserService = Depends(get_user_service)):
    user = await user_service.get_user(user_id)
    return UserResponse(id=user.id, email=user.email, full_name=user.full_name)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, user_service: UserService = Depends(get_user_service)):
    await user_service.delete_user(user_id)
    return None
