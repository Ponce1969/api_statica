from datetime import datetime, UTC
from uuid import UUID

from app.domain.models.base import AuditableEntity
from app.domain.exceptions.base import StructuralValidationError


class Contact(AuditableEntity):
    """Entidad de dominio que representa un contacto enviado desde el formulario."""

    __slots__ = (
        "email", "message", "full_name", "is_read",
        "_id", "created_at", "updated_at"
    )

    def __init__(
        self,
        email: str,
        message: str,
        full_name: str,
        is_read: bool = False,
        entity_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(entity_id, created_at, updated_at)

        errors = {}

        if not email or "@" not in email:
            errors["email"] = "El email es requerido y debe ser válido"

        if not full_name.strip():
            errors["full_name"] = "El nombre completo no puede estar vacío"

        if not message.strip():
            errors["message"] = "El mensaje no puede estar vacío"

        if errors:
            raise StructuralValidationError("Error de validación al crear contacto", errors)

        self.email = email
        self.message = message
        self.full_name = full_name
        self.is_read = is_read


