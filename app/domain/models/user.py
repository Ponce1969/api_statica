from datetime import UTC, datetime
from uuid import UUID

from app.domain.exceptions.base import StructuralValidationError
from app.domain.models.base import AuditableEntity


class User(AuditableEntity):
    """Entidad de dominio que representa a un usuario del sistema."""

    __slots__ = (
        "email", "full_name", "is_active", "is_superuser", "role_ids",
        "_id", "created_at", "updated_at"
    )

    def __init__(
        self,
        email: str,
        full_name: str,
        entity_id: UUID | None = None,
        is_active: bool = True,
        is_superuser: bool = False,
        role_ids: set[UUID] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(entity_id, created_at, updated_at)

        errors = {}

        if not email or "@" not in email:
            errors["email"] = "El email es requerido y debe ser válido"

        if not full_name.strip():
            errors["full_name"] = "El nombre completo no puede estar vacío"

        if errors:
            raise StructuralValidationError("Error de validación al crear usuario", errors)

        self.email = email
        self.full_name = full_name
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.role_ids = role_ids or set()

    def assign_role(self, role_id: UUID) -> None:
        self.role_ids.add(role_id)

    def remove_role(self, role_id: UUID) -> None:
        self.role_ids.discard(role_id)

    def has_role(self, role_id: UUID) -> bool:
        return role_id in self.role_ids

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def update_email(self, new_email: str) -> None:
        if not new_email or "@" not in new_email:
            raise StructuralValidationError(
                "Email inválido", {"email": "Debe ser un email válido"}
            )
        self.email = new_email
        self.updated_at = datetime.now(UTC)

    def update_full_name(self, new_full_name: str) -> None:
        if not new_full_name.strip():
            raise StructuralValidationError(
                "Nombre inválido", {"full_name": "No puede estar vacío"}
            )
        self.full_name = new_full_name
        self.updated_at = datetime.now(UTC)
