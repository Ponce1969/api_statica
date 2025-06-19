# tests/unit/services/test_user_service.py
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.exceptions.base import EntityNotFoundError, ValidationError
from app.domain.models.user import User as UserDomain
from app.domain.repositories.base import IUserRepository
from app.schemas.user import UserCreate
from app.services.user_service import UserService


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    """Fixture to create a mock user repository."""
    repo = AsyncMock(spec=IUserRepository)
    return repo


@pytest.fixture
def mock_hasher() -> MagicMock:
    """Fixture to create a mock password hasher."""
    hasher = MagicMock()
    hasher.hash_password.return_value = "hashed_password_value"
    hasher.verify_password.return_value = True # Default to successful verification
    return hasher


@pytest.fixture
def user_service(
    mock_user_repo: AsyncMock, mock_hasher: MagicMock
) -> UserService:
    """Fixture to create a UserService instance with a mock repository and hasher."""
    return UserService(user_repository=mock_user_repo, hasher=mock_hasher)


@pytest.fixture
def sample_user_domain() -> UserDomain:
    """Fixture for a sample User domain model."""
    return UserDomain(
        entity_id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )


@pytest.fixture
def sample_user_create_schema() -> UserCreate:
    """Fixture for a sample UserCreate schema."""
    return UserCreate(
        email="newuser@example.com",
        password="securepassword123",
        full_name="New User Full Name"
    )


@pytest.mark.asyncio
async def test_get_user_found(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test get_user returns a user when found."""
    user_id = sample_user_domain.id
    mock_user_repo.get.return_value = sample_user_domain

    found_user = await user_service.get_user(user_id)

    mock_user_repo.get.assert_called_once_with(user_id)
    assert found_user == sample_user_domain


@pytest.mark.asyncio
async def test_get_user_not_found(
    user_service: UserService, 
    mock_user_repo: AsyncMock
) -> None:
    """Test get_user raises EntityNotFoundError when user is not found."""
    non_existent_id = uuid4()
    mock_user_repo.get.return_value = None

    with pytest.raises(EntityNotFoundError) as excinfo:
        await user_service.get_user(non_existent_id)

    mock_user_repo.get.assert_called_once_with(non_existent_id)
    assert str(non_existent_id) in str(excinfo.value)
    assert "Usuario" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_user_by_email_found(
    user_service: UserService, mock_user_repo: AsyncMock, sample_user_domain: UserDomain
) -> None:
    """Test get_user_by_email returns a user when found."""
    email = sample_user_domain.email
    mock_user_repo.get_by_email.return_value = sample_user_domain

    found_user = await user_service.get_user_by_email(email)

    mock_user_repo.get_by_email.assert_called_once_with(email)
    assert found_user == sample_user_domain


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(
    user_service: UserService, 
    mock_user_repo: AsyncMock
) -> None:
    """Test get_user_by_email returns None when user is not found."""
    non_existent_email = "nonexistent@example.com"
    mock_user_repo.get_by_email.return_value = None

    found_user = await user_service.get_user_by_email(non_existent_email)

    mock_user_repo.get_by_email.assert_called_once_with(non_existent_email)
    assert found_user is None


@pytest.mark.asyncio
async def test_create_user_success(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test create_user successfully creates and returns a user."""
    mock_user_repo.get_by_email.return_value = None  # No existing user with this email
    mock_user_repo.create.return_value = sample_user_domain

    created_user = await user_service.create_user(sample_user_domain)

    mock_user_repo.get_by_email.assert_called_once_with(sample_user_domain.email)
    mock_user_repo.create.assert_called_once_with(sample_user_domain)
    assert created_user == sample_user_domain


@pytest.mark.asyncio
async def test_create_user_email_exists(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test create_user raises ValidationError if email already exists."""
    mock_user_repo.get_by_email.return_value = sample_user_domain  # Email exists

    with pytest.raises(ValidationError) as excinfo:
        await user_service.create_user(sample_user_domain)

    mock_user_repo.get_by_email.assert_called_once_with(sample_user_domain.email)
    mock_user_repo.create.assert_not_called()
    error_msg = f"Ya existe un usuario con el email {sample_user_domain.email}"
    assert error_msg in str(excinfo.value)

# TODO: Add tests for get_users, get_active_users, create_user_with_hashed_password,
# update_user, delete_user, deactivate_user, activate_user, assign_role_to_user,
# remove_role_from_user
