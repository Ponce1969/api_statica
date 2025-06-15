from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.crud.user import UserRepository as UserRepositoryImpl
from app.crud.role import RoleRepositoryImpl
from app.crud.contact import ContactRepository as ContactRepositoryImpl
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.services.contact_service import ContactService


# Obtener sesión de base de datos asíncrona
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Repositorios
async def get_user_repository(db: Optional[AsyncSession] = None) -> AsyncGenerator[UserRepositoryImpl, None]:
    if db:
        yield UserRepositoryImpl(db=db)
    else:
        async for session in get_db():
            yield UserRepositoryImpl(db=session)


async def get_role_repository(db: Optional[AsyncSession] = None) -> AsyncGenerator[RoleRepositoryImpl, None]:
    if db:
        yield RoleRepositoryImpl(db=db)
    else:
        async for session in get_db():
            yield RoleRepositoryImpl(db=session)


async def get_contact_repository(db: Optional[AsyncSession] = None) -> AsyncGenerator[ContactRepositoryImpl, None]:
    if db:
        yield ContactRepositoryImpl(db=db)
    else:
        async for session in get_db():
            yield ContactRepositoryImpl(db=session)


# Servicios

async def get_user_service(
    user_repo: Optional[UserRepositoryImpl] = None,
) -> AsyncGenerator[UserService, None]:
    if user_repo:
        yield UserService(user_repository=user_repo)
    else:
        async for repo in get_user_repository():
            yield UserService(user_repository=repo)


async def get_role_service(
    role_repo: Optional[RoleRepositoryImpl] = None,
) -> AsyncGenerator[RoleService, None]:
    if role_repo:
        yield RoleService(role_repository=role_repo)
    else:
        async for repo in get_role_repository():
            yield RoleService(role_repository=repo)


async def get_contact_service(
    contact_repo: Optional[ContactRepositoryImpl] = None,
) -> AsyncGenerator[ContactService, None]:
    if contact_repo:
        yield ContactService(contact_repository=contact_repo)
    else:
        async for repo in get_contact_repository():
            yield ContactService(contact_repository=repo)


async def get_auth_service(
    user_repo: Optional[UserRepositoryImpl] = None,
) -> AsyncGenerator[AuthService, None]:
    if user_repo:
        yield AuthService(user_repository=user_repo)
    else:
        async for repo in get_user_repository():
            yield AuthService(user_repository=repo)
