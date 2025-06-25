"""
Interfaces base para los repositorios.

Los repositorios son abstracciones que ocultan los detalles de persistencia y
proporcionan una interfaz orientada al dominio para realizar operaciones de
acceso a datos.

Estas interfaces definen los métodos que deben implementar los repositorios
concretos, siguiendo el patrón Repository y el principio de inversión de
dependencias (DIP) de SOLID.
"""
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import date, datetime
from typing import Generic, TypeVar
from uuid import UUID

from app.domain.models.contact import Contact
from app.domain.models.role import Role
from app.domain.models.user import User

# T es un tipo genérico que representa cualquier entidad de dominio
T = TypeVar("T")


class IRepository(Generic[T], ABC):
    """
    Interfaz base para todos los repositorios.
    
    Renombrado a IRepository para indicar que es una interfaz.
    """

    @abstractmethod
    async def get(self, entity_id: UUID) -> T | None:
        """
        Obtiene una entidad por su ID.

        Args:
            entity_id: UUID de la entidad a buscar

        Returns:
            Optional[T]: La entidad encontrada o None si no existe

        Raises:
            ValueError: Si el UUID proporcionado no es válido 
                (manejo en implementación concreta)
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
    async def create(self, entity: T, hashed_password: str | None = None) -> T:
        """
        Crea una nueva entidad.

        Args:
            entity: Entidad a crear

        Returns:
            T: La entidad creada con su ID asignado

        Raises:
            ValueError: Si la entidad ya existe o tiene datos inválidos 
                (manejo en implementación concreta)
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
                (manejo en implementación concreta)
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
                (manejo en implementación concreta)
        """
        ...

    @abstractmethod
    async def get_by_field(
        self, 
        field_name: str, 
        value: str | float | bool | UUID | datetime | date | None
    ) -> T | None:
        """
        Obtiene una entidad por un campo específico.
        Ideal para campos únicos.

        Args:
            field_name: Nombre del campo por el que buscar
            value: Valor a buscar en el campo

        Returns:
            Optional[T]: La entidad encontrada o None si no existe

        Raises:
            ValueError: Si el nombre del campo no existe en la entidad 
                (manejo en implementación concreta)
        """
        ...

    @abstractmethod
    async def filter_by(
        self,
        **filters: str | float | bool | UUID | datetime | date | None
    ) -> Sequence[T]:
        """
        Filtra entidades según criterios específicos.

        Args:
            **filters: Criterios de filtrado como pares campo=valor

        Returns:
            Sequence[T]: Secuencia de entidades que cumplen los criterios

        Raises:
            ValueError: Si alguno de los campos de filtro no existe 
                (manejo en implementación concreta)
        """
        ...

    @abstractmethod
    async def exists(
        self, 
        **criteria: str | float | bool | UUID | datetime | date | None
    ) -> bool:
        """
        Verifica si existe una entidad que cumpla los criterios especificados.

        Args:
            **criteria: Criterios como pares campo=valor

        Returns:
            bool: True si existe al menos una entidad, False en caso contrario

        Raises:
            ValueError: Si alguno de los campos de criterio no existe 
                (manejo en implementación concreta)
        """
        ...

    @abstractmethod
    async def count(
        self, 
        **filters: str | float | bool | UUID | datetime | date | None
    ) -> int:
        """
        Cuenta el número de entidades que cumplen los criterios dados.

        Args:
            **filters: Criterios de filtrado como pares campo=valor

        Returns:
            int: Número de entidades que cumplen los criterios

        Raises:
            ValueError: Si alguno de los campos de filtro no existe 
                (manejo en implementación concreta)
        """
        ...


class IUserRepository(IRepository[User], ABC): # Renombrado y hereda de IRepository
    """
    Interfaz específica para el repositorio de usuarios.

    Extiende el repositorio genérico con métodos específicos para la entidad Usuario.
    """

    # Los métodos genéricos get y list ya están definidos en IRepository[User]
    # Si no cambian la firma ni el comportamiento esperado, 
    # no es necesario re-declararlos aquí.
    # Los dejo comentados para que veas que son redundantes si no añaden algo.

    # @abstractmethod
    # async def get(self, entity_id: UUID) -> Optional[User]:
    #     ...

    # @abstractmethod
    # async def list(self) -> Sequence[User]:
    #     ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """
        Obtiene un usuario por su dirección de email.

        Esta es una especialización para la búsqueda por email.

        Args:
            email: Dirección de email a buscar

        Returns:
            Optional[User]: El usuario encontrado o None si no existe ninguno 
                con ese email 

        Raises:
            ValueError: Si el email proporcionado no es válido 
                (manejo en implementación concreta)
        """
        ...

    @abstractmethod
    async def get_active(self) -> Sequence[User]:
        """
        Obtiene todos los usuarios activos.

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
                (manejo en implementación concreta)
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
                (manejo en implementación concreta)
        """
        ...


class IRoleRepository(IRepository[Role], ABC): # Renombrado y hereda de IRepository
    """
    Interfaz específica para el repositorio de roles.

    Extiende el repositorio genérico con métodos específicos para la entidad Rol.
    """

    # get y list son heredados y ya tipados para Role

    @abstractmethod
    async def get_by_name(self, name: str) -> Role | None: # Usar Optional
        """
        Obtiene un rol por su nombre.

        Esta es una especialización para la búsqueda por nombre de rol.

        Args:
            name: Nombre del rol a buscar

        Returns:
            Optional[Role]: El rol encontrado o None si no existe ninguno con ese nombre

        Raises:
            ValueError: Si el nombre proporcionado está vacío 
                (manejo en implementación concreta)
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


class IContactRepository(IRepository[Contact], ABC):
    """Interfaz específica para el repositorio de contactos.
    
    Renombrado y hereda de IRepository.
    """
    """
    Interfaz específica para el repositorio de contactos.

    Extiende el repositorio genérico con métodos específicos para la entidad Contacto.
    """

    # get y list son heredados y ya tipados para Contact

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
                (manejo en implementación concreta)
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
                (manejo en implementación concreta)
        """
        ...

    @abstractmethod
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
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
                (manejo en implementación concreta)
        """
        ...
