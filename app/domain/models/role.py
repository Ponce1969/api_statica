"""
Modelo de dominio para la entidad Rol.
Este modelo representa el concepto de rol en el dominio de la aplicación,
independientemente de la persistencia o infraestructura.
"""
from datetime import UTC, datetime
from uuid import UUID

from app.domain.models.base import AuditableEntity


class Role(AuditableEntity):
    """Entidad de dominio que representa un rol en el sistema."""
    
    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime | None
    
    def __init__(
        self,
        name: str,
        description: str | None = None,
        id: UUID | None = None, # Cambiado de entity_id a id
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ) -> None:
        super().__init__(id, created_at, updated_at)
        self.name = name
        self.description = description
    
    def update_description(self, new_description: str) -> None:
        """Actualiza la descripción del rol."""
        self.description = new_description
    
    def __str__(self) -> str:
        return f"Role(id={self.id}, name={self.name})"
