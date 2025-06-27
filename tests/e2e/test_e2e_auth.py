import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
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
    user = await user_repository.create(
        User(email=email, full_name="Auth Test User"), 
        hashed_password=hashed_password
    )
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
    assert response.status_code == 401
    assert response.json() == {"detail": "Credenciales inválidas"}

@pytest.mark.asyncio
async def test_login_user_not_found(test_app: AsyncClient):
    login_data = {
        "username": "nonexistent@example.com",
        "password": "any_password"
    }
    response = await test_app.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Credenciales inválidas"}

@pytest.mark.asyncio
async def test_access_protected_route_no_token(test_app: AsyncClient):
    # No incluir el header de autorización
    response = await test_app.get("/api/v1/users/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "No autenticado"}
    
    # Probar con un token vacío
    response = await test_app.get(
        "/api/v1/users/me",
        headers={"Authorization": ""}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "No autenticado"}
    
    # Probar con un esquema de autenticación inválido
    response = await test_app.get(
        "/api/v1/users/me",
        headers={"Authorization": "InvalidScheme token"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "No autenticado"}

@pytest.mark.asyncio
async def test_access_protected_route_invalid_token(test_app: AsyncClient):
    # Token malformado
    headers = {"Authorization": "Bearer invalid_token.invalid_part.invalid_signature"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    
    # Token con formato inválido
    headers = {"Authorization": "Bearer not_a_valid_jwt_token"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    
    # Token con estructura incorrecta
    headers = {"Authorization": "Bearer abc.def.ghi"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}

@pytest.mark.asyncio
async def test_access_protected_route_expired_token(test_app: AsyncClient, create_test_user_for_auth: dict):
    # Crear manualmente un token expirado
    from app.core.security.jwt import create_access_token
    from datetime import timedelta

    expired_token = create_access_token(
        {"sub": create_test_user_for_auth["user_id"]},
        expires_delta=timedelta(seconds=-1)  # Token expirado
    )
    
    # No es necesario un sleep en tests unitarios/integración para expiración de tokens
    # La validación de expiración se basa en el timestamp del token, no en el tiempo real de ejecución del test.
    
    # Probar con el token expirado
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
    
    # Verificar que el mensaje de error sea consistente
    assert "token" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_access_protected_route_valid_token(test_app: AsyncClient, create_test_user_for_auth: dict):
    # Iniciar sesión para obtener un token válido
    login_data = {
        "username": create_test_user_for_auth["email"],
        "password": create_test_user_for_auth["password"]
    }
    login_response = await test_app.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]

    # Probar acceso a ruta protegida con token válido
    headers = {"Authorization": f"Bearer {token}"}
    response = await test_app.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == create_test_user_for_auth["email"]
    
    # Verificar que el token no es válido para otro usuario
    # (esto asume que tienes una forma de generar un token para un usuario diferente)
    # headers["Authorization"] = f"Bearer {other_user_token}"
    # response = await test_app.get("/api/v1/users/me", headers=headers)
    # assert response.status_code == 403  # O 401 dependiendo de tu lógica de autorización
