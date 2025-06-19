"""
Excepciones base del dominio de la aplicación.

Estas excepciones representan errores específicos del dominio y son independientes
de la infraestructura subyacente (como SQL, HTTP, etc).
"""
from __future__ import annotations

from uuid import UUID


class DomainError(Exception):
    """Excepción base para todas las excepciones del dominio."""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
        
    def __str__(self) -> str:
        return self.message
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={repr(self.message)})"


class EntityNotFoundError(DomainError):
    """Se lanza cuando una entidad no se encuentra en el sistema."""
    
    def __init__(self, entity: str, entity_id: UUID | str | int) -> None:
        self.entity = entity
        self.entity_id = entity_id
        message = f"{entity} con id {entity_id} no encontrado."
        super().__init__(message)
        
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f"{class_name}(entity={repr(self.entity)}, "
            f"entity_id={repr(self.entity_id)})"
        )


class ValidationError(DomainError):
    """Se lanza cuando falla la validación de datos de una entidad."""
    
    def __init__(self, message: str, errors: dict[str, str] | None = None) -> None:
        self.errors = errors or {}
        super().__init__(message)
        
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(message={repr(self.message)}, errors={repr(self.errors)})"


class BusinessRuleViolationError(DomainError):
    """Se lanza cuando se viola una regla de negocio."""
    
    def __init__(self, rule: str) -> None:
        self.rule = rule
        message = f"Regla de negocio violada: {rule}"
        super().__init__(message)
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(rule={repr(self.rule)})"


class UnauthorizedOperationError(DomainError):
    """Se lanza cuando un usuario intenta realizar una operación para la que no tiene
    permiso.
    """
    
    def __init__(self, operation: str, reason: str | None = None) -> None:
        self.operation = operation
        self.reason = reason
        message = f"Operación no autorizada: {operation}"
        if reason:
            message += f". Razón: {reason}"
        super().__init__(message)
        
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return (
            f"{class_name}(operation={repr(self.operation)}, "
            f"reason={repr(self.reason)})"
        )


class StructuralValidationError(ValidationError):
    """Se lanza cuando fallan validaciones estructurales.
    
    Para datos faltantes o formato incorrecto.
    """
    
    def __init__(
        self, 
        message: str = "Error en la estructura de los datos", 
        errors: dict[str, str] | None = None
    ) -> None:
        super().__init__(message, errors)


class BusinessValidationError(ValidationError):
    """Se lanza cuando fallan validaciones de reglas de negocio.
    
    Para valores inválidos según reglas de negocio.
    """
    
    def __init__(
        self, 
        message: str = "Error en las reglas de validación de negocio", 
        errors: dict[str, str] | None = None
    ) -> None:
        super().__init__(message, errors)
