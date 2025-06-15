"""
Base para repositorios concretos de la capa de infraestructura (CRUD).
Aquí puedes definir lógica genérica o utilidades compartidas por todos los repositorios.
"""

from typing import Generic, TypeVar, Type, Optional, Any, Dict, Sequence, List
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Table
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=DeclarativeBase)  # Modelo SQLAlchemy con restricción a DeclarativeBase

class BaseRepository(Generic[T]):
    """
    Repositorio base genérico para operaciones CRUD sobre modelos SQLAlchemy.

    - Utiliza UUID como tipo de clave primaria por defecto (id: uuid.UUID).
    - Proporciona métodos genéricos para obtener, listar, agregar, eliminar y filtrar entidades.
    - Pensado para ser heredado por repositorios concretos de cada entidad.
    """
    def __init__(self, model: Type[T], db: AsyncSession):
        """
        Inicializa el repositorio base.
        
        Args:
            model: Clase del modelo SQLAlchemy (debe tener id: uuid.UUID).
            db: Sesión asíncrona de SQLAlchemy.
        """
        self.model = model
        self.db = db

    async def get_by_id(self, id_: uuid.UUID) -> Optional[T]:
        """
        Recupera una entidad por su UUID primario.
        Args:
            id_: UUID de la entidad a buscar.
        Returns:
            Instancia del modelo o None si no se encuentra.
        """
        stmt = select(self.model).where(getattr(self.model, 'id') == id_)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> List[T]:
        """
        Lista todas las entidades del modelo.
        Returns:
            Lista de instancias del modelo.
        """
        result = await self.db.execute(select(self.model))
        return list(result.scalars().all())

    async def add(self, obj_in: T) -> T:
        """
        Agrega una nueva entidad a la base de datos.
        Args:
            obj_in: Instancia del modelo a agregar.
        Returns:
            Instancia agregada (con ID y campos autogenerados).
        """
        self.db.add(obj_in)
        await self.db.commit()
        await self.db.refresh(obj_in)
        return obj_in

    async def delete(self, entity_id: uuid.UUID) -> None:
        """
        Elimina una entidad de la base de datos por su ID.
        Args:
            entity_id: UUID de la entidad a eliminar.
        """
        obj = await self.get_by_id(entity_id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()

    async def list_filtered(self, skip: int = 0, limit: int = 100, **filters: Any) -> List[T]:
        """
        Lista entidades filtradas por los campos dados y soporta paginación.
        Solo se permiten filtros por columnas reales del modelo (no propiedades ni métodos).
        Args:
            skip: Número de entidades a omitir (para paginación).
            limit: Número máximo de entidades a devolver.
            **filters: Filtros por campo del modelo (ej: email="a@b.com").
        Returns:
            Lista de instancias del modelo que cumplen los filtros.
        Raises:
            ValueError: Si se intenta filtrar por un campo que no es columna real del modelo.
        """
        stmt = select(self.model)
        # Acceder a __table__ de forma segura
        table = getattr(self.model, '__table__', None)
        if table is None:
            raise ValueError(f"El modelo {self.model.__name__} no tiene atributo __table__")
        table_obj: Table = table
            
        column_names = table.columns.keys()
        for attr, value in filters.items():
            if value is not None:
                if attr not in column_names:
                    raise ValueError(f"El campo '{attr}' no es una columna válida de {self.model.__name__}.")                
                stmt = stmt.where(getattr(self.model, attr) == value)
        stmt = stmt.offset(skip).limit(limit)

        if logger.isEnabledFor(logging.DEBUG):
            filtered = {k: v for k, v in filters.items() if k != "password"}
            logger.debug(f"[{self.model.__name__}] Filtros aplicados: {filtered}, skip={skip}, limit={limit}")

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
