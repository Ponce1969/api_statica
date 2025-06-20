"""Paquete de utilidades de seguridad (JWT, hashing, OAuth2).

Define y expone `oauth2_scheme` para que FastAPI genere el formulario de
login en Swagger UI.
"""
from fastapi.security import OAuth2PasswordBearer

# La ruta del endpoint de login que entrega el token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

__all__ = ["oauth2_scheme"]
