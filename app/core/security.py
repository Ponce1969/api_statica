"""Security utilities and reusable dependencies for FastAPI auth.

Defines the OAuth2 bearer scheme so that Swagger (OpenAPI) shows the
"Authorize" button. The token URL points to the login endpoint that
returns the JWT token.
"""
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import Request
from typing import Optional

class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    """Extensión de OAuth2PasswordBearer para personalizar los mensajes de error."""
    
    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No autenticado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        return param

# The login route is registered under /api/v1/login
oauth2_scheme = CustomOAuth2PasswordBearer(
    tokenUrl="/api/v1/login",
    auto_error=True
)
