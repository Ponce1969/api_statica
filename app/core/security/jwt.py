from datetime import UTC, datetime, timedelta
from typing import Optional, Dict, Any
import logging
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError

from app.core.config import settings

logger = logging.getLogger(__name__)
ALGORITHM = settings.ALGORITHM

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token de acceso JWT con expiración."""
    sub = data.get("sub")
    if not isinstance(sub, str) or not sub:
        raise ValueError("El token debe incluir un 'sub' válido como string no vacío")

    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    return str(jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM))

def decode_access_token(token: str) -> Dict[str, Any] | None:
    """Decodifica un token JWT y retorna el payload si es válido."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        logger.warning("JWT expirado")
        return None
    except (JWTClaimsError, JWTError) as e:
        logger.warning(f"Error de token JWT: {e}")
        return None
