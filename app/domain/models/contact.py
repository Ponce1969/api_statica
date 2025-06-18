import time
from datetime import UTC, datetime
from uuid import UUID

from app.domain.exceptions.base import StructuralValidationError, ValidationError
from app.domain.models.base import AuditableEntity


class Contact(AuditableEntity):
    """Entidad de dominio que representa un contacto en el sistema."""

    __slots__ = (
        "full_name", "email", "message", "is_read",
        "_id", "created_at", "updated_at"
    )

    full_name: str
    email: str
    message: str
    is_read: bool

    def __init__(
        self,
        full_name: str,
        email: str,
        message: str,
        entity_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        is_read: bool = False
    ) -> None:
        super().__init__(entity_id, created_at, updated_at)

        if not full_name.strip():
            raise ValueError("El nombre no puede estar vacío")
        if not email or "@" not in email:
            raise ValueError("Email inválido")
        if not message.strip():
            raise ValueError("El mensaje no puede estar vacío")

        self.full_name = full_name
        self.email = email
        self.message = message
        self.is_read = is_read

        self.validate()

    def update_message(self, new_message: str) -> None:
        if not new_message.strip():
            raise ValueError("El mensaje no puede estar vacío")
        self.message = new_message
        # Forzar un pequeño delay para asegurar un timestamp diferente
        time.sleep(0.002)
        self.updated_at = datetime.now(UTC)

    def update_contact_info(self, name: str | None = None, email: str | None = None) -> None:
        if name is not None:
            if not name.strip():
                raise ValueError("El nombre no puede estar vacío")
            self.full_name = name

        if email is not None:
            if not email or "@" not in email:
                raise ValueError("Email inválido")
            self.email = email

        # Forzar un pequeño delay para asegurar un timestamp diferente
        time.sleep(0.002)
        self.updated_at = datetime.now(UTC)
        self.validate()

    def mark_as_read(self) -> None:
        if not self.is_read:
            self.is_read = True
            # Forzar un pequeño delay para asegurar un timestamp diferente
            time.sleep(0.002)
            self.updated_at = datetime.now(UTC)

    def mark_as_unread(self) -> None:
        if self.is_read:
            self.is_read = False
            # Forzar un pequeño delay para asegurar un timestamp diferente
            time.sleep(0.002)
            self.updated_at = datetime.now(UTC)

    def validate(self) -> None:
        errors = {}

        if not self.full_name or not self.full_name.strip():
            errors["full_name"] = "El nombre es requerido y no puede estar vacío"

        if not self.email:
            errors["email"] = "El email es requerido"
        elif "@" not in self.email:
            errors["email"] = "El email debe tener un formato válido"

        if not self.message or not self.message.strip():
            errors["message"] = "El mensaje es requerido y no puede estar vacío"

        if errors:
            raise StructuralValidationError(
                "Error de validación en el contacto", errors
            )

        business_errors = {}
        if self.message and len(self.message) > 1000:
            business_errors["message"] = "El mensaje no puede exceder los 1000 caracteres"

        if self.email.endswith(".test"):
            business_errors["email"] = "No se permiten emails de prueba"

        if business_errors:
            raise ValidationError("Error en reglas de negocio para el contacto", business_errors)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Contact):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"Contact(id={self.id}, full_name={self.full_name}, email={self.email})"

