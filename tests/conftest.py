"""
Configuración global de pytest para todas las pruebas.
Configura la base de datos SQLite en memoria antes de importar cualquier módulo.
"""
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator

# 1) Configura la URL de la base de datos de test desde una variable de entorno
import os
from app.core.config import settings

# Lee la TEST_DATABASE_URL de las variables de entorno.
# Si no está definida, usa un valor por defecto para el servicio test_db de Docker.
DEFAULT_TEST_DATABASE_URL = "postgresql+asyncpg://testuser:testpassword@localhost:5433/app_test"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)
settings.SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL

# 2) Ahora importa el resto
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app as fastapi_app
from app.database.base import Base
from app.core.deps import get_db

# 3) Crea el engine y sessionmaker global de test
_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,  # Puedes cambiarlo a True para debuggear SQL
    poolclass=NullPool
)
_TestSessionLocal = sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function")
async def db_session_global() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture global para obtener una sesión de base de datos para los tests.
    Crea las tablas al inicio y las elimina al final.
    """
    # Crear tablas
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Crear sesión
    session = _TestSessionLocal()
    try:
        yield session
    finally:
        await session.close()
        # Limpiar tablas
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client_global(db_session_global: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture global para el cliente de prueba HTTP con soporte para async.
    Override de la dependencia get_db para usar nuestra sesión SQLite en memoria.
    """
    # Guardar el override original
    original_override = fastapi_app.dependency_overrides.get(get_db)
    
    # Definir la función que devolverá nuestra sesión de prueba
    async def _get_test_db():
        try:
            yield db_session_global
        finally:
            pass  # La sesión se cierra en el fixture db_session_global
    
    # Aplicar el override
    fastapi_app.dependency_overrides[get_db] = _get_test_db
    
    # Crear el cliente con la aplicación
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app),
        base_url="http://test",
        follow_redirects=True,
        timeout=30.0
    ) as client:
        try:
            yield client
        finally:
            # Restaurar el override original
            if original_override is None:
                fastapi_app.dependency_overrides.pop(get_db, None)
            else:
                fastapi_app.dependency_overrides[get_db] = original_override
