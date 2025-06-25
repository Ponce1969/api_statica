import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.crud.user import UserRepository
from app.domain.models.user import User
from app.core.security.hashing import get_password_hash

@pytest.fixture(scope="function")
async def create_test_user_for_auth(db_session_e2e: AsyncSession):
    email = "auth_user@example.com"
    password = "auth_password"
    hashed_password = get_password_hash(password)
    user_repository = UserRepository(db=db_session_e2e)
    user = await user_repository.create(entity=User(email=email, full_name="Auth Test User"), hashed_password=hashed_password)
    return {"email": email, "password": password, "user_id": str(user.id)}

@pytest.mark.asyncio
async def test_login_success(test_app: AsyncClient, create_test_user_for_auth: dict):
    login_data = {
        "username": create_test_user_for_auth["email"],
        "password": create_test_user_for_auth["password"]
    }
    response = await test_app.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_incorrect_password(test_app: AsyncClient, create_test_user_for_auth: dict):
    login_data = {
        "username": create_test_user_for_auth["email"],
        "password": "wrong_password"
    }
    response = await test_app.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Credenciales incorrectas"}

@pytest.mark.asyncio
async def test_login_user_not_found(test_app: AsyncClient):
    login_data = {
        "username": "nonexistent@example.com",
        "password": "any_password"
    }
    response = await test_app.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Credenciales incorrectas"}

@pytest.mark.asyncio
async def test_access_protected_route_no_token(test_app: AsyncClient):
    response = await test_app.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

@pytest.mark.asyncio
async def test_access_protected_route_invalid_token(test_app: AsyncClient):
    headers = {"Authorization": "Bearer invalid_token"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

@pytest.mark.asyncio
async def test_access_protected_route_expired_token(test_app: AsyncClient, create_test_user_for_auth: dict):
    # Manually create an expired token
    from app.core.security.jwt import create_access_token
    from datetime import timedelta

    expired_token = create_access_token(
        {"sub": create_test_user_for_auth["user_id"]},
        expires_delta=timedelta(seconds=-1)
    )
    # No es necesario un sleep en tests unitarios/integración para expiración de tokens
    # La validación de expiración se basa en el timestamp del token, no en el tiempo real de ejecución del test.

    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

@pytest.mark.asyncio
async def test_access_protected_route_valid_token(test_app: AsyncClient, create_test_user_for_auth: dict):
    login_data = {
        "username": create_test_user_for_auth["email"],
        "password": create_test_user_for_auth["password"]
    }
    login_response = await test_app.post("/api/v1/auth/login", data=login_data)
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == create_test_user_for_auth["email"]
