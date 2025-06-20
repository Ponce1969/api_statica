"""
Configuración de pytest para tests de integración.
Incluye fixtures para la base de datos y sesiones.
"""
import asyncio
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.base import Base
from tests.integration.test_config import test_settings

# Usar la URL de la base de datos de la configuración de test
TEST_DATABASE_URL = test_settings.SQLALCHEMY_DATABASE_URI

# Engine asíncrono para tests
test_engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, poolclass=NullPool
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


@pytest.fixture(scope="session")
async def setup_database() -> AsyncGenerator[None, None]:
    """
    Fixture para configurar la base de datos de prueba.
    Crea todas las tablas antes de los tests y las elimina después.
    """
    # Crear todas las tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Eliminar todas las tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database: None) -> AsyncGenerator[AsyncSession, None]:

    """
    Fixture para obtener una sesión de base de datos para los tests.
    Crea una transacción que se hace rollback al final de cada test.
    """
    async with TestingSessionLocal() as session:
        # Iniciar una transacción para cada test
        transaction = await session.begin()
        
        yield session
        
        # Hacer rollback de la transacción al final del test
        await transaction.rollback()
        await session.close()
