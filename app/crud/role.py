from app.domain.repositories.base import IRoleRepository
from app.database.models import Role as RoleORM
from sqlalchemy.ext.asyncio import AsyncSession

class RoleRepository(IRoleRepository):
    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def create(self, role: RoleORM):
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def get_by_name(self, name: str):
        result = await self.db.execute(
            select(RoleORM).where(RoleORM.name == name)
        )
        return result.scalar_one_or_none()

    async def list(self):
        result = await self.db.execute(select(RoleORM))
        return result.scalars().all()

