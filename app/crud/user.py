from collections.abc import Sequence
from datetime import UTC, date, datetime
from typing import Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User as UserORM
from app.domain.exceptions.base import EntityNotFoundError
from app.domain.models.user import User
from app.domain.repositories.base import IUserRepository

# Type alias for accepted query filter values
AcceptedQueryTypes = str | int | bool | UUID | datetime | date | None


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.model = UserORM

    def _to_domain(self, user_orm: UserORM) -> User:
        return User(
            entity_id=user_orm.id,
            email=user_orm.email,
            full_name=user_orm.full_name or "",
            is_active=user_orm.is_active,
            is_superuser=bool(getattr(user_orm, 'is_superuser', False)),
        )

    async def create(self, user: User) -> User:
        user_orm = UserORM(
            email=user.email,
            hashed_password=getattr(user, 'hashed_password', None),
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
        self.db.add(user_orm)
        await self.db.commit()
        await self.db.refresh(user_orm)
        return self._to_domain(user_orm)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(self.model).where(self.model.email == email)
        )
        user_orm = result.scalars().first()
        return self._to_domain(user_orm) if user_orm else None

    async def get(self, entity_id: UUID) -> User | None:
        """Obtiene un usuario por su ID."""
        user_orm = await self.db.get(self.model, entity_id)
        if not user_orm:
            return None
        return self._to_domain(user_orm)

    async def list(self) -> Sequence[User]:
        """Lista todos los usuarios."""
        result = await self.db.execute(select(self.model))
        return [self._to_domain(user_orm) for user_orm in result.scalars().all()]

    async def get_by_field(
        self, field_name: str, value: AcceptedQueryTypes
    ) -> User | None:
        """Obtiene un usuario por un campo específico."""
        if not hasattr(self.model, field_name):
            model_name = self.model.__name__
            raise ValueError(
                f"El campo {field_name} no existe "
                f"en el modelo {model_name}"
            )
        query = select(self.model).where(getattr(self.model, field_name) == value)
        result = await self.db.execute(query)
        user_orm = result.scalar_one_or_none()
        return self._to_domain(user_orm) if user_orm else None

    async def filter_by(self, **filters: AcceptedQueryTypes) -> Sequence[User]:
        """Filtra usuarios basados en criterios."""
        query = select(self.model)
        for field, value in filters.items():
            if not hasattr(self.model, field):
                model_name = self.model.__name__
                raise ValueError(
                    f"El campo {field} no existe "
                    f"en el modelo {model_name}"
                )
            query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return [self._to_domain(user_orm) for user_orm in result.scalars().all()]

    async def get_active(self) -> Sequence[User]:
        result = await self.db.execute(
            select(self.model).where(self.model.is_active)
        )
        users_orm = result.scalars().all()
        return [self._to_domain(user_orm) for user_orm in users_orm]

    async def get_by_role(self, role_id: UUID) -> Sequence[User]:
        result = await self.db.execute(
            select(self.model).where(self.model.roles.any(id=role_id))
        )
        users_orm = result.scalars().all()
        return [self._to_domain(user_orm) for user_orm in users_orm]

    async def update_last_login(self, user_id: UUID) -> User:
        result = await self.db.execute(
            select(self.model).where(self.model.id == user_id)
        )
        user_orm = result.scalars().first()
        if not user_orm:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")

        user_orm.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(user_orm)
        return self._to_domain(user_orm)

    async def count(self, **filters: AcceptedQueryTypes) -> int:
        raise NotImplementedError()

    async def exists(self, **filters: AcceptedQueryTypes) -> bool:
        raise NotImplementedError()

    async def update(self, entity: User) -> User:
        # Implementación de update pendiente, similar a otros repositorios
        user_orm = await self.db.get(self.model, entity.id)
        if not user_orm:
            raise EntityNotFoundError(entity="User", entity_id=str(entity.id))

        # Actualizar campos. Asegúrate de que los campos de 'entity' (User de dominio)
        # se mapeen correctamente a 'user_orm' (UserORM)
        user_orm.email = entity.email
        user_orm.full_name = entity.full_name
        user_orm.is_active = entity.is_active
        # user_orm.is_superuser = entity.is_superuser # Si es necesario
        # Si hashed_password se puede actualizar aquí, añádelo.
        # Normalmente, la actualización de contraseña tiene un flujo dedicado.
        # user_orm.hashed_password = entity.hashed_password 

        await self.db.commit()
        await self.db.refresh(user_orm)
        return self._to_domain(user_orm)

    async def delete(self, entity_id: UUID) -> None:
        user_orm = await self.db.get(self.model, entity_id)
        if not user_orm:
            raise EntityNotFoundError(entity="User", entity_id=str(entity_id))
        await self.db.delete(user_orm)
        await self.db.commit()
