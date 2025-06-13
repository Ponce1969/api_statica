"""
Base para repositorios concretos de la capa de infraestructura (CRUD).
Aquí puedes definir lógica genérica o utilidades compartidas por todos los repositorios.
"""

from typing import Generic, TypeVar, Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar("T")  # Modelo SQLAlchemy

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id_: str) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == id_)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self, db: AsyncSession) -> list[T]:
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def add(self, db: AsyncSession, obj_in: T) -> T:
        db.add(obj_in)
        await db.commit()
        await db.refresh(obj_in)
        return obj_in

    async def delete(self, db: AsyncSession, obj: T) -> None:
        await db.delete(obj)
        await db.commit()

