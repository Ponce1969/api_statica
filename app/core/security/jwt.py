from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from app.core.config import settings

# Se recomienda definir explícitamente el algoritmo en settings.py
ALGORITHM = getattr(settings, "ALGORITHM", "HS256")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token de acceso JWT con expiración."""
    if "sub" not in data:
        raise ValueError("El token debe incluir el campo 'sub'")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica un token JWT y retorna el payload si es válido."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        return None
    except (JWTClaimsError, JWTError):
        return None
