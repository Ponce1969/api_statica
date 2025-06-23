from collections.abc import Sequence
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Role
from app.domain.exceptions.base import EntityNotFoundError  # Modelo de Dominio
from app.domain.models.role import Role as RoleDomain
from app.domain.repositories.base import IRoleRepository

# Type alias for accepted query filter values
AcceptedQueryTypes = str | float | bool | UUID | datetime | date | None


class RoleRepositoryImpl(IRoleRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.model = Role # Modelo ORM

    def _to_domain(self, role_orm: Role) -> RoleDomain:
        """Convierte un modelo ORM Role a un modelo de dominio RoleDomain."""
        if role_orm is None:
            raise ValueError("role_orm no puede ser None para la conversión a dominio")
        return RoleDomain(
            entity_id=role_orm.id,
            name=role_orm.name,
            description=role_orm.description,
            # permissions y updated_at no están en el modelo de dominio Role
            created_at=role_orm.created_at
        )

    async def get(self, entity_id: UUID) -> RoleDomain | None:
        query = select(self.model).where(self.model.id == entity_id)
        result = await self.db.execute(query)
        role_orm = result.scalar_one_or_none()
        return self._to_domain(role_orm) if role_orm else None

    async def list(self) -> Sequence[RoleDomain]:
        query = select(self.model)
        result = await self.db.execute(query)
        return [self._to_domain(role_orm) for role_orm in result.scalars().all()]

    async def create(self, entity: RoleDomain) -> RoleDomain:
        # Convertir de dominio a ORM
        # El ID se toma directamente de la entidad de dominio (entity.id),
        # que garantiza que siempre sea un UUID.
        # `RoleDomain` hereda `id` de `Entity`,
        # y `Entity` asegura que `id` sea un UUID
        # (ya sea el `entity_id` proporcionado o uno nuevo).
        # permissions no se maneja aquí directamente si no está
        # en el constructor de RoleORM o RoleDomain
        role_orm_data: dict[str, Any] = {
            "name": entity.name,
            "description": entity.description,
            "id": entity.id
        }
        
        role_orm = self.model(**role_orm_data)
        self.db.add(role_orm)
        await self.db.commit()
        await self.db.refresh(role_orm)
        return self._to_domain(role_orm)

    async def update(self, entity: RoleDomain) -> RoleDomain:
        role_orm = await self.db.get(self.model, entity.id)
        if not role_orm:
            # Asegúrate que EntityNotFoundError pueda tomar estos argumentos o ajústalo
            raise EntityNotFoundError(entity="Rol", entity_id=entity.id)

        role_orm.name = entity.name
        # Asegurar que no sea None si el ORM no lo permite
        role_orm.description = entity.description or ""
        # role_orm.permissions = entity.permissions # Omitir si no se maneja
        # updated_at se manejará automáticamente si está configurado en el modelo ORM

        await self.db.commit()
        await self.db.refresh(role_orm)
        return self._to_domain(role_orm)

    # Ajustado a la interfaz IRepository
    async def delete(self, entity_id: UUID) -> None:
        role_orm = await self.db.get(self.model, entity_id)
        if not role_orm:
            raise EntityNotFoundError(entity="Rol", entity_id=str(entity_id))
        await self.db.delete(role_orm)
        await self.db.commit()

    async def count(self, **filters: str | float | bool | UUID | datetime | date | None) -> int:
        query = select(self.model)
        for field, value in filters.items():
            if not hasattr(self.model, field):
                model_name = self.model.__name__
                raise ValueError(
                    f"El campo '{field}' no existe en el modelo {model_name}"
                )
            query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def exists(self, **filters: str | float | bool | UUID | datetime | date | None) -> bool:
        query = select(self.model)
        for field, value in filters.items():
            if not hasattr(self.model, field):
                model_name = self.model.__name__
                raise ValueError(
                    f"El campo '{field}' no existe en el modelo {model_name}"
                )
            query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_by_field(
        self, field_name: str, value: str | float | bool | UUID | datetime | date | None
    ) -> RoleDomain | None:
        # Implementación basada en la lógica de otros repositorios
        if not hasattr(self.model, field_name):
            # Opcional: devolver None o lanzar error específico
            # si el campo no es del modelo,
            # en lugar de un ValueError genérico.
            # Mantenemos ValueError por consistencia si el campo no existe.
            model_name = self.model.__name__
            raise ValueError(
                f"El campo '{field_name}' no existe "
                f"en el modelo {model_name}"
            )
        query = select(self.model).where(getattr(self.model, field_name) == value)
        result = await self.db.execute(query)
        role_orm = result.scalar_one_or_none()
        return self._to_domain(role_orm) if role_orm else None

    async def filter_by(self, **filters: str | float | bool | UUID | datetime | date | None) -> Sequence[RoleDomain]:
        query = select(self.model)
        for field, value in filters.items():
            if not hasattr(self.model, field):
                model_name = self.model.__name__
                raise ValueError(
                    f"El campo '{field}' no existe en el modelo {model_name}"
                )
            query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return [self._to_domain(role_orm) for role_orm in result.scalars().all()]

    async def get_by_name(self, name: str) -> RoleDomain | None:
        query = select(self.model).where(self.model.name == name)
        result = await self.db.execute(query)
        role_orm = result.scalar_one_or_none()
        return self._to_domain(role_orm) if role_orm else None

    async def get_default_roles(self) -> Sequence[RoleDomain]:
        # Asumiendo que los roles por defecto tienen un flag o nombres específicos
        # Esta es una implementación stub, necesitarás definir la lógica
        # Por ejemplo, si tienes un campo 'is_default' en tu modelo RoleORM:
        # query = select(self.model).where(self.model.is_default == True)
        # result = await self.db.execute(query)
        # return list(result.scalars().all())
        raise NotImplementedError("get_default_roles no implementado")

    async def get_by_permissions(
        self, permissions: Sequence[str]
    ) -> Sequence[RoleDomain]:
        # Esta lógica puede ser compleja y depende de cómo almacenes los permisos
        # Por ejemplo, si los permisos son una lista de strings en una columna JSON
        # o una relación many-to-many con una
        # tabla de Permisos.
        # query = select(self.model).where(
        #     self.model.permissions.contains(permissions)
        # ) 
        # Conceptual
        raise NotImplementedError("get_by_permissions no implementado")
