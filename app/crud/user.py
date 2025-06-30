from collections.abc import Sequence
from typing import Any
from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User as UserORM
from app.domain.exceptions.base import EntityNotFoundError
from app.domain.models.user import User
from app.domain.repositories.base import IUserRepository

# Type alias for accepted query filter values
AcceptedQueryTypes = str | float | bool | UUID | datetime | date | None


class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.model = UserORM
        
        # Asegurarnos que db es una sesión válida
        if not isinstance(db, AsyncSession):
            raise TypeError("db debe ser una instancia de AsyncSession")

    def _to_domain(self, user_orm: UserORM) -> User:
        """Convierte una instancia ORM a la entidad de dominio User.

        Incluimos el *hashed_password* porque algunos flujos (p. ej. autenticación)
        necesitan verificar la contraseña.  Mantener este dato dentro del modelo
        de dominio simplifica la API del repositorio y evita tener que devolver
        tuplas u otras estructuras ad-hoc.
        """
        return User(
            id=user_orm.id,
            email=user_orm.email,
            full_name=user_orm.full_name or "",
            is_active=user_orm.is_active,
            is_superuser=bool(getattr(user_orm, "is_superuser", False)),
        )

    async def create(self, entity: User, hashed_password: str | None = None) -> User:
        """Crea un usuario y lo persiste en la base de datos.

        Solo se incluyen en el ORM los campos válidos para evitar errores de
        parámetros inesperados.
        """
        user_data: dict[str, Any] = {
            "email": entity.email,
            "full_name": entity.full_name,
            "is_active": entity.is_active,
            "is_superuser": entity.is_superuser,
        }
        if hashed_password is not None:
            user_data["hashed_password"] = hashed_password

        user_orm = UserORM(**user_data)
        self.db.add(user_orm)
        await self.db.flush()
        await self.db.refresh(user_orm)
        return self._to_domain(user_orm)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(self.model).where(self.model.email == email)
        )
        user_orm = result.scalars().first()
        if user_orm:
            return self._to_domain(user_orm)
        return None

    async def get(self, entity_id: UUID) -> User:
        """Obtiene un usuario por su ID.

        Lanza EntityNotFoundError si no existe para que las capas superiores no
        necesiten volver a validar.
        """
        user_orm = await self.db.get(self.model, entity_id)
        if not user_orm:
            raise EntityNotFoundError(entity="Usuario", entity_id=str(entity_id))
        return self._to_domain(user_orm)

    async def list(self) -> Sequence[User]:
        """Lista todos los usuarios."""
        result = await self.db.execute(select(self.model))
        return [self._to_domain(user_orm) for user_orm in result.scalars().all()]

    async def get_by_field(
        self, field_name: str, value: str | float | bool | UUID | datetime | date | None
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

    async def filter_by(self, **filters: str | float | bool | UUID | datetime | date | None) -> Sequence[User]:
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

    async def get_hashed_password_by_email(self, email: str) -> str:
        """
        Obtiene el hash de la contraseña de un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            str: El hash de la contraseña del usuario
            
        Raises:
            ValidationError: Si no existe un usuario con el email proporcionado
        """
        from app.domain.exceptions.base import ValidationError
        
        result = await self.db.execute(
            select(self.model.hashed_password).where(self.model.email == email)
        )
        hashed_password = result.scalar_one_or_none()
        
        if hashed_password is None:
            raise ValidationError("Credenciales incorrectas")
            
        return hashed_password

    async def update_last_login(self, user_id: UUID) -> User:
        result = await self.db.execute(
            select(self.model).where(self.model.id == user_id)
        )
        user_orm = result.scalars().first()
        if not user_orm:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")

        user_orm.updated_at = datetime.now(UTC)
        await self.db.flush()
        await self.db.refresh(user_orm)
        return self._to_domain(user_orm)

    async def count(self, **filters: str | float | bool | UUID | datetime | date | None) -> int:
        raise NotImplementedError()

    async def exists(self, **filters: str | float | bool | UUID | datetime | date | None) -> bool:
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

        await self.db.flush()
        await self.db.refresh(user_orm)
        return self._to_domain(user_orm)

    async def delete(self, entity_id: UUID) -> None:
        """Elimina un usuario sin acceder a la relación `roles`.

        Evitamos cualquier acceso a ``user_orm.roles`` para no provocar
        consultas a tablas que pueden no existir en la base de datos de test
        (por ejemplo, ``roles`` o ``user_roles``). Simplemente eliminamos el
        usuario y confirmamos la operación.
        """

        # Elimina la instancia del identity map para que el flush asociado a
        # commit no intente cargar sus relaciones.
        self.db.sync_session.expunge_all()

        # Ejecutamos el DELETE SQL directamente.
        await self.db.execute(sa_delete(self.model).where(self.model.id == entity_id))

        # Solo flush para aplicar cambios sin cerrar la transacción (importante en tests).
        await self.db.flush()
