"""
Servicio para la gestión de usuarios.

Contiene la lógica de negocio relacionada con usuarios, separada del acceso a datos
y de la presentación (API).
"""
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from app.domain.exceptions.base import EntityNotFoundError, ValidationError
from app.domain.models.user import User
from app.domain.repositories.base import IUserRepository

# Importar los schemas para evitar forward references
from app.schemas.user import UserCreate, UserResponse


class UserService:
    """Servicio para gestionar la lógica de negocio relacionada con usuarios."""
    
    def __init__(self, user_repository: IUserRepository, hasher: Any = None) -> None:
        """
        Inicializa el servicio de usuarios.
        
        Args:
            user_repository: Repositorio de usuarios
            hasher: Servicio de hashing para contraseñas (opcional)
        """
        self.user_repository = user_repository
        self.hasher = hasher
    
    async def get_user(self, user_id: UUID) -> User:
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id: UUID del usuario a buscar
            
        Returns:
            User: El usuario encontrado
            
        Raises:
            EntityNotFoundError: Si no se encuentra ningún usuario con ese ID
        """
        user = await self.user_repository.get(user_id)
        if not user:
            raise EntityNotFoundError(entity="Usuario", entity_id=user_id)
        return user
    
    async def get_user_by_email(self, email: str) -> User | None:
        """
        Obtiene un usuario por su email.
        
        Args:
            email: Email del usuario a buscar
            
        Returns:
            User | None: El usuario encontrado o None si no existe
        """
        return await self.user_repository.get_by_email(email)
    
    async def get_users(self, email: str | None = None, is_active: bool | None = None) -> Sequence[User]:
        """
        Obtiene la lista de usuarios, con filtros opcionales por email e is_active.
        """
        users = await self.user_repository.list()
        if email is not None and is_active is not None:
            return [u for u in users if u.email == email and u.is_active == is_active]
        elif email is not None:
            return [u for u in users if u.email == email]
        elif is_active is not None:
            return [u for u in users if u.is_active == is_active]
        return users
    
    async def get_active_users(self) -> Sequence[User]:
        """
        Obtiene la lista de usuarios activos.
        Returns:
            Sequence[User]: Lista de usuarios activos
        """
        return await self.user_repository.get_active()

    async def create_user_with_hashed_password(
        self, user_in: UserCreate
    ) -> UserResponse:
        """
        Crea un usuario con la contraseña hasheada y valida unicidad de email.
        Args:
            user_in: UserCreate (schema)
        Returns:
            UserResponse (schema)
        Raises:
            ValidationError: Si el email ya existe
        """
        # Validar que no exista el email
        existing = await self.user_repository.get_by_email(user_in.email)
        if existing:
            raise ValidationError(f"Ya existe un usuario con el email {user_in.email}")
        hashed_password = self.hasher.hash_password(user_in.password)
        # Aquí deberías crear el modelo ORM para la base de datos
        from uuid import uuid4

        from app.domain.models.user import User
        user_domain = User(
            entity_id=uuid4(),
            email=user_in.email,
            full_name=user_in.full_name or "",
            is_active=True,
            is_superuser=False
        )
        await self.user_repository.create(user_domain)
        # Construir el schema de respuesta
        from app.schemas.user import UserResponse
        return UserResponse(
            id=user_domain.id,
            email=user_domain.email,
            full_name=user_domain.full_name
        )
    
    async def create_user(self, user: User) -> User:
        """
        Crea un nuevo usuario.
        
        Args:
            user: Usuario a crear
            
        Returns:
            User: El usuario creado
            
        Raises:
            ValidationError: Si ya existe un usuario con el mismo email
        """
        # Validar que el email no esté duplicado
        existing_user = await self.user_repository.get_by_email(user.email)
        if existing_user:
            raise ValidationError(
                f"Ya existe un usuario con el email {user.email}"
            )
        
        return await self.user_repository.create(user)
    
    async def update_user(self, user: User) -> User:
        """
        Actualiza un usuario existente.
        
        Args:
            user: Usuario con los datos actualizados
            
        Returns:
            User: El usuario actualizado
            
        Raises:
            EntityNotFoundException: Si no existe el usuario
        """
        # Verificar que el usuario existe
        existing_user = await self.user_repository.get(user.id)
        if not existing_user:
            raise EntityNotFoundError(entity="Usuario", entity_id=user.id)
        
        # Si se cambia el email, validar que no esté duplicado
        if existing_user.email != user.email:
            email_user = await self.user_repository.get_by_email(user.email)
            if email_user:
                raise ValidationError(
                    f"Ya existe un usuario con el email {user.email}"
                )
        
        return await self.user_repository.update(user)
    
    async def delete_user(self, user_id: UUID) -> None:
        """
        Elimina un usuario.
        
        Args:
            user_id: ID del usuario a eliminar
            
        Raises:
            EntityNotFoundException: Si no existe el usuario
        """
        user = await self.user_repository.get(user_id)
        if not user:
            raise EntityNotFoundError(entity="Usuario", entity_id=user_id)
        
        await self.user_repository.delete(user_id)
    
    async def deactivate_user(self, user_id: UUID) -> User:
        """
        Desactiva un usuario.
        
        Args:
            user_id: ID del usuario a desactivar
            
        Returns:
            User: El usuario desactivado
            
        Raises:
            EntityNotFoundException: Si no existe el usuario
        """
        user = await self.get_user(user_id)
        user.deactivate()
        return await self.user_repository.update(user)
    
    async def activate_user(self, user_id: UUID) -> User:
        """
        Activa un usuario.
        
        Args:
            user_id: ID del usuario a activar
            
        Returns:
            User: El usuario activado
            
        Raises:
            EntityNotFoundException: Si no existe el usuario
        """
        user = await self.get_user(user_id)
        user.activate()
        return await self.user_repository.update(user)
