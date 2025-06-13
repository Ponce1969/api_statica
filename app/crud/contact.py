from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Contact as ContactORM
from app.domain.repositories.base import IContactRepository


class ContactRepository(IContactRepository):
    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def create(self, contact: ContactORM):
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def get_by_email(self, email: str):
        result = await self.db.execute(
            select(ContactORM).where(ContactORM.email == email)
        )
        return result.scalars().all()

    async def list(self):
        result = await self.db.execute(select(ContactORM))
        return result.scalars().all()

