"""Manejadores de excepciones personalizados para la aplicación."""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Maneja las excepciones HTTP personalizadas."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Maneja los errores de validación de Pydantic.
    
    Convierte los errores 422 a 401 cuando el error está relacionado con la autenticación.
    """
    # Verificar si el error está relacionado con la autenticación
    for error in exc.errors():
        if any("authorization" in str(loc).lower() for loc in error["loc"]) or \
           any("token" in str(loc).lower() for loc in error["loc"]):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Could not validate credentials"},
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Para otros errores de validación, mantener el comportamiento por defecto
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

def setup_exception_handlers(app: FastAPI) -> None:
    """Configura los manejadores de excepciones personalizados."""
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
