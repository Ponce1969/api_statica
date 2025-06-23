"""Repositorio de ContactRequest (implementaciones en memoria y SQLAlchemy)."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Final
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ContactRequest as ContactRequestORM
from app.domain.models.contact_request import ContactRequest
from app.domain.repositories.contact_request import IContactRequestRepository

__all__ = ["InMemoryContactRequestRepository", "SQLAlchemyContactRequestRepository"]


class InMemoryContactRequestRepository(IContactRequestRepository):
    """Simple almacenamiento en lista, útil para la versión sin DB."""

    def __init__(self) -> None:  # noqa: D401
        self._items: Final[list[ContactRequest]] = []

    async def create(self, contact_request: ContactRequest) -> ContactRequest:  # noqa: D401
        self._items.append(contact_request)
        return contact_request

    async def list(self) -> Sequence[ContactRequest]:  # noqa: D401
        return list(self._items)


class SQLAlchemyContactRequestRepository(IContactRequestRepository):
    """Implementación del repositorio usando SQLAlchemy para persistencia."""

    def __init__(self, db: AsyncSession) -> None:  # noqa: D401
        self.db = db
        self.model = ContactRequestORM

    def _to_domain(self, orm_model: ContactRequestORM) -> ContactRequest:
        """Convierte un modelo ORM a modelo de dominio."""
        return ContactRequest(
            full_name=orm_model.full_name,
            email=orm_model.email,
            message=orm_model.message,
            phone=orm_model.phone,
            entity_id=orm_model.id,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    async def create(self, contact_request: ContactRequest) -> ContactRequest:
        """Guarda una solicitud de contacto en la base de datos."""
        # Creamos una instancia del ORM
        contact_request_orm = self.model(
            id=contact_request.id,
            full_name=contact_request.full_name,
            email=contact_request.email,
            phone=contact_request.phone,
            message=contact_request.message,
            is_processed=False,
            created_at=contact_request.created_at,
            updated_at=contact_request.updated_at,
        )
        
        # La añadimos a la sesión y hacemos flush para generar el ID
        self.db.add(contact_request_orm)
        await self.db.flush()
        
        # Devolvemos un objeto de dominio
        return self._to_domain(contact_request_orm)
    
    async def list(self) -> Sequence[ContactRequest]:
        """Devuelve todas las solicitudes de contacto."""
        result = await self.db.execute(select(self.model))
        return [self._to_domain(orm) for orm in result.scalars().all()]
    
    async def get_by_id(self, entity_id: UUID) -> ContactRequest | None:
        """Obtiene una solicitud de contacto por su ID."""
        contact_request_orm = await self.db.get(self.model, entity_id)
        if not contact_request_orm:
            return None
        return self._to_domain(contact_request_orm)
