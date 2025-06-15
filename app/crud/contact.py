from typing import Any, Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete, update as sql_update

from app.database.models import Contact as ContactORM
from datetime import datetime, UTC # Asegúrate que UTC esté importado
from sqlalchemy import func, exists as sql_exists # Para count y exists

from app.domain.models.contact import Contact as ContactDomain # Importamos el modelo de dominio
from app.domain.repositories.base import IContactRepository
from app.domain.exceptions.base import EntityNotFoundError


class ContactRepository(IContactRepository):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = ContactORM # Modelo SQLAlchemy

    def _to_domain(self, contact_orm: ContactORM) -> ContactDomain:
        """Convierte un modelo ORM ContactORM a un modelo de dominio ContactDomain."""
        if contact_orm is None:
            # Esto no debería ocurrir si se llama después de una verificación de existencia,
            # pero es una salvaguarda.
            raise ValueError("contact_orm no puede ser None para la conversión a dominio")
        
        # Mapeo de ContactORM a Contact (dominio)
        return ContactDomain(
            entity_id=contact_orm.id,
            full_name=contact_orm.name,  # Corregido de full_name a name según el ORM
            email=contact_orm.email,
            # phone no está en el constructor de ContactDomain
            message=contact_orm.message,
            is_read=contact_orm.is_read,
            created_at=contact_orm.created_at,
            updated_at=contact_orm.updated_at
        )

    async def get(self, entity_id: UUID) -> Optional[ContactDomain]:
        contact_orm = await self.db.get(self.model, entity_id)
        if not contact_orm:
            return None
        return self._to_domain(contact_orm)

    async def list(self) -> Sequence[ContactDomain]:
        result = await self.db.execute(select(self.model))
        return [self._to_domain(contact_orm) for contact_orm in result.scalars().all()]

    async def create(self, entity: ContactDomain) -> ContactDomain:
        # Convertir de dominio a ORM
        # Asegúrate de que los campos coincidan con tu modelo ContactORM
        contact_orm_data = {
            "name": entity.full_name,
            "email": entity.email,
            "message": entity.message,
            "is_read": entity.is_read
            # No incluimos id aquí si es autogenerado por la BD o si se pasa explícitamente
            # y se maneja de forma diferente en tu modelo ORM.
            # Si tu ContactORM espera un 'id' en la creación y el 'entity.id' del dominio
            # es el que se debe usar, entonces inclúyelo:
            # "id": entity.id,
        }
        # Si el ID se genera en el dominio y debe pasarse al ORM:
        if entity.id:
             contact_orm_data["id"] = entity.id

        contact_orm = self.model(**contact_orm_data)
        self.db.add(contact_orm)
        await self.db.commit()
        await self.db.refresh(contact_orm)
        return self._to_domain(contact_orm)

    async def update(self, entity: ContactDomain) -> ContactDomain:
        contact_orm = await self.db.get(self.model, entity.id)
        if not contact_orm:
            raise EntityNotFoundError(entity="Contact", entity_id=str(entity.id))
        
        contact_orm.name = entity.full_name
        contact_orm.email = entity.email
        contact_orm.message = entity.message
        contact_orm.is_read = entity.is_read
        # El campo updated_at debería actualizarse automáticamente si está configurado
        # en el modelo ORM con onupdate=datetime.now(UTC) o similar.
        # Si no, deberías hacerlo manualmente: contact_orm.updated_at = datetime.now(UTC)
        
        await self.db.commit()
        await self.db.refresh(contact_orm)
        return self._to_domain(contact_orm)

    async def delete(self, entity_id: UUID) -> None:
        contact_orm = await self.db.get(self.model, entity_id)
        if not contact_orm:
            raise EntityNotFoundError(entity="Contact", entity_id=str(entity_id))
        await self.db.delete(contact_orm)
        await self.db.commit()

    async def get_by_email(self, email: str) -> Sequence[ContactDomain]:
        query = select(self.model).where(self.model.email == email)
        result = await self.db.execute(query)
        contacts_orm = result.scalars().all()
        return [self._to_domain(contact_orm) for contact_orm in contacts_orm]

    async def get_by_field(self, field_name: str, value: Any) -> Optional[ContactDomain]:
        if not hasattr(self.model, field_name):
            raise ValueError(f"El campo '{field_name}' no existe en el modelo {self.model.__name__}")
        query = select(self.model).where(getattr(self.model, field_name) == value)
        result = await self.db.execute(query)
        contact_orm = result.scalar_one_or_none()
        return self._to_domain(contact_orm) if contact_orm else None

    async def filter_by(self, **filters: Any) -> Sequence[ContactDomain]:
        query = select(self.model)
        for field, value in filters.items():
            if not hasattr(self.model, field):
                raise ValueError(f"El campo '{field}' no existe en el modelo {self.model.__name__}")
            query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return [self._to_domain(contact_orm) for contact_orm in result.scalars().all()]

    # Métodos de IRepository que necesitan implementación o ya están (como get, list, create, update, delete, get_by_field, filter_by)

    async def count(self, **filters: Any) -> int:
        # Construir la consulta con filtros, similar a filter_by pero con func.count
        query = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            if not hasattr(self.model, field):
                # Opcionalmente, podrías querer que esto devuelva 0 o lance un error más específico
                raise ValueError(f"El campo '{field}' no existe en el modelo {self.model.__name__} para contar")
            query = query.where(getattr(self.model, field) == value)
        
        result = await self.db.execute(query)
        count = result.scalar_one_or_none()
        return count if count is not None else 0

    async def exists(self, **criteria: Any) -> bool:
        # Construir la consulta con criterios, similar a filter_by pero con select(self.model.id).exists()
        # o una consulta más optimizada si tu ORM lo permite.
        query = select(self.model.id) # Solo necesitamos saber si existe, no traer toda la entidad
        for field, value in criteria.items():
            if not hasattr(self.model, field):
                raise ValueError(f"El campo '{field}' no existe en el modelo {self.model.__name__} para verificar existencia")
            query = query.where(getattr(self.model, field) == value)
        
        # Usar exists() de SQLAlchemy para una consulta más eficiente
        exists_query = select(sql_exists(query))
        result = await self.db.execute(exists_query)
        return bool(result.scalar_one())

    # Métodos específicos de IContactRepository

    async def get_unread(self) -> Sequence[ContactDomain]:
        query = select(self.model).where(self.model.is_read == False)
        result = await self.db.execute(query)
        contacts_orm = result.scalars().all()
        return [self._to_domain(contact_orm) for contact_orm in contacts_orm]

    async def mark_as_read(self, contact_id: UUID) -> ContactDomain:
        contact_orm = await self.db.get(self.model, contact_id)
        if not contact_orm:
            raise EntityNotFoundError(entity="Contact", entity_id=str(contact_id))
        
        if not contact_orm.is_read:
            # Actualizar el campo y 'updated_at'
            # Usar la instancia ORM directamente es más común si la sesión está activa
            contact_orm.is_read = True
            contact_orm.updated_at = datetime.now(UTC) # Asegurar que UTC esté importado y datetime también
            self.db.add(contact_orm) # Marcar para la sesión que el objeto ha cambiado
            await self.db.commit()
            await self.db.refresh(contact_orm)
        
        return self._to_domain(contact_orm)

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> Sequence[ContactDomain]:
        # Asegúrate que start_date y end_date sean conscientes de la zona horaria si tu BD lo requiere
        # o que created_at en la BD también lo sea.
        query = select(self.model).where(
            self.model.created_at >= start_date,
            self.model.created_at <= end_date
        ).order_by(self.model.created_at)
        result = await self.db.execute(query)
        contacts_orm = result.scalars().all()
        return [self._to_domain(contact_orm) for contact_orm in contacts_orm]
