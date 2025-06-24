"""
Adaptador de logging estándar.

Este módulo implementa un adaptador concreto para el sistema de logging
utilizando la biblioteca estándar de Python, siguiendo los principios de Clean Architecture.
"""

import logging
import re
from typing import Any, Dict, Optional, Set, Union

from app.domain.interfaces.logging.protocols import LogLevel, LoggerProtocol, LoggerFactoryProtocol
from app.core.config import settings


def get_log_level(level: LogLevel) -> int:
    """
    Convierte un nivel de log del dominio a un nivel de log de la biblioteca estándar.
    
    Args:
        level: El nivel de log del dominio.
        
    Returns:
        El nivel de log de la biblioteca estándar.
    """
    mapping = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
        LogLevel.CRITICAL: logging.CRITICAL,
    }
    return mapping[level]


class SensitiveDataFilter(logging.Filter):
    """
    Filtro para enmascarar datos sensibles en los logs.
    
    Este filtro busca patrones de datos sensibles en los mensajes de log
    y los enmascara para evitar la exposición de información confidencial.
    """
    
    def __init__(
        self,
        sensitive_fields: Optional[Set[str]] = None,
        mask_char: str = "*",
        mask_length: int = 8
    ) -> None:
        """
        Inicializa el filtro.
        
        Args:
            sensitive_fields: Conjunto de campos sensibles a enmascarar.
            mask_char: Carácter a utilizar para el enmascaramiento.
            mask_length: Longitud del enmascaramiento.
        """
        super().__init__()
        
        # Campos sensibles por defecto
        default_fields = {
            "password", "token", "api_key", "secret", "credential",
            "auth", "key", "email", "phone", "address", "credit_card",
            "cvv", "ssn", "social_security", "passport"
        }
        
        self.sensitive_fields = default_fields.union(sensitive_fields or set())
        self.mask_char = mask_char
        self.mask_length = mask_length
        self.mask = mask_char * mask_length
        
        # Compilar patrones regex para mayor eficiencia
        self.patterns = [
            re.compile(rf"(?i)['\"]?{field}['\"]?\s*[:=]\s*['\"]?([^'\",\s]+)['\"]?", re.IGNORECASE)
            for field in self.sensitive_fields
        ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filtra un registro de log para enmascarar datos sensibles.
        
        Args:
            record: El registro de log a filtrar.
            
        Returns:
            True para incluir el registro en el log, False para excluirlo.
        """
        # Si el mensaje es un string, verificar si contiene datos sensibles
        if isinstance(record.msg, str):
            for field in self.sensitive_fields:
                if field.lower() in record.msg.lower():
                    record.msg = f"[Mensaje con datos sensibles: {field}]"
                    break
        
        # Si el mensaje es un diccionario, enmascarar campos sensibles
        elif isinstance(record.msg, dict):
            record.msg = self._mask_dict(record.msg)
        
        # Si hay args, verificar y enmascarar
        if record.args:
            args_list = list(record.args)
            for i, arg in enumerate(args_list):
                if isinstance(arg, dict):
                    args_list[i] = self._mask_dict(arg)
                elif isinstance(arg, str):
                    for field in self.sensitive_fields:
                        if field.lower() in arg.lower():
                            args_list[i] = f"[Dato sensible: {field}]"
                            break
            record.args = tuple(args_list)
        
        return True
    
    def _mask_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enmascara campos sensibles en un diccionario.
        
        Args:
            data: El diccionario a enmascarar.
            
        Returns:
            El diccionario con los campos sensibles enmascarados.
        """
        result = {}
        for key, value in data.items():
            if any(field.lower() in key.lower() for field in self.sensitive_fields):
                result[key] = self.mask
            elif isinstance(value, dict):
                result[key] = self._mask_dict(value)
            elif isinstance(value, str) and any(field.lower() in value.lower() for field in self.sensitive_fields):
                result[key] = self.mask
            else:
                result[key] = value
        return result


class StandardLoggerFactory(LoggerFactoryProtocol):
    """
    Fábrica para crear y configurar loggers estándar.
    
    Esta fábrica implementa el protocolo LoggerFactoryProtocol y proporciona
    loggers configurados según las necesidades de la aplicación.
    """
    
    def __init__(self, debug_mode: bool = False) -> None:
        """
        Inicializa la fábrica.
        
        Args:
            debug_mode: Si es True, configura los loggers en modo debug.
        """
        self.debug_mode = debug_mode
        self._configure_logging()
    
    def _configure_logging(self) -> None:
        """Configura el sistema de logging global."""
        # Nivel base según modo
        base_level = logging.DEBUG if self.debug_mode else logging.INFO
        
        # Configuración básica
        logging.basicConfig(
            level=base_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        
        # Añadir filtro de datos sensibles al logger raíz
        root_logger = logging.getLogger()
        root_logger.addFilter(SensitiveDataFilter())
        
        # Configurar loggers específicos
        self._configure_sqlalchemy_logger()
        self._configure_email_loggers()
    
    def _configure_sqlalchemy_logger(self) -> None:
        """Configura el logger de SQLAlchemy."""
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        
        # En producción, solo mostrar errores de SQL
        if not self.debug_mode:
            sqlalchemy_logger.setLevel(logging.WARNING)
    
    def _configure_email_loggers(self) -> None:
        """Configura los loggers relacionados con email."""
        # Configurar logger de SMTP
        smtp_logger = logging.getLogger("smtplib")
        smtp_logger.setLevel(logging.DEBUG if self.debug_mode else logging.ERROR)
        
        # Configurar logger de email
        email_logger = logging.getLogger("email")
        email_logger.setLevel(logging.DEBUG if self.debug_mode else logging.ERROR)
    
    def get_logger(self, name: str) -> LoggerProtocol:
        """
        Obtiene un logger con el nombre especificado.
        
        Args:
            name: El nombre del logger.
            
        Returns:
            Un logger configurado.
        """
        return logging.getLogger(name)


# Instancia global de la fábrica de loggers
logger_factory = StandardLoggerFactory(debug_mode=settings.DEBUG)


def get_logger(name: str) -> LoggerProtocol:
    """
    Función de conveniencia para obtener un logger.
    
    Args:
        name: El nombre del logger.
        
    Returns:
        Un logger configurado.
    """
    return logger_factory.get_logger(name)
