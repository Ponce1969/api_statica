from typing import Optional, Sequence, Any
from datetime import datetime, UTC
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.models import User as UserORM
from app.domain.repositories.base import IUserRepository
from app.domain.exceptions.base import EntityNotFoundError
from app.domain.models.user import User
from app.crud.base import BaseRepository


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
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

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(self.model).where(self.model.email == email)
        )
        user_orm = result.scalars().first()
        return self._to_domain(user_orm) if user_orm else None

    async def get(self, entity_id: UUID) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        user_orm = await self.db.get(self.model, entity_id)
        if not user_orm:
            return None
        return self._to_domain(user_orm)

    async def list(self) -> Sequence[User]:
        """Lista todos los usuarios."""
        result = await self.db.execute(select(self.model))
        return [self._to_domain(user_orm) for user_orm in result.scalars().all()]

    async def get_by_field(self, field_name: str, value: Any) -> Optional[User]:
        """Obtiene un usuario por un campo específico."""
        if not hasattr(self.model, field_name):
            raise ValueError(f"El campo {field_name} no existe en el modelo {self.model.__name__}")
        query = select(self.model).where(getattr(self.model, field_name) == value)
        result = await self.db.execute(query)
        user_orm = result.scalar_one_or_none()
        return self._to_domain(user_orm) if user_orm else None

    async def filter_by(self, **filters: Any) -> Sequence[User]:
        """Filtra usuarios basados en criterios."""
        query = select(self.model)
        for field, value in filters.items():
            if not hasattr(self.model, field):
                raise ValueError(f"El campo {field} no existe en el modelo {self.model.__name__}")
            query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return [self._to_domain(user_orm) for user_orm in result.scalars().all()]

    async def get_active(self) -> Sequence[User]:
        result = await self.db.execute(
            select(self.model).where(self.model.is_active == True)
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

    async def count(self, **filters: Any) -> int:
        raise NotImplementedError()

    async def exists(self, *args: Any, **kwargs: Any) -> bool:
        raise NotImplementedError()

    async def update(self, entity: User) -> User:
        raise NotImplementedError()
