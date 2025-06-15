from passlib.context import CryptContext
from typing import Any

# Contexto de hashing configurable
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash."""
    return bool(pwd_context.verify(plain_password, hashed_password))

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return str(pwd_context.hash(password))
