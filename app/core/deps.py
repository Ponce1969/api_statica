from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, AsyncGenerator, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import oauth2_scheme
from app.core.security.jwt import decode_access_token
from app.crud.contact import ContactRepository as ContactRepositoryImpl
from app.crud.contact_request import (
    InMemoryContactRequestRepository,
    SQLAlchemyContactRequestRepository,
)
from app.crud.role import RoleRepositoryImpl
from app.crud.user import UserRepository as UserRepositoryImpl
from app.database.session import AsyncSessionLocal
from app.domain.models.user import User
from app.domain.repositories.base import (
    IContactRepository,
    IRoleRepository,
    IUserRepository,
)
from app.domain.repositories.contact_request import IContactRequestRepository
from app.services.auth_service import AuthService
from app.services.contact_service import ContactService
from app.services.contact_request_service import ContactRequestService
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


# ----------------------- Seguridad y autenticación -----------------------

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_repo: Annotated[IUserRepository, Depends(get_user_repository)],
) -> User:
    """Devuelve el usuario autenticado a partir del JWT o lanza 401."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    user_id = payload.get("sub")
    user = await user_repo.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return user

# ------------------- ContactRequest dependencies -------------------
async def get_contact_request_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncGenerator[IContactRequestRepository, None]:
    # Para usar con base de datos real
    if True:  # Establecer en True para usar PostgreSQL
        yield SQLAlchemyContactRequestRepository(db=db)
    else:
        # Fallback a la versión en memoria para pruebas
        yield InMemoryContactRequestRepository()


async def get_contact_request_service(
    repo: Annotated[IContactRequestRepository, Depends(get_contact_request_repository)],  # noqa: B008
) -> AsyncGenerator[ContactRequestService, None]:
    from app.infrastructure.email.smtp_email import SMTPEmailSender

    email_sender = SMTPEmailSender()
    yield ContactRequestService(repository=repo, email_sender=email_sender)
