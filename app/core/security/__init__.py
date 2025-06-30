"""Paquete de utilidades de seguridad (JWT, hashing, OAuth2).

Este paquete proporciona utilidades para manejo de autenticación y seguridad,
incluyendo hashing de contraseñas, generación de tokens JWT y esquemas OAuth2.
"""
from fastapi.security import OAuth2PasswordBearer

from .hashing import (
    PasswordHasher,
    Argon2PasswordHasher,
    default_password_hasher,
    verify_password,
    get_password_hash,
)

# La ruta del endpoint de login que entrega el token JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

__all__ = [
    "oauth2_scheme",
    "PasswordHasher",
    "Argon2PasswordHasher",
    "default_password_hasher",
    "verify_password",
    "get_password_hash",
]
