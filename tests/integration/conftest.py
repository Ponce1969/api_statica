"""
Configuración de pytest para tests de integración.
Incluye fixtures para la base de datos y sesiones.
"""
import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.base import Base
from tests.integration.test_config import test_settings

# Usar un archivo temporal para SQLite en lugar de memoria compartida
# Esto es más confiable en Windows que usar memoria compartida
import tempfile
import os

# Crear un archivo temporal para la base de datos SQLite
temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
temp_db.close()
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{temp_db.name}"

# Engine asíncrono para tests
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={"uri": True, "check_same_thread": False}
)

# Factory de sesiones asíncronas para tests
TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    """Fixture para el loop de eventos de asyncio."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def setup_database() -> AsyncGenerator[None, None]:
    """
    Fixture para configurar la base de datos de prueba.
    Crea todas las tablas antes de cada test.
    La base de datos en memoria se limpiará automáticamente después de cada test.
    """
    # Crear todas las tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield
    finally:
        # Limpiar la base de datos después de cada test
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        # Cerrar conexiones y eliminar archivo temporal
        await test_engine.dispose()
        try:
            os.unlink(temp_db.name)
        except:
            pass


@pytest_asyncio.fixture
async def db_session(setup_database: None) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture para obtener una sesión de base de datos para los tests.
    Crea una transacción que se hace rollback al final de cada test.
    """
    async with TestingSessionLocal() as session:
        # Iniciar una transacción para cada test
        transaction = await session.begin()
        
        try:
            yield session
        finally:
            # Hacer rollback de la transacción al final del test
            await transaction.rollback()
            await session.close()
