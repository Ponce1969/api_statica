"""
Interfaces base para los repositorios.

Los repositorios son abstracciones que ocultan los detalles de persistencia y 
proporcionan una interfaz orientada al dominio para realizar operaciones de
acceso a datos.
"""
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Generic, TypeVar
from uuid import UUID

from app.domain.models.base import Entity
from app.domain.models.contact import Contact
from app.domain.models.role import Role
from app.domain.models.user import User

# Tipado genérico para entidades
T = TypeVar('T', bound=Entity)


class Repository(Generic[T], ABC):
    """
    Interfaz base para todos los repositorios.
    
    Define un conjunto de operaciones comunes que todos los repositorios deben 
    implementar. Las implementaciones concretas pueden optar por implementar 
    directamente estos métodos o utilizar métodos auxiliares más específicos 
    según las necesidades.
    
    Args genéricos:
        T: Tipo de entidad con la que trabaja el repositorio, debe ser subclase 
           de Entity
    """
    
    @abstractmethod
    async def get(self, entity_id: UUID) -> T | None:
        """
        Obtiene una entidad por su ID.
        
        Args:
            entity_id: UUID de la entidad a buscar
            
        Returns:
            T | None: La entidad encontrada o None si no existe
            
        Raises:
            ValueError: Si el UUID proporcionado no es válido
        """
        ...
    
    @abstractmethod
    async def list(self) -> Sequence[T]:
        """
        Lista todas las entidades.
        
        Returns:
            Sequence[T]: Secuencia de todas las entidades
        """
        ...
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """
        Crea una nueva entidad.
        
        Args:
            entity: Entidad a crear
            
        Returns:
            T: La entidad creada con su ID asignado
            
        Raises:
            ValueError: Si la entidad ya existe o tiene datos inválidos
        """
        ...
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """
        Actualiza una entidad existente.
        
        Args:
            entity: Entidad con los datos actualizados
            
        Returns:
            T: La entidad actualizada
            
        Raises:
            ValueError: Si la entidad no existe o tiene datos inválidos
        """
        ...
    
    @abstractmethod
    async def delete(self, entity_id: UUID) -> None:
        """
        Elimina una entidad por su ID.
        
        Args:
            entity_id: ID de la entidad a eliminar
            
        Raises:
            ValueError: Si el UUID proporcionado no es válido o la entidad no existe
        """
        ...
    
    @abstractmethod
    async def get_by_field(self, field_name: str, value: object) -> T | None:
        """
        Obtiene una entidad por un campo específico.
        
        Args:
            field_name: Nombre del campo por el que buscar
            value: Valor a buscar en el campo
            
        Returns:
            T | None: La entidad encontrada o None si no existe
            
        Raises:
            ValueError: Si el nombre del campo no existe en la entidad
        """
        ...
    
    @abstractmethod
    async def filter_by(self, **filters: object) -> Sequence[T]:
        """
        Filtra entidades según criterios específicos.
        
        Args:
            **filters: Criterios de filtrado como pares campo=valor
            
        Returns:
            Sequence[T]: Secuencia de entidades que cumplen los criterios
            
        Raises:
            ValueError: Si alguno de los campos de filtro no existe
        """
        ...
    
    @abstractmethod
    async def exists(self, **criteria: object) -> bool:
        """
        Verifica si existe una entidad que cumpla los criterios especificados.
        
        Args:
            **criteria: Criterios como pares campo=valor
            
        Returns:
            bool: True si existe al menos una entidad, False en caso contrario
            
        Raises:
            ValueError: Si alguno de los campos de criterio no existe
        """
        ...
        
    @abstractmethod
    async def count(self, **filters: object) -> int:
        """
        Cuenta el número de entidades que cumplen los criterios dados.
        
        Args:
            **filters: Criterios de filtrado como pares campo=valor
            
        Returns:
            int: Número de entidades que cumplen los criterios
            
        Raises:
            ValueError: Si alguno de los campos de filtro no existe
        """
        ...


class UserRepository(Repository[User], ABC):
    """
    Interfaz específica para el repositorio de usuarios.
    
    Extiende el repositorio genérico con métodos específicos para la entidad Usuario.
    """
    
    @abstractmethod
    async def get(self, entity_id: UUID) -> User | None:
        """
        Obtiene un usuario por su ID.
        
        Args:
            entity_id: UUID del usuario a buscar
            
        Returns:
            User | None: El usuario encontrado o None si no existe
        """
        ...
    
    @abstractmethod
    async def list(self) -> Sequence[User]:
        """
        Lista todos los usuarios.
        
        Returns:
            Sequence[User]: Secuencia de todos los usuarios
        """
        ...
    
    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """
        Obtiene un usuario por su dirección de email.
        
        Esta es una implementación específica de get_by_field para el caso común
        de búsqueda por email, proporcionando una interfaz más clara y directa.
        
        Args:
            email: Dirección de email a buscar
            
        Returns:
            User | None: El usuario encontrado o None si no existe ninguno con ese email
            
        Raises:
            ValueError: Si el email proporcionado no es válido
        """
        ...
    
    @abstractmethod
    async def get_active(self) -> Sequence[User]:
        """
        Obtiene todos los usuarios activos.
        
        Esta es una implementación específica de filter_by para el caso común
        de filtrar usuarios por su estado activo.
        
        Returns:
            Sequence[User]: Secuencia de usuarios activos
        """
        ...
        
    @abstractmethod
    async def get_by_role(self, role_id: UUID) -> Sequence[User]:
        """
        Obtiene todos los usuarios que tienen asignado un rol específico.
        
        Args:
            role_id: ID del rol a buscar
            
        Returns:
            Sequence[User]: Secuencia de usuarios con el rol especificado
            
        Raises:
            ValueError: Si el UUID del rol no es válido
        """
        ...
        
    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> User:
        """
        Actualiza la fecha de último login de un usuario.
        
        Args:
            user_id: UUID del usuario
            
        Returns:
            User: El usuario con la fecha de último login actualizada
            
        Raises:
            ValueError: Si el UUID del usuario no es válido o el usuario no existe
        """
        ...


class RoleRepository(Repository[Role], ABC):
    """
    Interfaz específica para el repositorio de roles.
    
    Extiende el repositorio genérico con métodos específicos para la entidad Rol.
    """
    
    @abstractmethod
    async def get(self, entity_id: UUID) -> Role | None:
        """
        Obtiene un rol por su ID.
        
        Args:
            entity_id: UUID del rol a buscar
            
        Returns:
            Role | None: El rol encontrado o None si no existe
        """
        ...
    
    @abstractmethod
    async def list(self) -> Sequence[Role]:
        """
        Lista todos los roles.
        
        Returns:
            Sequence[Role]: Secuencia de todos los roles
        """
        ...
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None:
        """
        Obtiene un rol por su nombre.
        
        Esta es una implementación específica de get_by_field para el caso común
        de búsqueda por nombre de rol, proporcionando una interfaz más clara y directa.
        
        Args:
            name: Nombre del rol a buscar
            
        Returns:
            Role | None: El rol encontrado o None si no existe ninguno con ese nombre
            
        Raises:
            ValueError: Si el nombre proporcionado está vacío
        """
        ...
        
    @abstractmethod
    async def get_default_roles(self) -> Sequence[Role]:
        """
        Obtiene todos los roles que se asignan por defecto a nuevos usuarios.
        
        Returns:
            Sequence[Role]: Secuencia de roles predeterminados
        """
        ...
        
    @abstractmethod
    async def get_by_permissions(self, permissions: Sequence[str]) -> Sequence[Role]:
        """
        Obtiene roles que tienen ciertas permissions.
        
        Args:
            permissions: Lista de permissions requeridos
            
        Returns:
            Sequence[Role]: Roles que tienen todas las permissions especificadas
        """
        ...


class ContactRepository(Repository[Contact], ABC):
    """
    Interfaz específica para el repositorio de contactos.
    
    Extiende el repositorio genérico con métodos específicos para la entidad Contacto.
    """
    
    @abstractmethod
    async def get(self, entity_id: UUID) -> Contact | None:
        """
        Obtiene un contacto por su ID.
        
        Args:
            entity_id: UUID del contacto a buscar
            
        Returns:
            Contact | None: El contacto encontrado o None si no existe
        """
        ...
    
    @abstractmethod
    async def list(self) -> Sequence[Contact]:
        """
        Lista todos los contactos.
        
        Returns:
            Sequence[Contact]: Secuencia de todos los contactos
        """
        ...
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Sequence[Contact]:
        """
        Obtiene contactos por su dirección de email.
        
        A diferencia del repositorio de usuarios, aquí devolvemos una secuencia ya que
        múltiples contactos podrían tener el mismo email.
        
        Args:
            email: Dirección de email a buscar
            
        Returns:
            Sequence[Contact]: Secuencia de contactos con el email especificado
            
        Raises:
            ValueError: Si el email proporcionado no es válido
        """
        ...
        
    @abstractmethod
    async def get_unread(self) -> Sequence[Contact]:
        """
        Obtiene todos los contactos no leídos.
        
        Returns:
            Sequence[Contact]: Secuencia de contactos no leídos
        """
        ...
        
    @abstractmethod
    async def mark_as_read(self, contact_id: UUID) -> Contact:
        """
        Marca un contacto como leído.
        
        Args:
            contact_id: ID del contacto a marcar como leído
            
        Returns:
            Contact: El contacto actualizado
            
        Raises:
            ValueError: Si el UUID del contacto no es válido o el contacto no existe
        """
        ...
        
    @abstractmethod
    async def get_by_date_range(
        self, start_date: str, end_date: str
    ) -> Sequence[Contact]:
        """
        Obtiene contactos creados dentro de un rango de fechas.
        
        Args:
            start_date: Fecha de inicio en formato ISO (YYYY-MM-DD)
            end_date: Fecha de fin en formato ISO (YYYY-MM-DD)
            
        Returns:
            Sequence[Contact]: Contactos creados en el rango especificado
            
        Raises:
            ValueError: Si el formato de las fechas no es válido
        """
        ...
