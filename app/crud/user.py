from app.database.models import User as UserORM
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.base import IUserRepository

class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def create(self, user: UserORM):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # Otros métodos como get_by_email, get, etc. pueden ir aquí
