"""
Modelos base del dominio.
Estos modelos son independientes de la infraestructura y representan las entidades
centrales de la aplicación y sus reglas de negocio.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


class Entity:
    """Clase base para todas las entidades del dominio.
    
    Una entidad es un objeto con identidad única que persiste a lo largo del tiempo.
    """
    id: UUID
    
    def __init__(self, entity_id: Optional[UUID] = None):
        self.id = entity_id or uuid4()
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)


class AggregateRoot(Entity):
    """Clase base para agregados del dominio.
    
    Un agregado es un conjunto de entidades y objetos de valor que se tratan como
    una unidad para cambios de datos. El agregado root es la entidad principal
    que garantiza la consistencia del agregado.
    """
    pass


class ValueObject:
    """Clase base para objetos de valor.
    
    Un objeto de valor es un objeto inmutable que se distingue solo por su valor,
    no por su identidad. Dos objetos de valor con los mismos valores son iguales.
    """
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))


class AuditableEntity(Entity):
    """Entidad con capacidad de auditoría.
    
    Extiende la entidad base para incluir campos de auditoría como
    fechas de creación y actualización.
    """
    created_at: datetime
    updated_at: Optional[datetime]
    
    def __init__(
        self, 
        entity_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(entity_id)
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
