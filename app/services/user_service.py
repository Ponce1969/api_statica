"""
Servicio para la gestión de usuarios.

Contiene la lógica de negocio relacionada con usuarios, separada del acceso a datos
y de la presentación (API).
"""
from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

from app.domain.exceptions.base import EntityNotFoundError, ValidationError
from app.domain.models.user import User
from app.domain.repositories.base import IUserRepository

# Importar los schemas para evitar forward references
from app.schemas.user import UserCreate, UserResponse, UserUpdate


from typing import runtime_checkable

@runtime_checkable
class PasswordHasher(Protocol):
    """Protocolo para definir un hasher de contraseñas."""
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool: ...
    def get_password_hash(self, password: str) -> str: ...


class UserService:
    """Servicio para gestionar la lógica de negocio relacionada con usuarios."""
    
    def __init__(
        self, 
        user_repository: IUserRepository, 
        hasher: PasswordHasher | None = None
    ) -> None:
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
            Optional[User]: El usuario encontrado o None si no existe
        """
        return await self.user_repository.get_by_email(email)
    
    async def get_users(
        self, 
        email: str | None = None, 
        is_active: bool | None = None
    ) -> Sequence[User]:
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
        # Hashear la contraseña y usarla al crear el usuario
        # self.hasher.hash_password(user_in.password)
        if not self.hasher:
            raise ValueError("PasswordHasher no está configurado en UserService.")
        hashed_password = self.hasher.get_password_hash(user_in.password)

        user_domain = User(
            email=user_in.email,
            full_name=user_in.full_name or "",
            is_active=True,
            is_superuser=False
        )
        created_user = await self.user_repository.create(user_domain, hashed_password=hashed_password)
        return UserResponse(
            id=created_user.id,
            email=created_user.email,
            full_name=created_user.full_name,
            is_active=created_user.is_active,
            is_superuser=created_user.is_superuser,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at
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
        
        # Aquí no se maneja el hashed_password, asumiendo que este método
        # se usa para crear usuarios sin contraseña (ej. por admin) o que
        # el hashing se hizo antes de llamar a este método.
        return await self.user_repository.create(user)
    
    async def update_user(self, user_id: UUID, user_in: UserUpdate) -> User:
        """
        Actualiza un usuario existente.
        
        Args:
            user_id: ID del usuario a actualizar
            user_in: Esquema con los datos a actualizar
            
        Returns:
            User: El usuario actualizado
            
        Raises:
            EntityNotFoundError: Si no existe el usuario
            ValidationError: Si el email ya existe en otro usuario
        """
        existing_user = await self.user_repository.get(user_id)
        if not existing_user:
            raise EntityNotFoundError(entity="Usuario", entity_id=user_id)

        # Si se proporciona un email y es diferente al actual, validar unicidad
        if user_in.email and user_in.email != existing_user.email:
            email_user = await self.user_repository.get_by_email(user_in.email)
            if email_user and email_user.id != user_id:
                raise ValidationError(
                    f"Ya existe un usuario con el email {user_in.email}"
                )

        # Actualizar los campos del usuario existente con los datos de user_in
        update_data = user_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_user, key, value)

        return await self.user_repository.update(existing_user)
    
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
