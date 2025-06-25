"""
Pruebas unitarias para el adaptador de logging estándar.

Este módulo contiene pruebas para verificar que el adaptador de logging estándar
funciona correctamente y cumple con los protocolos definidos.
"""

import logging
import pytest
from unittest.mock import MagicMock, patch

from app.domain.interfaces.logging.protocols import LogLevel, LoggerProtocol
from app.infrastructure.adapters.logging.standard_logger import (
    get_log_level,
    SensitiveDataFilter,
    StandardLoggerFactory,
    get_logger,
)


def test_get_log_level() -> None:
    """Verifica que la función get_log_level convierte correctamente los niveles de log."""
    assert get_log_level(LogLevel.DEBUG) == logging.DEBUG
    assert get_log_level(LogLevel.INFO) == logging.INFO
    assert get_log_level(LogLevel.WARNING) == logging.WARNING
    assert get_log_level(LogLevel.ERROR) == logging.ERROR
    assert get_log_level(LogLevel.CRITICAL) == logging.CRITICAL


class TestSensitiveDataFilter:
    """Pruebas para el filtro de datos sensibles."""
    
    def test_init_default_fields(self) -> None:
        """Verifica que se inicializan correctamente los campos sensibles por defecto."""
        filter = SensitiveDataFilter()
        
        # Verificar que existen los campos sensibles por defecto
        assert "password" in filter.sensitive_fields
        assert "token" in filter.sensitive_fields
        assert "api_key" in filter.sensitive_fields
        
        # Verificar que se inicializan correctamente los parámetros de enmascaramiento
        assert filter.mask_char == "*"
        assert filter.mask_length == 8
        assert filter.mask == "********"
    
    def test_init_custom_fields(self) -> None:
        """Verifica que se inicializan correctamente los campos sensibles personalizados."""
        custom_fields = {"custom_field", "another_field"}
        filter = SensitiveDataFilter(sensitive_fields=custom_fields, mask_char="#", mask_length=4)
        
        # Verificar que existen los campos sensibles personalizados
        assert "custom_field" in filter.sensitive_fields
        assert "another_field" in filter.sensitive_fields
        
        # Verificar que también existen los campos sensibles por defecto
        assert "password" in filter.sensitive_fields
        
        # Verificar que se inicializan correctamente los parámetros de enmascaramiento
        assert filter.mask_char == "#"
        assert filter.mask_length == 4
        assert filter.mask == "####"
    
    def test_filter_string_message(self) -> None:
        """Verifica que se enmascaran correctamente los mensajes de tipo string."""
        filter = SensitiveDataFilter()
        
        # Crear un registro de log con un mensaje sensible
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="El password es secreto123",
            args=(),
            exc_info=None,
        )
        
        # Aplicar el filtro
        filter.filter(record)
        
        # Verificar que se ha enmascarado el mensaje
        assert record.msg == "[Mensaje con datos sensibles: password]"
    
    def test_filter_dict_message(self) -> None:
        """Verifica que se enmascaran correctamente los mensajes de tipo dict."""
        filter = SensitiveDataFilter()
        
        # Crear un registro de log con un mensaje sensible en formato dict
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg={"user": "admin", "password": "secreto123", "data": {"api_key": "abc123"}},
            args=(),
            exc_info=None,
        )
        
        # Aplicar el filtro
        filter.filter(record)
        
        # Verificar que se han enmascarado los campos sensibles
        assert record.msg["user"] == "admin"
        assert record.msg["password"] == "********"
        assert record.msg["data"]["api_key"] == "********"
    
    def test_filter_args(self) -> None:
        """Verifica que se enmascaran correctamente los argumentos sensibles."""
        filter = SensitiveDataFilter()
        
        # Crear un registro de log con argumentos sensibles
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="User: %s, Password: %s",
            args=("admin", "secreto123"),
            exc_info=None,
        )
        
        # Aplicar el filtro
        filter.filter(record)
        
        # Verificar que se ha enmascarado el argumento sensible
        assert record.args[0] == "admin"
        assert record.args[1] == filter.mask


class TestStandardLoggerFactory:
    """Pruebas para la fábrica de loggers estándar."""
    
    @patch("logging.basicConfig")
    @patch("logging.getLogger")
    def test_init(self, mock_get_logger: MagicMock, mock_basic_config: MagicMock) -> None:
        """Verifica que se inicializa correctamente la fábrica de loggers."""
        # Crear mock para el logger raíz
        mock_root_logger = MagicMock()
        mock_get_logger.return_value = mock_root_logger
        
        # Crear la fábrica de loggers
        factory = StandardLoggerFactory(debug_mode=True)
        
        # Verificar que se ha configurado el logging básico
        mock_basic_config.assert_called_once()
        
        # Verificar que se ha añadido el filtro de datos sensibles al logger raíz
        mock_root_logger.addFilter.assert_called_once()
        filter_arg = mock_root_logger.addFilter.call_args[0][0]
        assert isinstance(filter_arg, SensitiveDataFilter)
    
    @patch("logging.getLogger")
    def test_get_logger(self, mock_get_logger: MagicMock) -> None:
        """Verifica que get_logger devuelve un logger configurado."""
        # Crear mock para el logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Crear la fábrica de loggers
        factory = StandardLoggerFactory(debug_mode=False)
        
        # Obtener un logger
        logger = factory.get_logger("test")
        
        # Verificar que se ha llamado a getLogger con el nombre correcto
        mock_get_logger.assert_called_with("test")
        
        # Verificar que se ha devuelto el logger correcto
        assert logger is mock_logger


def test_get_logger_function() -> None:
    """Verifica que la función get_logger funciona correctamente."""
    with patch("app.infrastructure.adapters.logging.standard_logger.logger_factory") as mock_factory:
        # Crear mock para el logger
        mock_logger = MagicMock()
        mock_factory.get_logger.return_value = mock_logger
        
        # Obtener un logger
        logger = get_logger("test")
        
        # Verificar que se ha llamado a get_logger con el nombre correcto
        mock_factory.get_logger.assert_called_with("test")
        
        # Verificar que se ha devuelto el logger correcto
        assert logger is mock_logger
