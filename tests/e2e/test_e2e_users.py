import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from app.database.base import Base # Importar Base

# Override the get_db dependency for testing


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


@pytest.fixture(scope="module")
async def test_app(db_session_e2e: AsyncSession):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="module")
async def create_test_user(test_app: AsyncClient, db_session_e2e: AsyncSession):
    user_data = {
        "email": "test_e2e@example.com",
        "password": "password123",
        "full_name": "Test User E2E"
    }
    response = await test_app.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    return response.json()

@pytest.mark.asyncio
async def test_create_user_e2e(test_app: AsyncClient, db_session_e2e: AsyncSession):
    user_data = {
        "email": "new_e2e@example.com",
        "password": "newpassword123",
        "full_name": "New User E2E"
    }
    response = await test_app.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "created_at" in data

@pytest.mark.asyncio
async def test_login_for_access_token_e2e(test_app: AsyncClient, create_test_user: dict):
    login_data = {
        "username": create_test_user["email"],
        "password": "password123"
    }
    response = await test_app.post("/api/v1/users/login/access-token", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user_e2e(test_app: AsyncClient, create_test_user: dict):
    login_data = {
        "username": create_test_user["email"],
        "password": "password123"
    }
    login_response = await test_app.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == create_test_user["email"]

@pytest.mark.asyncio
async def test_update_user_e2e(test_app: AsyncClient, create_test_user: dict):
    login_data = {
        "username": create_test_user["email"],
        "password": "password123"
    }
    login_response = await test_app.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"full_name": "Updated Name E2E", "is_active": False}
    response = await test_app.put(f"/api/v1/users/{create_test_user['id']}", headers=headers, json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["full_name"] == "Updated Name E2E"
    assert updated_user["is_active"] is False

@pytest.mark.asyncio
async def test_delete_user_e2e(test_app: AsyncClient, db_session_e2e: AsyncSession):
    # Create a user specifically for deletion test
    user_data = {
        "email": "delete_e2e@example.com",
        "password": "password123",
        "full_name": "Delete User E2E"
    }
    create_response = await test_app.post("/api/v1/users/", json=user_data)
    assert create_response.status_code == 201
    user_to_delete = create_response.json()

    login_data = {
        "username": user_to_delete["email"],
        "password": "password123"
    }
    login_response = await test_app.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.delete(f"/api/v1/users/{user_to_delete['id']}", headers=headers)
    assert response.status_code == 200
    deleted_user = response.json()
    assert deleted_user["id"] == user_to_delete["id"]

    # Verify user is actually deleted from DB
    from app.crud.user import UserRepository
    from app.domain.models.user import User
    user_crud = UserRepository(db=db_session_e2e)
    assert await user_crud.get(user_to_delete["id"]) is None
