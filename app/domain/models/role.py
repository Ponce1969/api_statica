"""
Modelo de dominio para la entidad Rol.
Este modelo representa el concepto de rol en el dominio de la aplicación,
independientemente de la persistencia o infraestructura.
"""
from datetime import UTC, datetime
from uuid import UUID

from app.domain.models.base import Entity


class Role(Entity):
    """Entidad de dominio que representa un rol en el sistema."""
    
    id: UUID
    name: str
    description: str | None
    created_at: datetime
    
    def __init__(
        self,
        name: str,
        description: str | None = None,
        entity_id: UUID | None = None,
        created_at: datetime | None = None
    ) -> None:
        super().__init__(entity_id)
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now(UTC)
    
    def update_description(self, new_description: str) -> None:
        """Actualiza la descripción del rol."""
        self.description = new_description
    
    def __str__(self) -> str:
        return f"Role(id={self.id}, name={self.name})"
