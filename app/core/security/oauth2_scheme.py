"""Módulo que define el esquema de autenticación OAuth2 personalizado.

Este módulo contiene la implementación de CustomOAuth2PasswordBearer y la instancia
del esquema que se utiliza en toda la aplicación.
"""
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.oauth2 import OAuth2
from typing import Optional, Dict, Any
from starlette.requests import Request as StarletteRequest

class CustomOAuth2PasswordBearer(OAuth2):
    """Extensión de OAuth2 para personalizar los mensajes de error y códigos de estado.
    
    Esta implementación asegura que se devuelva un 401 en lugar de 422 cuando falta
    el token o es inválido.
    """
    
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)
    
    async def __call__(self, request: StarletteRequest) -> Optional[str]:
        # Obtener el header de autorización
        authorization: str = request.headers.get("Authorization")
        
        # Si no hay header de autorización, lanzar 401
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No autenticado",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
            
        try:
            # Verificar el esquema de autenticación
            scheme, param = get_authorization_scheme_param(authorization)
            
            # Si el esquema no es Bearer o no hay token, lanzar 401
            if not authorization or scheme.lower() != "bearer" or not param:
                raise ValueError("Formato de token inválido")
                
            return param
            
        except (ValueError, IndexError):
            # Capturar errores de formato de token
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

# La ruta del endpoint de login que entrega el token JWT
oauth2_scheme = CustomOAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=True,
    scheme_name="JWT"
)
