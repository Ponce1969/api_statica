"""
Adaptadores de middleware HTTP para FastAPI.

Este módulo implementa los adaptadores concretos para middleware HTTP
utilizando FastAPI y Starlette, siguiendo los principios de Clean Architecture.
"""

import logging
import time
import uuid
from typing import Any, Awaitable, Callable, List, Optional, Set

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.domain.interfaces.http.protocols import MiddlewareFactoryProtocol, MiddlewareProtocol


class RequestLoggingMiddleware(BaseHTTPMiddleware, MiddlewareProtocol):
    """
    Middleware para logging y monitoreo de solicitudes HTTP.
    
    Este middleware añade un ID único a cada solicitud, mide el tiempo de procesamiento,
    y registra información relevante sobre la solicitud y la respuesta.
    """
    
    def __init__(
        self,
        app: FastAPI,
        exclude_paths: Optional[List[str]] = None,
        slow_response_threshold_ms: int = 1000,
    ) -> None:
        """
        Inicializa el middleware.
        
        Args:
            app: La aplicación FastAPI.
            exclude_paths: Lista de rutas a excluir del logging.
            slow_response_threshold_ms: Umbral en milisegundos para considerar una respuesta lenta.
        """
        super().__init__(app)
        self.logger = logging.getLogger("app.middleware.request")
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/metrics", "/health"]
        self.slow_response_threshold_ms = slow_response_threshold_ms
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Procesa una solicitud HTTP.
        
        Args:
            request: La solicitud HTTP a procesar.
            call_next: Función para llamar al siguiente middleware en la cadena.
            
        Returns:
            La respuesta HTTP resultante.
        """
        # Excluir rutas específicas
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Generar ID único para la solicitud
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Registrar inicio de la solicitud
        start_time = time.time()
        self.logger.info(
            f"Solicitud iniciada | ID: {request_id} | Método: {request.method} | "
            f"Ruta: {request.url.path} | Cliente: {request.client.host if request.client else 'desconocido'}"
        )
        
        # Procesar la solicitud
        try:
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time
            process_time_ms = process_time * 1000
            formatted_process_time = f"{process_time_ms:.2f}ms"
            
            # Añadir headers de diagnóstico
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = formatted_process_time
            
            # Registrar finalización de la solicitud
            log_level = logging.WARNING if process_time_ms > self.slow_response_threshold_ms else logging.INFO
            self.logger.log(
                log_level,
                f"Solicitud completada | ID: {request_id} | Estado: {response.status_code} | "
                f"Tiempo: {formatted_process_time}" +
                (f" | ALERTA: Respuesta lenta" if process_time_ms > self.slow_response_threshold_ms else "")
            )
            
            return response
        except Exception as e:
            # Registrar error
            self.logger.exception(
                f"Error en solicitud | ID: {request_id} | Error: {str(e)}"
            )
            raise


class FastAPIMiddlewareFactory(MiddlewareFactoryProtocol):
    """Fábrica para crear y configurar middlewares de FastAPI."""
    
    def __init__(self, app: FastAPI) -> None:
        """
        Inicializa la fábrica.
        
        Args:
            app: La aplicación FastAPI.
        """
        self.app = app
    
    def get_middlewares(self) -> Set[MiddlewareProtocol]:
        """
        Obtiene los middlewares configurados.
        
        Returns:
            Un conjunto de middlewares configurados.
        """
        return {RequestLoggingMiddleware(self.app)}


def setup_middlewares(app: FastAPI) -> None:
    """
    Configura los middlewares para la aplicación FastAPI.
    
    Args:
        app: La aplicación FastAPI.
    """
    # Añadir middleware de logging con los parámetros adecuados
    app.add_middleware(
        RequestLoggingMiddleware,
        exclude_paths=["/docs", "/redoc", "/openapi.json", "/metrics", "/health"],
        slow_response_threshold_ms=1000
    )
    
    # Aquí se pueden añadir más middlewares según sea necesario
