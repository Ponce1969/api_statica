"""
Protocolos para middleware HTTP.

Este módulo define las interfaces para los componentes de middleware HTTP
siguiendo los principios de Clean Architecture y el patrón de puertos y adaptadores.
"""

from typing import Any, Awaitable, Callable, Dict, Optional, Protocol, Set, TypeVar


class RequestResponseProtocol(Protocol):
    """Protocolo para objetos que tienen headers como diccionarios."""
    
    @property
    def headers(self) -> Dict[str, str]:
        """Obtiene los headers de la solicitud o respuesta."""
        ...


class RequestProtocol(RequestResponseProtocol, Protocol):
    """Protocolo para objetos de solicitud HTTP."""
    
    @property
    def method(self) -> str:
        """Obtiene el método HTTP de la solicitud."""
        ...
    
    @property
    def url(self) -> Any:
        """Obtiene la URL de la solicitud."""
        ...
    
    @property
    def client(self) -> Any:
        """Obtiene información del cliente que realizó la solicitud."""
        ...


class ResponseProtocol(RequestResponseProtocol, Protocol):
    """Protocolo para objetos de respuesta HTTP."""
    
    @property
    def status_code(self) -> int:
        """Obtiene el código de estado HTTP de la respuesta."""
        ...


# Definición de tipos para mejorar la legibilidad
TRequest = TypeVar("TRequest", bound=RequestProtocol)
TResponse = TypeVar("TResponse", bound=ResponseProtocol)


class MiddlewareProtocol(Protocol):
    """Protocolo para middleware HTTP."""
    
    async def process_request(
        self, 
        request: RequestProtocol, 
        call_next: Callable[[RequestProtocol], Awaitable[ResponseProtocol]]
    ) -> ResponseProtocol:
        """
        Procesa una solicitud HTTP.
        
        Args:
            request: La solicitud HTTP a procesar.
            call_next: Función para llamar al siguiente middleware en la cadena.
            
        Returns:
            La respuesta HTTP resultante.
        """
        ...


class MiddlewareFactoryProtocol(Protocol):
    """Protocolo para fábricas de middleware HTTP."""
    
    def get_middlewares(self) -> Set[MiddlewareProtocol]:
        """
        Obtiene los middlewares configurados.
        
        Returns:
            Un conjunto de middlewares configurados.
        """
        ...
