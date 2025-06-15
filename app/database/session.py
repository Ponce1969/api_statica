"""
Gestión centralizada de la sesión de base de datos para SQLAlchemy.
Incluye creación de engine asíncrono y dependencia para FastAPI.
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# URL de la base de datos (debería estar en settings)
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# Engine asíncrono
engine = create_async_engine(DATABASE_URL, echo=getattr(settings, "DEBUG", False), future=True)

# Factory de sesiones asíncronas
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

from collections.abc import AsyncGenerator

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia para obtener una sesión asíncrona en FastAPI.
    Cierra la sesión automáticamente al finalizar la request.
    """
    async with AsyncSessionLocal() as session:
        yield session
