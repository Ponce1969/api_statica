# tests/unit/services/test_user_service.py
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.exceptions.base import EntityNotFoundError, ValidationError
from app.domain.models.user import User as UserDomain
from app.domain.repositories.base import IUserRepository
from app.schemas.user import UserCreate
from app.services.user_service import UserService

# Configurar pytest-asyncio para los tests asíncronos
pytest_plugins = ["pytest_asyncio"]


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
        id=uuid4(),
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

@pytest.mark.asyncio
async def test_get_users(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test get_users returns all users when no filters are applied."""
    # Arrange
    users = [sample_user_domain, 
             UserDomain(
                 email="user2@example.com",
                 full_name="User Two",
                 is_active=False
             )]
    mock_user_repo.list.return_value = users
    
    # Act
    result = await user_service.get_users()
    
    # Assert
    assert result == users
    mock_user_repo.list.assert_called_once()


@pytest.mark.asyncio
async def test_get_users_with_email_filter(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test get_users filters by email when provided."""
    # Arrange
    users = [
        sample_user_domain,
        UserDomain(
            email="user2@example.com",
            full_name="User Two",
            is_active=True
        )
    ]
    mock_user_repo.list.return_value = users
    
    # Act
    result = await user_service.get_users(email="test@example.com")
    
    # Assert
    assert len(result) == 1
    assert result[0].email == "test@example.com"
    mock_user_repo.list.assert_called_once()


@pytest.mark.asyncio
async def test_get_users_with_active_filter(
    user_service: UserService, 
    mock_user_repo: AsyncMock
) -> None:
    """Test get_users filters by is_active when provided."""
    # Arrange
    users = [
        UserDomain(
            email="user1@example.com",
            full_name="User One",
            is_active=True
        ),
        UserDomain(
            email="user2@example.com",
            full_name="User Two",
            is_active=False
        )
    ]
    mock_user_repo.list.return_value = users
    
    # Act
    result = await user_service.get_users(is_active=True)
    
    # Assert
    assert len(result) == 1
    assert result[0].email == "user1@example.com"
    assert result[0].is_active is True
    mock_user_repo.list.assert_called_once()


@pytest.mark.asyncio
async def test_get_users_with_both_filters(
    user_service: UserService, 
    mock_user_repo: AsyncMock
) -> None:
    """Test get_users filters by both email and is_active when provided."""
    # Arrange
    users = [
        UserDomain(
            email="user1@example.com",
            full_name="User One",
            is_active=True
        ),
        UserDomain(
            email="user1@example.com",
            full_name="User One Inactive",
            is_active=False
        ),
        UserDomain(
            email="user2@example.com",
            full_name="User Two",
            is_active=True
        )
    ]
    mock_user_repo.list.return_value = users
    
    # Act
    result = await user_service.get_users(email="user1@example.com", is_active=True)
    
    # Assert
    assert len(result) == 1
    assert result[0].email == "user1@example.com"
    assert result[0].is_active is True
    assert result[0].full_name == "User One"
    mock_user_repo.list.assert_called_once()


@pytest.mark.asyncio
async def test_get_active_users(
    user_service: UserService, 
    mock_user_repo: AsyncMock
) -> None:
    """Test get_active_users returns only active users."""
    # Arrange
    active_users = [
        UserDomain(
            email="active1@example.com",
            full_name="Active User 1",
            is_active=True
        ),
        UserDomain(
            email="active2@example.com",
            full_name="Active User 2",
            is_active=True
        )
    ]
    mock_user_repo.get_active.return_value = active_users
    
    # Act
    result = await user_service.get_active_users()
    
    # Assert
    assert result == active_users
    assert len(result) == 2
    mock_user_repo.get_active.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_with_hashed_password(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    mock_hasher: MagicMock
) -> None:
    """Test create_user_with_hashed_password creates a user with hashed password."""
    # Arrange
    from app.schemas.user import UserCreate, UserResponse
    
    user_create = UserCreate(
        email="new@example.com",
        full_name="New User",
        password="password123"
    )
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = UserDomain(
        email=user_create.email,
        full_name=user_create.full_name,
        is_active=True,
        is_superuser=False
    )
    
    # Act
    result = await user_service.create_user_with_hashed_password(user_create)
    
    # Assert
    assert isinstance(result, UserResponse)
    assert result.email == user_create.email
    assert result.full_name == user_create.full_name
    mock_user_repo.get_by_email.assert_called_once_with(user_create.email)
    mock_user_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_with_hashed_password_email_exists(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test create_user_with_hashed_password raises error if email exists."""
    # Arrange
    from app.schemas.user import UserCreate
    
    user_create = UserCreate(
        email="test@example.com",  # Same as sample_user_domain
        full_name="New User",
        password="password123"
    )
    mock_user_repo.get_by_email.return_value = sample_user_domain
    
    # Act & Assert
    expected_msg = f"Ya existe un usuario con el email {user_create.email}"
    with pytest.raises(ValidationError, match=expected_msg):
        await user_service.create_user_with_hashed_password(user_create)
    
    mock_user_repo.get_by_email.assert_called_once_with(user_create.email)
    mock_user_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_update_user_success(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test update_user successfully updates a user."""
    # Arrange
    user_update_data = UserUpdate(
        email="updated@example.com",
        full_name="Updated Name",
        is_active=sample_user_domain.is_active,
        is_superuser=sample_user_domain.is_superuser
    )
    
    mock_user_repo.get.return_value = sample_user_domain
    mock_user_repo.get_by_email.return_value = None  # No user with the new email
    mock_user_repo.update.return_value = sample_user_domain # El mock debe devolver el user_domain original para que luego el servicio lo actualice
    
    # Act
    result = await user_service.update_user(sample_user_domain.id, user_update_data)
    
    # Assert
    assert result == updated_user
    mock_user_repo.get.assert_called_once_with(updated_user.id)
    mock_user_repo.get_by_email.assert_called_once_with(updated_user.email)
    mock_user_repo.update.assert_called_once_with(updated_user)


@pytest.mark.asyncio
async def test_update_user_not_found(
    user_service: UserService, 
    mock_user_repo: AsyncMock
) -> None:
    """Test update_user raises error if user not found."""
    # Arrange
    non_existent_user = UserDomain(
        email="nonexistent@example.com",
        full_name="Non Existent"
    )
    mock_user_repo.get.return_value = None
    
    # Act & Assert
    with pytest.raises(EntityNotFoundError):
        await user_service.update_user(non_existent_user)
    
    mock_user_repo.get.assert_called_once_with(non_existent_user.id)
    mock_user_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_user_email_exists(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test update_user raises error if new email already exists."""
    # Arrange
    another_user = UserDomain(
        email="another@example.com",
        full_name="Another User"
    )
    
    updated_user = UserDomain(
        id=sample_user_domain.id,
        email="another@example.com",  # Email that already exists
        full_name=sample_user_domain.full_name,
        is_active=sample_user_domain.is_active,
        is_superuser=sample_user_domain.is_superuser
    )
    
    mock_user_repo.get.return_value = sample_user_domain
    # Asignar otro usuario con el mismo email
    mock_user_repo.get_by_email.return_value = another_user
    
    # Act & Assert
    expected_msg_dupl = (
        f"Ya existe un usuario con el email {updated_user.email}"
    )
    with pytest.raises(ValidationError, match=expected_msg_dupl):
        await user_service.update_user(updated_user)
    
    mock_user_repo.get.assert_called_once_with(updated_user.id)
    mock_user_repo.get_by_email.assert_called_once_with(updated_user.email)
    mock_user_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_user_success(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test delete_user successfully deletes a user."""
    # Arrange
    mock_user_repo.get.return_value = sample_user_domain
    
    # Act
    await user_service.delete_user(sample_user_domain.id)
    
    # Assert
    mock_user_repo.get.assert_called_once_with(sample_user_domain.id)
    mock_user_repo.delete.assert_called_once_with(sample_user_domain.id)


@pytest.mark.asyncio
async def test_delete_user_not_found(
    user_service: UserService, 
    mock_user_repo: AsyncMock
) -> None:
    """Test delete_user raises error if user not found."""
    # Arrange
    from uuid import uuid4
    user_id = uuid4()
    mock_user_repo.get.return_value = None
    
    # Act & Assert
    with pytest.raises(EntityNotFoundError):
        await user_service.delete_user(user_id)
    
    mock_user_repo.get.assert_called_once_with(user_id)
    mock_user_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_deactivate_user_success(
    user_service: UserService, 
    mock_user_repo: AsyncMock, 
    sample_user_domain: UserDomain
) -> None:
    """Test deactivate_user successfully deactivates a user."""
    # Arrange
    mock_user_repo.get.return_value = sample_user_domain
    
    # Create a copy of the user that will be returned after deactivation
    deactivated_user = UserDomain(
        id=sample_user_domain.id,
        email=sample_user_domain.email,
        full_name=sample_user_domain.full_name,
        is_active=False,
        is_superuser=sample_user_domain.is_superuser
    )
    mock_user_repo.update.return_value = deactivated_user
    
    # Act
    result = await user_service.deactivate_user(sample_user_domain.id)
    
    # Assert
    assert result.is_active is False
    mock_user_repo.get.assert_called_once_with(sample_user_domain.id)
    mock_user_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_activate_user_success(
    user_service: UserService, 
    mock_user_repo: AsyncMock
) -> None:
    """Test activate_user successfully activates a user."""
    # Arrange
    inactive_user = UserDomain(
        email="inactive@example.com",
        full_name="Inactive User",
        is_active=False
    )
    mock_user_repo.get.return_value = inactive_user
    
    # Create a copy of the user that will be returned after activation
    activated_user = UserDomain(
        id=inactive_user.id,
        email=inactive_user.email,
        full_name=inactive_user.full_name,
        is_active=True,
        is_superuser=inactive_user.is_superuser
    )
    mock_user_repo.update.return_value = activated_user
    
    # Act
    result = await user_service.activate_user(inactive_user.id)
    
    # Assert
    assert result.is_active is True
    mock_user_repo.get.assert_called_once_with(inactive_user.id)
    mock_user_repo.update.assert_called_once()
