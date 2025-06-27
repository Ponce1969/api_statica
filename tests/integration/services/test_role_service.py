import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.base import EntityNotFoundError, ValidationError
from app.domain.models.role import Role
from app.schemas.role import RoleCreate, RoleResponse
from app.services.role_service import RoleService
from app.crud.role import RoleRepositoryImpl

@pytest.fixture
async def role_service_integration(db_session: AsyncSession) -> RoleService:
    # Use the actual CRUDRole for integration tests
    role_repository = RoleRepositoryImpl(db_session)
    return RoleService(role_repository=role_repository)

@pytest.mark.asyncio
async def test_integration_get_role(db_session: AsyncSession, role_service_integration: RoleService):
    # Create a role directly in DB for testing
    new_role = Role(id=uuid4(), name="IntegrationRole", description="Description for integration test")
    await RoleRepositoryImpl(db_session).create(entity=new_role)
    
    # Get the role using the service
    fetched_role = await role_service_integration.get_role(new_role.id)
    assert fetched_role.name == "IntegrationRole"
    assert fetched_role.description == "Description for integration test"

@pytest.mark.asyncio
async def test_integration_get_role_not_found(role_service_integration: RoleService):
    with pytest.raises(EntityNotFoundError):
        await role_service_integration.get_role(uuid4())

@pytest.mark.asyncio
async def test_integration_get_role_by_name(db_session: AsyncSession, role_service_integration: RoleService):
    new_role = Role(id=uuid4(), name="ByNameRole", description="Role to find by name")
    await RoleRepositoryImpl(db_session).create(entity=new_role)

    fetched_role = await role_service_integration.get_role_by_name("ByNameRole")
    assert fetched_role.name == "ByNameRole"

@pytest.mark.asyncio
async def test_integration_list_roles(db_session: AsyncSession, role_service_integration: RoleService):
    await RoleRepositoryImpl(db_session).create(Role(id=uuid4(), name="ListRole1", description="Desc1"))
    await RoleRepositoryImpl(db_session).create(Role(id=uuid4(), name="ListRole2", description="Desc2"))

    roles = await role_service_integration.list_roles()
    assert len(roles) >= 2 # May contain roles from other tests if not properly isolated
    assert any(r.name == "ListRole1" for r in roles)

@pytest.mark.asyncio
async def test_integration_create_role(db_session: AsyncSession, role_service_integration: RoleService):
    role_in = RoleCreate(name="NewServiceRole", description="Created via service")
    created_role = await role_service_integration.create_role(role_in)

    assert created_role.name == "NewServiceRole"
    assert created_role.description == "Created via service"
    # Verify it's in the DB
    retrieved_role = await RoleRepositoryImpl(db_session).get(created_role.id)
    assert retrieved_role.name == "NewServiceRole"

@pytest.mark.asyncio
async def test_integration_create_role_duplicate_name(db_session: AsyncSession, role_service_integration: RoleService):
    role_name = "DuplicateServiceRole"
    await RoleRepositoryImpl(db_session).create(Role(id=uuid4(), name=role_name, description="Original"))

    role_in = RoleCreate(name=role_name, description="Attempt to duplicate")
    with pytest.raises(ValidationError, match=f"Ya existe un rol con el nombre {role_name}"):
        await role_service_integration.create_role(role_in)

@pytest.mark.asyncio
async def test_integration_update_role(db_session: AsyncSession, role_service_integration: RoleService):
    original_role = Role(id=uuid4(), name="UpdateMe", description="Original Desc")
    await RoleRepositoryImpl(db_session).create(original_role)

    updated_role_data = Role(id=original_role.id, name="UpdatedServiceRole", description="Updated Desc")
    updated_role = await role_service_integration.update_role(updated_role_data)

    assert updated_role.name == "UpdatedServiceRole"
    assert updated_role.description == "Updated Desc"
    # Verify it's updated in the DB
    retrieved_role = await RoleRepositoryImpl(db_session).get(original_role.id)
    assert retrieved_role.name == "UpdatedServiceRole"

@pytest.mark.asyncio
async def test_integration_update_role_name_conflict(db_session: AsyncSession, role_service_integration: RoleService):
    role1 = Role(id=uuid4(), name="RoleToUpdate", description="Desc1")
    role2 = Role(id=uuid4(), name="ExistingRoleName", description="Desc2")
    await RoleRepositoryImpl(db_session).create(role1)
    await RoleRepositoryImpl(db_session).create(role2)

    role_update_data = Role(id=role1.id, name="ExistingRoleName", description="Should fail")
    with pytest.raises(ValidationError, match="Ya existe un rol con el nombre ExistingRoleName"):
        await role_service_integration.update_role(role_update_data)

@pytest.mark.asyncio
async def test_integration_delete_role(db_session: AsyncSession, role_service_integration: RoleService):
    role_to_delete = Role(id=uuid4(), name="DeleteMe", description="To be deleted")
    await RoleRepositoryImpl(db_session).create(role_to_delete)

    await role_service_integration.delete_role(role_to_delete.id)
    
    # Verify it's deleted from the DB
    retrieved_role = await RoleRepositoryImpl(db_session).get(role_to_delete.id)
    assert retrieved_role is None

@pytest.mark.asyncio
async def test_integration_delete_role_not_found(role_service_integration: RoleService):
    with pytest.raises(EntityNotFoundError):
        await role_service_integration.delete_role(uuid4())
