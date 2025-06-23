"""Puerto del dominio para manejar solicitudes de contacto."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.models.contact_request import ContactRequest

__all__ = ["IContactRequestRepository"]


class IContactRequestRepository(ABC):
    """Contrato requerido por la capa de aplicación para persistir ContactRequest."""

    @abstractmethod
    async def create(self, contact_request: ContactRequest) -> ContactRequest:  # noqa: D401
        """Persistir y devolver la solicitud almacenada."""

    @abstractmethod
    async def list(self) -> Sequence[ContactRequest]:  # noqa: D401
        """Listar todas las solicitudes (útil para tests o administración)."""
