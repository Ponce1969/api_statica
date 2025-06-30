"""Middleware personalizado para manejo de autenticación y códigos de estado HTTP."""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response
from typing import Any, Callable, Optional, Dict

from app.core.security.oauth2_scheme import oauth2_scheme
from app.core.security.jwt import decode_access_token

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware para manejar la autenticación y códigos de estado HTTP."""
    
    async def dispatch(self, request: StarletteRequest, call_next: Callable) -> Response:
        # Lista de rutas que no requieren autenticación
        public_paths = ["/api/v1/auth/login", "/api/v1/docs", "/api/v1/openapi.json", "/openapi.json"]
        
        # Si la ruta es pública, continuar sin validar autenticación
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
            
        # Verificar si la ruta es protegida (comienza con /api/v1/)
        if request.url.path.startswith("/api/v1/"):
            # Obtener el token del encabezado de autorización
            authorization: str = request.headers.get("Authorization")
            
            # Si no hay token o está vacío, devolver 401 con mensaje específico
            if not authorization or not authorization.strip():
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "No autenticado"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verificar el esquema de autenticación
            try:
                # Intentar dividir el esquema y el token
                parts = authorization.split()
                if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "No autenticado"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Validar el token JWT
                token = parts[1]
                payload = decode_access_token(token)
                if not payload:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Could not validate credentials"},
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                # Continuar con la solicitud si todo está bien
                return await call_next(request)
                
            except Exception as e:
                # Cualquier otro error inesperado, devolver 401 con mensaje de no autenticado
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "No autenticado"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        # Para rutas que no son API, continuar sin validación
        return await call_next(request)
