"""Entidad de dominio ContactRequest.

Representa una solicitud de contacto enviada desde el frontend. Aún no se persiste en
base de datos, pero está preparada para ello.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.domain.exceptions.base import StructuralValidationError
from app.domain.models.base import AuditableEntity


class ContactRequest(AuditableEntity):
    """Entidad que representa una solicitud de contacto."""

    __slots__ = (
        "full_name",
        "email",
        "phone",
        "message",
        "_id",
        "created_at",
        "updated_at",
    )

    full_name: str
    email: str
    phone: str | None
    message: str

    def __init__(
        self,
        full_name: str,
        email: str,
        message: str,
        phone: str | None = None,
        *,
        entity_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(entity_id, created_at, updated_at)

        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.message = message

        self.validate()

    # ---------------------------------------------------------------------
    # Validaciones
    # ---------------------------------------------------------------------
    def validate(self) -> None:  # noqa: D401
        """Validaciones estructurales y de negocio."""
        errors: dict[str, str] = {}

        if not self.full_name.strip():
            errors["full_name"] = "El nombre no puede estar vacío"
        if "@" not in self.email:
            errors["email"] = "Email inválido"
        if not self.message.strip():
            errors["message"] = "El mensaje no puede estar vacío"
        if len(self.message) > 1000:
            errors["message"] = "El mensaje no puede exceder 1000 caracteres"

        if errors:
            # Distinguimos entre errores estructurales y de negocio de forma simple
            raise StructuralValidationError("Errores de validación", errors)

    # ---------------------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------------------
    def __str__(self) -> str:  # noqa: D401
        return (
            f"ContactRequest(id={self.id}, name={self.full_name}, email={self.email})"
        )
