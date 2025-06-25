import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from app.core.security.hashing import verify_password
from app.core.security.jwt import create_access_token
from app.domain.exceptions.base import ValidationError
from app.domain.models.user import User
from app.domain.repositories.base import IUserRepository
from app.services.auth_service import AuthService

@pytest.fixture
def mock_user_repository() -> AsyncMock:
    return AsyncMock(spec=IUserRepository)

@pytest.fixture
def auth_service(mock_user_repository: AsyncMock) -> AuthService:
    return AuthService(user_repository=mock_user_repository)

@pytest.mark.asyncio
@patch('app.services.auth_service.verify_password')
async def test_authenticate_user_success(mock_verify_password: AsyncMock, auth_service: AuthService, mock_user_repository: AsyncMock):
    email = "test@example.com"
    password = "test_password"
    mock_user = User(id=uuid4(), email=email, full_name="Test User")
    mock_user_repository.get_by_email.return_value = mock_user
    mock_verify_password.return_value = True

    user = await auth_service.authenticate_user(email, password)
    assert user == mock_user
    mock_user_repository.get_by_email.assert_called_once_with(email)
    mock_verify_password.assert_called_once_with(password, mock_user.hashed_password)

@pytest.mark.asyncio
@patch('app.services.auth_service.verify_password')
async def test_authenticate_user_not_found(mock_verify_password: AsyncMock, auth_service: AuthService, mock_user_repository: AsyncMock):
    email = "nonexistent@example.com"
    password = "any_password"
    mock_user_repository.get_by_email.return_value = None

    with pytest.raises(ValidationError, match="Credenciales incorrectas"):
        await auth_service.authenticate_user(email, password)
    mock_user_repository.get_by_email.assert_called_once_with(email)
    mock_verify_password.assert_not_called()

@pytest.mark.asyncio
@patch('app.services.auth_service.verify_password')
async def test_authenticate_user_incorrect_password(mock_verify_password: AsyncMock, auth_service: AuthService, mock_user_repository: AsyncMock):
    email = "test@example.com"
    password = "wrong_password"
    mock_user = User(id=uuid4(), email=email, full_name="Test User")
    mock_user_repository.get_by_email.return_value = mock_user
    mock_verify_password.return_value = False

    with pytest.raises(ValidationError, match="Credenciales incorrectas"):
        await auth_service.authenticate_user(email, password)
    mock_user_repository.get_by_email.assert_called_once_with(email)
    mock_verify_password.assert_called_once_with(password, mock_user.hashed_password)

@pytest.mark.asyncio
@patch('app.services.auth_service.verify_password')
async def test_authenticate_user_no_hashed_password(mock_verify_password: AsyncMock, auth_service: AuthService, mock_user_repository: AsyncMock):
    email = "test@example.com"
    password = "test_password"
    # User without hashed_password attribute
    mock_user = User(id=uuid4(), email=email, full_name=f"Test User {uuid4()}")
    mock_user_repository.get_by_email.return_value = mock_user
    mock_verify_password.return_value = False # This won't even be called due to the check

    with pytest.raises(ValidationError, match="Credenciales incorrectas"):
        await auth_service.authenticate_user(email, password)
    mock_user_repository.get_by_email.assert_called_once_with(email)
    mock_verify_password.assert_not_called()

@patch('app.services.auth_service.create_access_token')
def test_generate_token(mock_create_access_token: AsyncMock, auth_service: AuthService):
    user_id = uuid4()
    mock_user = User(id=user_id, email="test@example.com", full_name=f"Test User {uuid4()}")
    mock_create_access_token.return_value = "mock_access_token"

    token_data = auth_service.generate_token(mock_user)
    assert token_data == {"access_token": "mock_access_token", "token_type": "bearer"}
    mock_create_access_token.assert_called_once_with({"sub": str(user_id)})
