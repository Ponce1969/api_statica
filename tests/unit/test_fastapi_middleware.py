"""
Pruebas unitarias para el adaptador de middleware HTTP de FastAPI.

Este módulo contiene pruebas para verificar que el adaptador de middleware HTTP
funciona correctamente y cumple con los protocolos definidos.
"""

import logging
import pytest
import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from app.infrastructure.adapters.http.fastapi_middleware import (
    RequestLoggingMiddleware,
    FastAPIMiddlewareFactory,
    setup_middlewares,
)


@pytest.fixture
def mock_app() -> MagicMock:
    """Fixture para crear un mock de la aplicación FastAPI."""
    return MagicMock(spec=FastAPI)


@pytest.fixture
def mock_request() -> MagicMock:
    """Fixture para crear un mock de una solicitud HTTP."""
    request = MagicMock(spec=Request)
    request.method = "GET"
    request.url.path = "/test"
    request.client.host = "127.0.0.1"
    request.state = MagicMock()
    return request


@pytest.fixture
def mock_response() -> MagicMock:
    """Fixture para crear un mock de una respuesta HTTP."""
    response = MagicMock(spec=Response)
    response.status_code = 200
    response.headers = {}
    return response


class TestRequestLoggingMiddleware:
    """Pruebas para el middleware de logging de solicitudes."""
    
    def test_init(self, mock_app: MagicMock) -> None:
        """Verifica que se inicializa correctamente el middleware."""
        # Crear el middleware
        middleware = RequestLoggingMiddleware(mock_app)
        
        # Verificar que se ha inicializado correctamente
        assert middleware.logger.name == "app.middleware.request"
        assert middleware.exclude_paths == ["/docs", "/redoc", "/openapi.json", "/metrics", "/health"]
        assert middleware.slow_response_threshold_ms == 1000
    
    def test_init_custom_params(self, mock_app: MagicMock) -> None:
        """Verifica que se inicializa correctamente el middleware con parámetros personalizados."""
        # Crear el middleware con parámetros personalizados
        exclude_paths = ["/custom", "/another"]
        slow_threshold = 500
        middleware = RequestLoggingMiddleware(
            mock_app,
            exclude_paths=exclude_paths,
            slow_response_threshold_ms=slow_threshold,
        )
        
        # Verificar que se ha inicializado correctamente
        assert middleware.exclude_paths == exclude_paths
        assert middleware.slow_response_threshold_ms == slow_threshold
    
    @pytest.mark.asyncio
    async def test_dispatch_excluded_path( # Renombrado para claridad
        self, mock_app: MagicMock, mock_request: MagicMock
    ) -> None:
        """Verifica que se excluyen correctamente las rutas especificadas."""
        # Configurar el mock de la solicitud
        mock_request.url.path = "/docs"
        
        # Crear el middleware
        middleware = RequestLoggingMiddleware(mock_app)
        
        # Crear un mock para call_next
        mock_response = MagicMock()
        call_next = AsyncMock(return_value=mock_response)
        
        # Procesar la solicitud
        response = await middleware.dispatch(mock_request, call_next) # LLAMAR A DISPATCH
        
        # Verificar que se ha llamado a call_next con la solicitud
        call_next.assert_called_once_with(mock_request)
        
        # Verificar que se ha devuelto la respuesta correcta
        assert response is mock_response
    
    @pytest.mark.asyncio
    async def test_dispatch_normal( # Renombrado para claridad
        self, mock_app: MagicMock, mock_request: MagicMock, mock_response: MagicMock
    ) -> None:
        """Verifica que se procesa correctamente una solicitud normal."""
        # Crear el middleware
        with patch("uuid.uuid4") as mock_uuid, \
             patch("time.time") as mock_time, \
             patch("logging.getLogger") as mock_get_logger:
            
            # Configurar los mocks
            mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
            mock_time.side_effect = [100.0, 100.5]  # Inicio y fin
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Crear el middleware
            middleware = RequestLoggingMiddleware(mock_app)
            
            # Crear un mock para call_next
            call_next = AsyncMock(return_value=mock_response)
            
            # Procesar la solicitud
            response = await middleware.dispatch(mock_request, call_next) # LLAMAR A DISPATCH
            
            # Verificar que se ha generado un ID único para la solicitud
            assert mock_request.state.request_id == "12345678-1234-5678-1234-567812345678"
            
            # Verificar que se ha registrado el inicio de la solicitud
            mock_logger.info.assert_called_once()
            assert "Solicitud iniciada" in mock_logger.info.call_args[0][0]
            assert "12345678-1234-5678-1234-567812345678" in mock_logger.info.call_args[0][0]
            
            # Verificar que se ha llamado a call_next con la solicitud
            call_next.assert_called_once_with(mock_request)
            
            # Verificar que se han añadido los headers de diagnóstico
            assert mock_response.headers["X-Request-ID"] == "12345678-1234-5678-1234-567812345678"
            assert mock_response.headers["X-Process-Time"] == "500.00ms"
            
            # Verificar que se ha registrado la finalización de la solicitud
            mock_logger.log.assert_called_once()
            assert mock_logger.log.call_args[0][0] == logging.INFO
            assert "Solicitud completada" in mock_logger.log.call_args[0][1]
            assert "12345678-1234-5678-1234-567812345678" in mock_logger.log.call_args[0][1]
            
            # Verificar que se ha devuelto la respuesta correcta
            assert response is mock_response
    
    @pytest.mark.asyncio
    async def test_dispatch_slow( # Renombrado para claridad
        self, mock_app: MagicMock, mock_request: MagicMock, mock_response: MagicMock
    ) -> None:
        """Verifica que se detecta correctamente una respuesta lenta."""
        # Crear el middleware
        with patch("uuid.uuid4") as mock_uuid, \
             patch("time.time") as mock_time, \
             patch("logging.getLogger") as mock_get_logger:
            
            # Configurar los mocks
            mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
            mock_time.side_effect = [100.0, 102.0]  # 2 segundos de procesamiento
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Crear el middleware
            middleware = RequestLoggingMiddleware(mock_app)
            
            # Crear un mock para call_next
            call_next = AsyncMock(return_value=mock_response)
            
            # Procesar la solicitud
            response = await middleware.dispatch(mock_request, call_next) # LLAMAR A DISPATCH

            # Verificar que se ha llamado a call_next con la solicitud
            call_next.assert_called_once_with(mock_request)
            
            # Verificar que se ha registrado la finalización de la solicitud como lenta
            mock_logger.log.assert_called_once()
            assert mock_logger.log.call_args[0][0] == logging.WARNING
            assert "ALERTA: Respuesta lenta" in mock_logger.log.call_args[0][1]
    
    @pytest.mark.asyncio
    async def test_dispatch_error( # Renombrado para claridad
        self, mock_app: MagicMock, mock_request: MagicMock
    ) -> None:
        """Verifica que se maneja correctamente un error durante el procesamiento."""
        # Crear el middleware
        with patch("uuid.uuid4") as mock_uuid, \
             patch("logging.getLogger") as mock_get_logger:
            
            # Configurar los mocks
            mock_uuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Crear el middleware
            middleware = RequestLoggingMiddleware(mock_app)
            
            # Crear un mock para call_next que lanza una excepción
            error = ValueError("Error de prueba")
            call_next = AsyncMock(side_effect=error)
            
            # Procesar la solicitud (debe lanzar la excepción)
            with pytest.raises(ValueError):
                await middleware.dispatch(mock_request, call_next) # LLAMAR A DISPATCH

            # Verificar que se ha generado un ID único para la solicitud
            assert mock_request.state.request_id == "12345678-1234-5678-1234-567812345678"
            
            # Verificar que se ha llamado a call_next con la solicitud
            call_next.assert_called_once_with(mock_request)
            
            # Verificar que se ha registrado el error
            mock_logger.exception.assert_called_once()
            assert "Error en solicitud" in mock_logger.exception.call_args[0][0]
            assert "12345678-1234-5678-1234-567812345678" in mock_logger.exception.call_args[0][0]
            assert "Error de prueba" in mock_logger.exception.call_args[0][0]


class TestFastAPIMiddlewareFactory:
    """Pruebas para la fábrica de middlewares de FastAPI."""
    
    def test_init(self, mock_app: MagicMock) -> None:
        """Verifica que se inicializa correctamente la fábrica."""
        # Crear la fábrica
        factory = FastAPIMiddlewareFactory(mock_app)
        
        # Verificar que se ha inicializado correctamente
        assert factory.app is mock_app
    
    def test_get_middlewares(self, mock_app: MagicMock) -> None:
        """Verifica que get_middlewares devuelve los middlewares configurados."""
        # Crear la fábrica
        factory = FastAPIMiddlewareFactory(mock_app)
        
        # Obtener los middlewares
        middlewares = factory.get_middlewares()
        
        # Verificar que se ha devuelto un conjunto de middlewares
        assert isinstance(middlewares, set)
        assert len(middlewares) == 1
        
        # Verificar que los middlewares son del tipo correcto
        for middleware in middlewares:
            assert isinstance(middleware, RequestLoggingMiddleware)


def test_setup_middlewares(mock_app: MagicMock) -> None:
    """Verifica que setup_middlewares configura correctamente los middlewares."""
    # Configurar los middlewares
    setup_middlewares(mock_app)
    
    # Verificar que se ha añadido el middleware de logging
    mock_app.add_middleware.assert_called_once_with(RequestLoggingMiddleware)
