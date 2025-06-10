"""
Modelo de dominio para la entidad Usuario.
Este modelo representa el concepto de usuario en el dominio de la aplicación,
independientemente de la persistencia o infraestructura.
"""
from datetime import datetime
from typing import List, Optional, Set
from uuid import UUID

from app.domain.models.base import AuditableEntity


class User(AuditableEntity):
    """Entidad de dominio que representa a un usuario del sistema."""
    
    email: str
    full_name: str
    is_active: bool
    role_ids: Set[UUID]  # IDs de los roles asignados al usuario
    
    def __init__(
        self,
        email: str,
        full_name: str,
        entity_id: Optional[UUID] = None,
        is_active: bool = True,
        role_ids: Optional[Set[UUID]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        super().__init__(entity_id, created_at, updated_at)
        self.email = email
        self.full_name = full_name
        self.is_active = is_active
        self.role_ids = role_ids or set()
    
    def assign_role(self, role_id: UUID) -> None:
        """Asigna un rol al usuario."""
        self.role_ids.add(role_id)
    
    def remove_role(self, role_id: UUID) -> None:
        """Elimina un rol del usuario."""
        self.role_ids.discard(role_id)
    
    def has_role(self, role_id: UUID) -> bool:
        """Verifica si el usuario tiene un rol específico."""
        return role_id in self.role_ids
    
    def deactivate(self) -> None:
        """Desactiva al usuario."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Activa al usuario."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def update_email(self, new_email: str) -> None:
        """Actualiza el email del usuario."""
        self.email = new_email
        self.updated_at = datetime.utcnow()
    
    def update_full_name(self, new_full_name: str) -> None:
        """Actualiza el nombre completo del usuario."""
        self.full_name = new_full_name
        self.updated_at = datetime.utcnow()
