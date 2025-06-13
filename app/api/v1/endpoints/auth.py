from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.core.deps import get_auth_service
from app.schemas.token import Token
from app.services.auth_service import AuthService

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login", response_model=Token)
async def login(data: LoginRequest, auth_service: AuthService = None) -> dict:
    if auth_service is None:
        auth_service = get_auth_service()
    try:
        user = await auth_service.authenticate_user(data.email, data.password)
        token = auth_service.generate_token(user)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
        ) from err
