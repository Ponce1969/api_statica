"""
Pruebas unitarias para los protocolos de logging.

Este módulo contiene pruebas para verificar que los protocolos de logging
están correctamente definidos y cumplen con los estándares de tipado estricto.
"""

import pytest
from typing import Any, Protocol, runtime_checkable

from app.domain.interfaces.logging.protocols import LogLevel, LoggerProtocol, LoggerFactoryProtocol


def test_log_level_enum() -> None:
    """Verifica que el enum LogLevel está correctamente definido."""
    # Verificar que existen todos los niveles esperados
    assert hasattr(LogLevel, "DEBUG")
    assert hasattr(LogLevel, "INFO")
    assert hasattr(LogLevel, "WARNING")
    assert hasattr(LogLevel, "ERROR")
    assert hasattr(LogLevel, "CRITICAL")
    
    # Verificar que son valores diferentes
    assert LogLevel.DEBUG != LogLevel.INFO
    assert LogLevel.INFO != LogLevel.WARNING
    assert LogLevel.WARNING != LogLevel.ERROR
    assert LogLevel.ERROR != LogLevel.CRITICAL


class MockLogger:
    """Implementación mock de LoggerProtocol para pruebas."""
    
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []
    
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(("DEBUG", msg))
    
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(("INFO", msg))
    
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(("WARNING", msg))
    
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(("ERROR", msg))
    
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(("CRITICAL", msg))
    
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.messages.append(("EXCEPTION", msg))


class MockLoggerFactory:
    """Implementación mock de LoggerFactoryProtocol para pruebas."""
    
    def __init__(self) -> None:
        self.loggers: dict[str, MockLogger] = {}
    
    def get_logger(self, name: str) -> LoggerProtocol:
        if name not in self.loggers:
            self.loggers[name] = MockLogger()
        return self.loggers[name]


def test_logger_protocol_compliance() -> None:
    """Verifica que MockLogger cumple con LoggerProtocol."""
    logger = MockLogger()
    
    # Verificar que cumple con el protocolo
    assert isinstance(logger, LoggerProtocol)
    
    # Verificar que los métodos funcionan correctamente
    logger.debug("Mensaje de debug")
    logger.info("Mensaje de info")
    logger.warning("Mensaje de warning")
    logger.error("Mensaje de error")
    logger.critical("Mensaje crítico")
    logger.exception("Mensaje de excepción")
    
    # Verificar que se registraron todos los mensajes
    assert len(logger.messages) == 6
    assert logger.messages[0] == ("DEBUG", "Mensaje de debug")
    assert logger.messages[1] == ("INFO", "Mensaje de info")
    assert logger.messages[2] == ("WARNING", "Mensaje de warning")
    assert logger.messages[3] == ("ERROR", "Mensaje de error")
    assert logger.messages[4] == ("CRITICAL", "Mensaje crítico")
    assert logger.messages[5] == ("EXCEPTION", "Mensaje de excepción")


def test_logger_factory_protocol_compliance() -> None:
    """Verifica que MockLoggerFactory cumple con LoggerFactoryProtocol."""
    factory = MockLoggerFactory()
    
    # Verificar que cumple con el protocolo
    assert isinstance(factory, LoggerFactoryProtocol)
    
    # Verificar que get_logger funciona correctamente
    logger1 = factory.get_logger("test1")
    logger2 = factory.get_logger("test2")
    logger3 = factory.get_logger("test1")  # Mismo nombre que logger1
    
    # Verificar que se crearon los loggers correctamente
    assert isinstance(logger1, LoggerProtocol)
    assert isinstance(logger2, LoggerProtocol)
    assert isinstance(logger3, LoggerProtocol)
    
    # Verificar que logger1 y logger3 son el mismo objeto
    assert logger1 is logger3
    
    # Verificar que logger1 y logger2 son objetos diferentes
    assert logger1 is not logger2
