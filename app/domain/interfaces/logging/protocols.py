"""
Protocolos para logging.

Este módulo define las interfaces para los componentes de logging
siguiendo los principios de Clean Architecture y el patrón de puertos y adaptadores.
"""

from enum import Enum, auto
from typing import Any, Dict, Protocol


class LogLevel(Enum):
    """Niveles de logging soportados."""
    
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


class LoggerProtocol(Protocol):
    """Protocolo para loggers."""
    
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Registra un mensaje con nivel DEBUG.
        
        Args:
            msg: El mensaje a registrar.
            *args: Argumentos adicionales para el mensaje.
            **kwargs: Argumentos de palabra clave adicionales para el mensaje.
        """
        ...
    
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Registra un mensaje con nivel INFO.
        
        Args:
            msg: El mensaje a registrar.
            *args: Argumentos adicionales para el mensaje.
            **kwargs: Argumentos de palabra clave adicionales para el mensaje.
        """
        ...
    
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Registra un mensaje con nivel WARNING.
        
        Args:
            msg: El mensaje a registrar.
            *args: Argumentos adicionales para el mensaje.
            **kwargs: Argumentos de palabra clave adicionales para el mensaje.
        """
        ...
    
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Registra un mensaje con nivel ERROR.
        
        Args:
            msg: El mensaje a registrar.
            *args: Argumentos adicionales para el mensaje.
            **kwargs: Argumentos de palabra clave adicionales para el mensaje.
        """
        ...
    
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Registra un mensaje con nivel CRITICAL.
        
        Args:
            msg: El mensaje a registrar.
            *args: Argumentos adicionales para el mensaje.
            **kwargs: Argumentos de palabra clave adicionales para el mensaje.
        """
        ...
    
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """
        Registra un mensaje con nivel ERROR incluyendo información de la excepción.
        
        Args:
            msg: El mensaje a registrar.
            *args: Argumentos adicionales para el mensaje.
            **kwargs: Argumentos de palabra clave adicionales para el mensaje.
        """
        ...


class LoggerFactoryProtocol(Protocol):
    """Protocolo para fábricas de loggers."""
    
    def get_logger(self, name: str) -> LoggerProtocol:
        """
        Obtiene un logger con el nombre especificado.
        
        Args:
            name: El nombre del logger.
            
        Returns:
            Un logger configurado.
        """
        ...
