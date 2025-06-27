# conftest.py
import asyncio
import pytest
import sys
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.base import Base

# Carga las variables de entorno desde .env.test
load_dotenv(Path(__file__).resolve().parent / ".env.test")

# Añade el directorio raíz del proyecto al sys.path
# Esto permite que Pytest encuentre el módulo 'app'
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configuración de la base de datos de prueba
TEST_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# Usar un motor de base de datos asíncrono para PostgreSQL
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# Crear una sesión de base de datos asíncrona para pruebas
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session")
async def db_engine():
    """Fixture para el motor de la base de datos de prueba."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(db_engine: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Fixture para una sesión de base de datos por función de prueba."""
    connection = await db_engine.connect()
    transaction = await connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        await transaction.rollback()
        await connection.close()

@pytest.fixture(scope="session")
def event_loop():
    """Fixture para el event loop de asyncio."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def app_client(db_session: AsyncSession):
    """Fixture para el cliente de la aplicación FastAPI con una base de datos de prueba."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database.session import get_db

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
