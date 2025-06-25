import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.database.base import Base

# Override the get_db dependency for testing
@pytest_asyncio.fixture(scope="module")
async def override_get_db_dependency(db_session_e2e: AsyncSession):
    """
    Overrides the get_async_session dependency for E2E tests to use the test database session.
    """
    app.dependency_overrides[get_async_session] = lambda: db_session_e2e
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="module")
async def test_app(override_get_db_dependency):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost") as client:
        yield client

@pytest.fixture(scope="module")
async def db_session_e2e():
    # Usar una base de datos SQLite en memoria para los tests E2E
    async_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:", echo=False, poolclass=NullPool
    )
    TestingSessionLocal = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
