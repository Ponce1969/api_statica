import os
import tempfile
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from contextlib import asynccontextmanager

import asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app as fastapi_app
from app.core.config import settings
from app.database.base import Base
from app.database.session import get_async_session

# Crear un archivo temporal para la base de datos SQLite de pruebas E2E
import tempfile
temp_db = tempfile.NamedTemporaryFile(suffix='_e2e.db', delete=False)
temp_db.close()
TEST_SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{temp_db.name}"

# Crear un motor para pruebas
@pytest.fixture(scope="session")
def event_loop():
    """Crea una instancia del bucle de eventos para la sesión de pruebas."""
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def engine():
    """Crea una instancia del motor de base de datos para pruebas."""
    # Usamos un archivo temporal por sesión, pero lo limpiamos por función
    return create_async_engine(
        TEST_SQLALCHEMY_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
        connect_args={"check_same_thread": False, "timeout": 30}
    )

# Crear tablas una vez al inicio de la sesión de pruebas
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database(engine):
    """Configura la base de datos antes de cada prueba."""
    # Limpiar y crear esquemas antes de cada prueba
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield  # Aquí se ejecuta la prueba
    
    # Limpiar después de la prueba
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # No eliminamos el archivo aquí, lo haremos al final de la sesión
    
    # Forzar la recolección de basura para liberar conexiones
    import gc
    gc.collect()

# Configurar la sesión de base de datos
@pytest_asyncio.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Crea una sesión de base de datos para cada prueba con transacciones aisladas."""
    # Crear una nueva conexión para esta sesión
    connection = await engine.connect()
    
    # Iniciar una transacción anidada (SAVEPOINT)
    transaction = await connection.begin_nested()
    
    # Configurar la sesión con la conexión
    session = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        class_=AsyncSession,
        future=True
    )()
    
    # Conectar eventos para manejar SAVEPOINT
    @event.listens_for(session.sync_session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if connection.closed:
            return
        if not connection.in_nested_transaction():
            connection.sync_connection.begin_nested()
    
    try:
        yield session
        # Hacer commit al final si no hubo errores
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        # Cerrar la sesión y la conexión
        await session.close()
        if connection.invalidated:
            await connection.close()
        else:
            if connection.in_transaction():
                await transaction.rollback()
            await connection.close()

# Anular la dependencia de la sesión de base de datos
@pytest_asyncio.fixture(scope="function")
async def override_get_db(db_session: AsyncSession):
    """Fixture para inyectar la sesión de base de datos en la aplicación."""
    async def _get_db():
        try:
            yield db_session
        finally:
            # No cerramos la sesión aquí, se maneja en el fixture db_session
            pass
    
    # Aplicar el override solo para esta prueba
    app = fastapi_app
    original_override = app.dependency_overrides.get(get_async_session)
    app.dependency_overrides[get_async_session] = _get_db
    
    try:
        yield
    finally:
        # Restaurar el override original
        if original_override is None:
            app.dependency_overrides.pop(get_async_session, None)
        else:
            app.dependency_overrides[get_async_session] = original_override

# Cliente de prueba HTTP
@pytest_asyncio.fixture(scope="function")
async def test_app(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Fixture para el cliente de prueba HTTP con soporte para async."""
    # Configurar el cliente para usar ASGITransport
    from httpx import ASGITransport
    
    # Crear una nueva aplicación FastAPI para este test
    test_app = fastapi_app
    
    # Crear el cliente con la aplicación
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
        follow_redirects=True,
        timeout=30.0
    ) as client:
        try:
            yield client
        finally:
            # Limpiar cualquier estado después de la prueba
            await client.aclose()

# Crear un usuario de prueba
@pytest_asyncio.fixture(scope="function")
async def create_test_user(db_session: AsyncSession):
    """Fixture para crear un usuario de prueba en la base de datos."""
    from app.crud.user import UserRepository
    from app.domain.models.user import User
    from app.core.security.hashing import get_password_hash
    import uuid
    
    # Crear un email único para cada test
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    user_repo = UserRepository(db=db_session)
    user = await user_repo.create(
        User(
            email=test_email,
            full_name="Test User",
            is_active=True
        ),
        hashed_password=get_password_hash("testpassword")
    )
    
    # Hacer commit para asegurar que el usuario se guarde
    await db_session.commit()
    
    return {
        "email": email,
        "password": password,
        "user_id": str(user.id)
    }

