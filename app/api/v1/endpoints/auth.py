
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.domain.exceptions.base import ValidationError, EntityNotFoundError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.core.deps import get_auth_service
from app.schemas.token import Token
from app.services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

router = APIRouter()

# Usamos formulario OAuth2 estándar (username y password)
    
    

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    Autentica un usuario y devuelve un token de acceso.
    
    - **username**: Email del usuario
    - **password**: Contraseña del usuario
    """
    try:
        user = await auth_service.authenticate_user(form_data.username, form_data.password)
        token_dict = auth_service.generate_token(user)
        return Token(**token_dict)
        
    except (ValidationError, EntityNotFoundError) as err:
        # Usuario no encontrado o credenciales inválidas
        logger.warning(f"Intento de inicio de sesión fallido para {form_data.username}: {str(err)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    except Exception as err:
        # Log del error inesperado
        logger.error(f"Error inesperado durante el login para {form_data.username}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante la autenticación",
        ) from err
