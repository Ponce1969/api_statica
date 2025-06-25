"""
Tests de integración para UserService.
Estos tests prueban la interacción entre el servicio y la base de datos real.
"""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security.hashing import get_password_hash, verify_password
from app.services.user_service import PasswordHasher
from app.crud.user import UserRepository
from app.domain.exceptions.base import EntityNotFoundError, ValidationError
from app.domain.models.user import User as UserDomain
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


@pytest.fixture
async def user_repository(db_session: AsyncSession) -> UserRepository:
    """Fixture para crear un repositorio de usuarios real."""
    return UserRepository(db=db_session)


class TestPasswordHasher(PasswordHasher):
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return get_password_hash(password)

@pytest.fixture
def password_hasher() -> TestPasswordHasher:
    """Fixture para proporcionar una instancia de PasswordHasher para pruebas."""
    return TestPasswordHasher()


@pytest.fixture
async def user_service(
    user_repository: UserRepository, password_hasher
) -> UserService:
    """Fixture para crear un UserService con un repositorio y hasher reales."""
    return UserService(user_repository=user_repository, hasher=password_hasher)


@pytest.fixture
async def sample_user(user_repository: UserRepository) -> UserDomain:
    """Fixture para crear un usuario de prueba en la base de datos."""
    test_password = "securepassword"
    hashed_test_password = get_password_hash(test_password)
    user = UserDomain(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_superuser=False
    )
    return await user_repository.create(user, hashed_password=hashed_test_password)


@pytest.fixture
async def inactive_user(user_repository: UserRepository) -> UserDomain:
    """Fixture para crear un usuario inactivo de prueba en la base de datos."""
    test_password = "securepassword"
    hashed_test_password = get_password_hash(test_password)
    user = UserDomain(
        id=uuid.uuid4(),
        email="inactive@example.com",
        full_name="Inactive User",
        is_active=False,
        is_superuser=False
    )
    return await user_repository.create(user, hashed_password=hashed_test_password)


@pytest.mark.asyncio
async def test_get_user_integration(
    user_service: UserService, sample_user: UserDomain
) -> None:
    """Test de integración para get_user."""
    # Arrange - ya configurado con el fixture sample_user
    
    # Act
    found_user = await user_service.get_user(sample_user.id)
    
    # Assert
    assert found_user is not None
    assert found_user.id == sample_user.id
    assert found_user.email == sample_user.email
    assert found_user.full_name == sample_user.full_name
    assert found_user.is_active == sample_user.is_active


@pytest.mark.asyncio
async def test_get_user_not_found_integration(user_service: UserService) -> None:
    """Test de integración para get_user cuando el usuario no existe."""
    # Arrange
    non_existent_id = uuid.uuid4()
    
    # Act & Assert
    with pytest.raises(EntityNotFoundError) as excinfo:
        await user_service.get_user(non_existent_id)
    
    assert str(non_existent_id) in str(excinfo.value)
    assert "Usuario" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_user_by_email_integration(
    user_service: UserService, sample_user: UserDomain
) -> None:
    """Test de integración para get_user_by_email."""
    # Act
    found_user = await user_service.get_user_by_email(sample_user.email)
    
    # Assert
    assert found_user is not None
    assert found_user.id == sample_user.id
    assert found_user.email == sample_user.email


@pytest.mark.asyncio
async def test_get_user_by_email_not_found_integration(
    user_service: UserService,
) -> None:
    """Test de integración para get_user_by_email cuando el usuario no existe."""
    # Act
    found_user = await user_service.get_user_by_email("nonexistent@example.com")
    
    # Assert
    assert found_user is None


@pytest.mark.asyncio
async def test_create_user_with_hashed_password_integration(
    user_service: UserService, user_repository: UserRepository
) -> None:
    """Test de integración para create_user_with_hashed_password."""
    # Arrange
    user_create = UserCreate(
        email="newuser@example.com",
        password="securepassword123",
        full_name="New User"
    )
    
    # Act
    created_user = await user_service.create_user_with_hashed_password(user_create)
    
    # Assert
    assert created_user is not None
    assert created_user.email == user_create.email
    assert created_user.full_name == user_create.full_name
    assert created_user.is_active is True
    
    # Verificar que el usuario se guardó en la base de datos
    db_user = await user_repository.get_by_email(user_create.email)
    assert db_user is not None
    assert db_user.id == created_user.id


@pytest.mark.asyncio
async def test_create_user_with_hashed_password_email_exists_integration(
    user_service: UserService, sample_user: UserDomain
) -> None:
    """Test de integración para create_user_with_hashed_password.
    Caso: el email ya existe."""
    # Arrange
    user_create = UserCreate(
        email=sample_user.email,  # Email que ya existe
        password="securepassword123",
        full_name="Duplicate Email User"
    )
    
    # Act & Assert
    with pytest.raises(ValidationError) as excinfo:
        await user_service.create_user_with_hashed_password(user_create)
    
    expected_msg = (
        f"Ya existe un usuario con el email {sample_user.email}"
    )
    assert expected_msg in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_users_integration(
    user_service: UserService, sample_user: UserDomain, inactive_user: UserDomain
) -> None:
    """Test de integración para get_users."""
    # Act
    users = await user_service.get_users()
    
    # Assert
    assert len(users) >= 2  # Al menos los dos usuarios que creamos
    user_ids = [user.id for user in users]
    assert sample_user.id in user_ids
    assert inactive_user.id in user_ids


@pytest.mark.asyncio
async def test_get_users_with_email_filter_integration(
    user_service: UserService, sample_user: UserDomain
) -> None:
    """Test de integración para get_users con filtro de email."""
    # Act
    users = await user_service.get_users(email=sample_user.email)
    
    # Assert
    assert len(users) == 1
    assert users[0].id == sample_user.id
    assert users[0].email == sample_user.email


@pytest.mark.asyncio
async def test_get_users_with_active_filter_integration(
    user_service: UserService, sample_user: UserDomain, inactive_user: UserDomain
) -> None:
    """Test de integración para get_users con filtro de is_active."""
    # Act
    active_users = await user_service.get_users(is_active=True)
    inactive_users = await user_service.get_users(is_active=False)
    
    # Assert
    assert all(user.is_active for user in active_users)
    assert sample_user.id in [user.id for user in active_users]
    
    assert all(not user.is_active for user in inactive_users)
    assert inactive_user.id in [user.id for user in inactive_users]


@pytest.mark.asyncio
async def test_get_active_users_integration(
    user_service: UserService, sample_user: UserDomain, inactive_user: UserDomain
) -> None:
    """Test de integración para get_active_users."""
    # Act
    active_users = await user_service.get_active_users()
    
    # Assert
    assert all(user.is_active for user in active_users)
    assert sample_user.id in [user.id for user in active_users]
    assert inactive_user.id not in [user.id for user in active_users]


@pytest.mark.asyncio
async def test_update_user_integration(
    user_service: UserService, sample_user: UserDomain, user_repository: UserRepository
) -> None:
    """Test de integración para update_user."""
    # Arrange
    updated_data = UserUpdate(
        full_name="Updated Name",
        email="updated@example.com"
    )
    
    # Act
    updated_user = await user_service.update_user(sample_user.id, updated_data)
    
    # Assert
    assert updated_user.id == sample_user.id
    assert updated_user.full_name == updated_data.full_name
    assert updated_user.email == updated_data.email
    
    # Verificar que los cambios se guardaron en la base de datos
    db_user = await user_repository.get(sample_user.id)
    assert db_user is not None
    assert db_user.full_name == updated_data.full_name
    assert db_user.email == updated_data.email


@pytest.mark.asyncio
async def test_update_user_not_found_integration(user_service: UserService) -> None:
    """Test de integración para update_user cuando el usuario no existe."""
    # Arrange
    non_existent_id = uuid.uuid4()
    updated_data = UserUpdate(full_name="Updated Name")
    
    # Act & Assert
    with pytest.raises(EntityNotFoundError) as excinfo:
        await user_service.update_user(non_existent_id, updated_data)
    
    assert str(non_existent_id) in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_user_email_exists_integration(
    user_service: UserService, sample_user: UserDomain, inactive_user: UserDomain
) -> None:
    """Test de integración para update_user cuando el email ya existe."""
    # Arrange
    updated_data = UserUpdate(email=inactive_user.email)  # Email que ya existe
    
    # Act & Assert
    with pytest.raises(ValidationError) as excinfo:
        await user_service.update_user(sample_user.id, updated_data)
    
    expected_msg = (
        f"Ya existe un usuario con el email {inactive_user.email}"
    )
    assert expected_msg in str(excinfo.value)


@pytest.mark.asyncio
async def test_delete_user_integration(
    user_service: UserService, user_repository: UserRepository
) -> None:
    """Test de integración para delete_user."""
    # Arrange
    # Crear un usuario específico para este test
    test_password = "securepassword"
    hashed_test_password = get_password_hash(test_password)
    user = UserDomain(
        id=uuid.uuid4(),
        email="to_delete@example.com",
        full_name="To Delete User",
        is_active=True,
        is_superuser=False
    )
    created_user = await user_repository.create(user, hashed_password=hashed_test_password)
    
    # Act
    await user_service.delete_user(created_user.id)
    
    # Assert
    with pytest.raises(EntityNotFoundError):
        await user_repository.get(created_user.id)


@pytest.mark.asyncio
async def test_delete_user_not_found_integration(user_service: UserService) -> None:
    """Test de integración para delete_user cuando el usuario no existe."""
    # Arrange
    non_existent_id = uuid.uuid4()
    
    # Act & Assert
    with pytest.raises(EntityNotFoundError) as excinfo:
        await user_service.delete_user(non_existent_id)
    
    assert str(non_existent_id) in str(excinfo.value)


@pytest.mark.asyncio
async def test_deactivate_user_integration(
    user_service: UserService, sample_user: UserDomain, user_repository: UserRepository
) -> None:
    """Test de integración para deactivate_user."""
    # Act
    deactivated_user = await user_service.deactivate_user(sample_user.id)
    
    # Assert
    assert deactivated_user.id == sample_user.id
    assert deactivated_user.is_active is False
    
    # Verificar que los cambios se guardaron en la base de datos
    db_user = await user_repository.get(sample_user.id)
    assert db_user is not None
    assert db_user.is_active is False


@pytest.mark.asyncio
async def test_activate_user_integration(
    user_service: UserService,
    inactive_user: UserDomain,
    user_repository: UserRepository
) -> None:
    """Test de integración para activate_user."""
    # Act
    activated_user = await user_service.activate_user(inactive_user.id)
    
    # Assert
    assert activated_user.id == inactive_user.id
    assert activated_user.is_active is True
    
    # Verificar que los cambios se guardaron en la base de datos
    db_user = await user_repository.get(inactive_user.id)
    assert db_user is not None
    assert db_user.is_active is True
