from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select, update as sqlalchemy_update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.base import EntityNotFoundError
from app.database.models import Role
from app.domain.repositories.base import IRoleRepository

class RoleRepositoryImpl(IRoleRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.model = Role

    async def get(self, entity_id: UUID) -> Optional[Role]:
        query = select(self.model).where(self.model.id == entity_id)
        result = await self.db.execute(query)
        role_orm = result.scalar_one_or_none()
        return role_orm

    async def list(self) -> list[Role]:
        query = select(self.model)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: Role) -> Role:
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity: Role) -> Role:
        query = select(self.model).where(self.model.id == entity.id)
        result = await self.db.execute(query)
        role_orm = result.scalar_one_or_none()
        if not role_orm:
            raise EntityNotFoundError("Role", entity.id)

        # Actualizar campos
        role_orm.name = entity.name
        role_orm.description = entity.description

        self.db.add(role_orm)
        await self.db.commit()
        await self.db.refresh(role_orm)
        return role_orm

    async def delete(self, entity_id: UUID) -> None:
        query = select(self.model).where(self.model.id == entity_id)
        result = await self.db.execute(query)
        role_orm = result.scalar_one_or_none()
        if not role_orm:
            raise EntityNotFoundError("Role", entity_id)

        await self.db.delete(role_orm)
        await self.db.commit()

    async def count(self, **filters: Any) -> int:
        query = select(self.model)
        # Aquí podrías aplicar filtros si quieres
        result = await self.db.execute(query)
        roles = result.scalars().all()
        return len(roles)

    async def exists(self, **filters: Any) -> bool:
        query = select(self.model)
        # Aquí podrías aplicar filtros si quieres
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        return role is not None

    async def get_by_field(self, field_name: str, value: Any) -> Optional[Role]:
        # Implementación basada en la lógica de otros repositorios
        if not hasattr(self.model, field_name):
            # Opcionalmente, podrías querer que esto devuelva None o lance un error más específico
            # si el campo no es parte del modelo, en lugar de un ValueError genérico.
            # Por ahora, mantenemos la consistencia con el ValueError si el campo no existe.
            raise ValueError(f"El campo '{field_name}' no existe en el modelo {self.model.__name__}")
        query = select(self.model).where(getattr(self.model, field_name) == value)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def filter_by(self, **filters: Any) -> list[Role]:
        query = select(self.model)
        for field, value in filters.items():
            if not hasattr(self.model, field):
                raise ValueError(f"El campo '{field}' no existe en el modelo {self.model.__name__}")
            query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Optional[Role]:
        query = select(self.model).where(self.model.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_default_roles(self) -> Sequence[Role]:
        # Asumiendo que los roles por defecto tienen un flag o nombres específicos
        # Esta es una implementación stub, necesitarás definir la lógica
        # Por ejemplo, si tienes un campo 'is_default' en tu modelo RoleORM:
        # query = select(self.model).where(self.model.is_default == True)
        # result = await self.db.execute(query)
        # return list(result.scalars().all())
        raise NotImplementedError("get_default_roles no implementado")

    async def get_by_permissions(self, permissions: Sequence[str]) -> Sequence[Role]:
        # Esta lógica puede ser compleja y depende de cómo almacenes los permisos
        # Por ejemplo, si los permisos son una lista de strings en una columna JSON
        # o una relación many-to-many con una tabla de Permisos.
        # query = select(self.model).where(self.model.permissions.contains(permissions)) # Ejemplo conceptual
        raise NotImplementedError("get_by_permissions no implementado")
