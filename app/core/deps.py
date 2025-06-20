from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends

from app.crud.contact import ContactRepository as ContactRepositoryImpl
from app.crud.role import RoleRepositoryImpl
from app.crud.user import UserRepository as UserRepositoryImpl
from app.database.session import AsyncSessionLocal
from app.domain.repositories.base import IContactRepository, IRoleRepository, IUserRepository
from app.services.auth_service import AuthService
from app.services.contact_service import ContactService
from app.services.role_service import RoleService
from app.services.user_service import UserService


# Obtener sesión de base de datos asíncrona
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Repositorios
async def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncGenerator[IUserRepository, None]:
    yield UserRepositoryImpl(db=db)


async def get_role_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncGenerator[IRoleRepository, None]:
    yield RoleRepositoryImpl(db=db)


async def get_contact_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncGenerator[IContactRepository, None]:
    yield ContactRepositoryImpl(db=db)


# Servicios

async def get_user_service(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
) -> AsyncGenerator[UserService, None]:
    yield UserService(user_repository=user_repo)


async def get_role_service(
    role_repo: Annotated[IRoleRepository, Depends(get_role_repository)],
) -> AsyncGenerator[RoleService, None]:
    yield RoleService(role_repository=role_repo)


async def get_contact_service(
    contact_repo: Annotated[IContactRepository, Depends(get_contact_repository)],
) -> AsyncGenerator[ContactService, None]:
    yield ContactService(contact_repository=contact_repo)


async def get_auth_service(
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
) -> AsyncGenerator[AuthService, None]:
    yield AuthService(user_repository=user_repo)
