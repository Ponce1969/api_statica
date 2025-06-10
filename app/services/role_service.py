"""
Servicio para la gestión de roles.

Contiene la lógica de negocio relacionada con roles, separada del acceso a datos
y de la presentación (API).
"""
from collections.abc import Sequence
from uuid import UUID

from app.domain.exceptions.base import EntityNotFoundError, ValidationError
from app.domain.models.role import Role
from app.domain.repositories.base import RoleRepository


class RoleService:
    """Servicio para gestionar la lógica de negocio relacionada con roles."""
    
    def __init__(self, role_repository: RoleRepository) -> None:
        self.role_repository = role_repository
    
    async def get_role(self, role_id: UUID) -> Role:
        """
        Obtiene un rol por su ID.
        
        Args:
            role_id: UUID del rol a buscar
            
        Returns:
            Role: El rol encontrado
            
        Raises:
            EntityNotFoundError: Si no se encuentra ningún rol con ese ID
        """
        role = await self.role_repository.get(role_id)
        if not role:
            raise EntityNotFoundError(entity="Rol", entity_id=role_id)
        return role
    
    async def get_role_by_name(self, name: str) -> Role | None:
        """
        Obtiene un rol por su nombre.
        
        Args:
            name: Nombre del rol a buscar
            
        Returns:
            Role | None: El rol encontrado o None si no existe
        """
        return await self.role_repository.get_by_name(name)
    
    async def get_roles(self) -> Sequence[Role]:
        """
        Obtiene la lista de todos los roles.
        
        Returns:
            Sequence[Role]: Lista de roles
        """
        return await self.role_repository.list()
    
    async def create_role(self, role: Role) -> Role:
        """
        Crea un nuevo rol.
        
        Args:
            role: Rol a crear
            
        Returns:
            Role: El rol creado
            
        Raises:
            ValidationError: Si ya existe un rol con el mismo nombre
        """
        # Validar que el nombre no esté duplicado
        existing_role = await self.role_repository.get_by_name(role.name)
        if existing_role:
            raise ValidationError(f"Ya existe un rol con el nombre {role.name}")
        
        return await self.role_repository.create(role)
    
    async def update_role(self, role: Role) -> Role:
        """
        Actualiza un rol existente.
        
        Args:
            role: Rol con los datos actualizados
            
        Returns:
            Role: El rol actualizado
            
        Raises:
            EntityNotFoundError: Si no existe el rol
            ValidationError: Si el nombre del rol ya existe
        """
        # Verificar que el rol existe
        existing_role = await self.role_repository.get(role.id)
        if not existing_role:
            raise EntityNotFoundError(entity="Rol", entity_id=role.id)
        
        # Si se cambia el nombre, validar que no esté duplicado
        if existing_role.name != role.name:
            name_role = await self.role_repository.get_by_name(role.name)
            if name_role:
                raise ValidationError(f"Ya existe un rol con el nombre {role.name}")
        
        return await self.role_repository.update(role)
    
    async def delete_role(self, role_id: UUID) -> None:
        """
        Elimina un rol.
        
        Args:
            role_id: ID del rol a eliminar
            
        Raises:
            EntityNotFoundError: Si no existe el rol
        """
        role = await self.role_repository.get(role_id)
        if not role:
            raise EntityNotFoundError(entity="Rol", entity_id=role_id)
        
        await self.role_repository.delete(role_id)
