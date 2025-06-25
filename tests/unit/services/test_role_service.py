import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from app.domain.exceptions.base import EntityNotFoundError, ValidationError
from app.domain.models.role import Role
from app.domain.repositories.base import IRoleRepository
from app.schemas.role import RoleCreate, RoleResponse
from app.services.role_service import RoleService

@pytest.fixture
def mock_role_repository() -> AsyncMock:
    return AsyncMock(spec=IRoleRepository)

@pytest.fixture
def role_service(mock_role_repository: AsyncMock) -> RoleService:
    return RoleService(role_repository=mock_role_repository)

@pytest.mark.asyncio
async def test_get_role_success(role_service: RoleService, mock_role_repository: AsyncMock):
    role_id = uuid4()
    mock_role = Role(id=role_id, name="test_role", description="Test Description")
    mock_role_repository.get.return_value = mock_role

    result = await role_service.get_role(role_id)
    assert result == mock_role
    mock_role_repository.get.assert_called_once_with(role_id)

@pytest.mark.asyncio
async def test_get_role_not_found(role_service: RoleService, mock_role_repository: AsyncMock):
    role_id = uuid4()
    mock_role_repository.get.return_value = None

    with pytest.raises(EntityNotFoundError):
        await role_service.get_role(role_id)
    mock_role_repository.get.assert_called_once_with(role_id)

@pytest.mark.asyncio
async def test_get_role_by_name_success(role_service: RoleService, mock_role_repository: AsyncMock):
    role_name = "test_role"
    mock_role = Role(id=uuid4(), name=role_name, description="Test Description")
    mock_role_repository.get_by_name.return_value = mock_role

    result = await role_service.get_role_by_name(role_name)
    assert result == mock_role
    mock_role_repository.get_by_name.assert_called_once_with(role_name)

@pytest.mark.asyncio
async def test_get_role_by_name_not_found(role_service: RoleService, mock_role_repository: AsyncMock):
    role_name = "non_existent_role"
    mock_role_repository.get_by_name.return_value = None

    result = await role_service.get_role_by_name(role_name)
    assert result is None
    mock_role_repository.get_by_name.assert_called_once_with(role_name)

@pytest.mark.asyncio
async def test_list_roles_no_filter(role_service: RoleService, mock_role_repository: AsyncMock):
    mock_roles = [
        Role(id=uuid4(), name="role1", description="Desc1"),
        Role(id=uuid4(), name="role2", description="Desc2"),
    ]
    mock_role_repository.list.return_value = mock_roles

    results = await role_service.list_roles()
    assert len(results) == 2
    assert all(isinstance(r, RoleResponse) for r in results)
    assert results[0].name == "role1"
    mock_role_repository.list.assert_called_once()

@pytest.mark.asyncio
async def test_list_roles_with_name_filter(role_service: RoleService, mock_role_repository: AsyncMock):
    mock_roles = [
        Role(id=uuid4(), name="role1", description="Desc1"),
        Role(id=uuid4(), name="filtered_role", description="Filtered Desc"),
    ]
    mock_role_repository.list.return_value = mock_roles

    results = await role_service.list_roles(name="filtered_role")
    assert len(results) == 1
    assert results[0].name == "filtered_role"
    mock_role_repository.list.assert_called_once()

@pytest.mark.asyncio
async def test_create_role_success(role_service: RoleService, mock_role_repository: AsyncMock):
    role_create = RoleCreate(name="new_role", description="New Role Description")
    mock_role_repository.get_by_name.return_value = None # No existing role
    created_role_model = Role(id=uuid4(), name="new_role", description="New Role Description")
    mock_role_repository.create.return_value = created_role_model

    result = await role_service.create_role(role_create)
    assert isinstance(result, RoleResponse)
    assert result.name == "new_role"
    mock_role_repository.get_by_name.assert_called_once_with("new_role")
    mock_role_repository.create.assert_called_once()

@pytest.mark.asyncio
async def test_create_role_already_exists(role_service: RoleService, mock_role_repository: AsyncMock):
    role_create = RoleCreate(name="existing_role", description="Existing Role Description")
    mock_role_repository.get_by_name.return_value = Role(id=uuid4(), name="existing_role", description="Desc")

    with pytest.raises(ValidationError, match="Ya existe un rol con el nombre existing_role"):
        await role_service.create_role(role_create)
    mock_role_repository.get_by_name.assert_called_once_with("existing_role")
    mock_role_repository.create.assert_not_called()

@pytest.mark.asyncio
async def test_update_role_success(role_service: RoleService, mock_role_repository: AsyncMock):
    role_id = uuid4()
    existing_role = Role(id=role_id, name="old_name", description="Old Description")
    updated_role_data = Role(id=role_id, name="new_name", description="Updated Description")

    mock_role_repository.get.return_value = existing_role
    mock_role_repository.get_by_name.side_effect = [None] # No role with new name exists
    mock_role_repository.update.return_value = updated_role_data

    result = await role_service.update_role(updated_role_data)
    assert result == updated_role_data
    mock_role_repository.get.assert_called_once_with(role_id)
    mock_role_repository.get_by_name.assert_called_once_with("new_name")
    mock_role_repository.update.assert_called_once_with(updated_role_data)

@pytest.mark.asyncio
async def test_update_role_not_found(role_service: RoleService, mock_role_repository: AsyncMock):
    role_id = uuid4()
    role_to_update = Role(id=role_id, name="non_existent", description="Desc")
    mock_role_repository.get.return_value = None

    with pytest.raises(EntityNotFoundError):
        await role_service.update_role(role_to_update)
    mock_role_repository.get.assert_called_once_with(role_id)
    mock_role_repository.update.assert_not_called()

@pytest.mark.asyncio
async def test_update_role_name_already_exists(role_service: RoleService, mock_role_repository: AsyncMock):
    role_id = uuid4()
    existing_role = Role(id=role_id, name="original_name", description="Original Desc")
    updated_role_data = Role(id=role_id, name="duplicate_name", description="Updated Desc")
    
    mock_role_repository.get.return_value = existing_role
    mock_role_repository.get_by_name.return_value = Role(id=uuid4(), name="duplicate_name", description="Another Desc") # Another role with the new name exists

    with pytest.raises(ValidationError, match="Ya existe un rol con el nombre duplicate_name"):
        await role_service.update_role(updated_role_data)
    mock_role_repository.get.assert_called_once_with(role_id)
    mock_role_repository.get_by_name.assert_called_once_with("duplicate_name")
    mock_role_repository.update.assert_not_called()

@pytest.mark.asyncio
async def test_delete_role_success(role_service: RoleService, mock_role_repository: AsyncMock):
    role_id = uuid4()
    mock_role_repository.get.return_value = Role(id=role_id, name="to_delete", description="Desc")
    mock_role_repository.delete.return_value = None

    await role_service.delete_role(role_id)
    mock_role_repository.get.assert_called_once_with(role_id)
    mock_role_repository.delete.assert_called_once_with(role_id)

@pytest.mark.asyncio
async def test_delete_role_not_found(role_service: RoleService, mock_role_repository: AsyncMock):
    role_id = uuid4()
    mock_role_repository.get.return_value = None

    with pytest.raises(EntityNotFoundError):
        await role_service.delete_role(role_id)
    mock_role_repository.get.assert_called_once_with(role_id)
    mock_role_repository.delete.assert_not_called()
