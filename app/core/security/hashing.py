
from typing import Protocol
from passlib.context import CryptContext

# Contexto de hashing configurable
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class PasswordHasher(Protocol):
    """Protocolo para definir un hasher de contraseñas."""
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...
    def get_password_hash(self, password: str) -> str: ...

class Argon2PasswordHasher:
    """Implementación concreta de PasswordHasher usando Argon2."""
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica si la contraseña plana coincide con el hash."""
        return bool(pwd_context.verify(plain_password, hashed_password))
    
    def get_password_hash(self, password: str) -> str:
        """Genera el hash de una contraseña."""
        return str(pwd_context.hash(password))

# Instancia por defecto para facilitar el uso
default_password_hasher = Argon2PasswordHasher()

# Funciones de conveniencia (para compatibilidad con código existente)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash."""
    return default_password_hasher.verify_password(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña."""
    return default_password_hasher.get_password_hash(password)
