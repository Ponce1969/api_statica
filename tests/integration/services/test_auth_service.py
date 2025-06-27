import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.base import ValidationError
from app.domain.models.user import User
from app.crud.user import UserRepository
from app.services.auth_service import AuthService
from app.core.security.hashing import get_password_hash # Import for setting up test data

@pytest.fixture
async def auth_service_integration(db_session: AsyncSession) -> AuthService:
    user_repository = UserRepository(db_session)
    return AuthService(user_repository=user_repository)

@pytest.mark.asyncio
async def test_integration_authenticate_user_success(db_session: AsyncSession, auth_service_integration: AuthService):
    email = "auth_test@example.com"
    password = "secure_password"
    hashed_password = get_password_hash(password)
    
    # Create user directly in DB for setup
    user_crud = UserRepository(db_session)
    await user_crud.create(User(email=email, full_name="Auth Test User"), hashed_password=hashed_password)

    # Authenticate using the service
    authenticated_user = await auth_service_integration.authenticate_user(email, password)
    assert authenticated_user.email == email
    assert authenticated_user.full_name == "Auth Test User"

@pytest.mark.asyncio
async def test_integration_authenticate_user_not_found(auth_service_integration: AuthService):
    with pytest.raises(ValidationError, match="Credenciales incorrectas"):
        await auth_service_integration.authenticate_user("nonexistent@example.com", "any_password")

@pytest.mark.asyncio
async def test_integration_authenticate_user_incorrect_password(db_session: AsyncSession, auth_service_integration: AuthService):
    email = "wrong_pwd_test@example.com"
    password = "correct_password"
    hashed_password = get_password_hash(password)

    user_crud = UserRepository(db_session)
    await user_crud.create(User(email=email, full_name="Wrong Pwd User"), hashed_password=hashed_password)

    with pytest.raises(ValidationError, match="Credenciales incorrectas"):
        await auth_service_integration.authenticate_user(email, "incorrect_password")

@pytest.mark.asyncio
async def test_integration_generate_token(db_session: AsyncSession, auth_service_integration: AuthService):
    email = "token_gen@example.com"
    password = "token_password"
    hashed_password = get_password_hash(password)

    user_crud = UserRepository(db_session)
    user = await user_crud.create(User(email=email, full_name="Token User"), hashed_password=hashed_password)

    token_data = auth_service_integration.generate_token(user)
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Optionally, decode and verify the token (though this is covered by unit tests for JWT)
    # from app.core.security.jwt import decode_access_token
    # decoded_payload = decode_access_token(token_data["access_token"])
    # assert decoded_payload["sub"] == str(user.id)
