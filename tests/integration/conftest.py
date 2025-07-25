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


from alembic.config import Config
from alembic import command
import os

@pytest_asyncio.fixture(scope="function")
async def setup_database() -> AsyncGenerator[None, None]:
    """
    Fixture para configurar la base de datos de prueba.
    Usa Alembic para PostgreSQL y SQLAlchemy directo para SQLite.
    """
    # Determinar si estamos usando PostgreSQL o SQLite
    is_postgres = "postgresql" in test_settings.SQLALCHEMY_DATABASE_URI
    
    if is_postgres:
        # Configurar Alembic para PostgreSQL
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "../../alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", test_settings.SQLALCHEMY_DATABASE_URI)
        
        # Aplicar migraciones
        command.upgrade(alembic_cfg, "head")
    else:
        # Para SQLite, crear tablas directamente
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    try:
        yield
    finally:
        # Limpiar la base de datos después de cada test
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        # Si es SQLite, cerrar conexiones y eliminar archivo temporal
        if not is_postgres:
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
