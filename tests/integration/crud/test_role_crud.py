import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.role import RoleRepositoryImpl
from app.schemas.role import RoleCreate, RoleUpdate
from app.domain.models.role import Role
from uuid import UUID

@pytest.mark.asyncio
async def test_create_role(db_session: AsyncSession):
    role_crud = RoleRepositoryImpl(db_session)
    role_domain = Role(name="admin", description="Administrator role")
    role = await role_crud.create(role_domain)
    assert role.name == "admin"
    assert role.description == "Administrator role"

@pytest.mark.asyncio
async def test_get_role(db_session: AsyncSession):
    role_crud = RoleRepositoryImpl(db_session)
    role_domain = Role(name="editor", description="Editor role")
    created_role = await role_crud.create(role_domain)

    role = await role_crud.get(created_role.id)
    assert role.name == "editor"

@pytest.mark.asyncio
async def test_get_role_not_found(db_session: AsyncSession):
    role_crud = RoleRepositoryImpl(db_session)
    role = await role_crud.get(UUID("00000000-0000-0000-0000-000000000000"))
    assert role is None

@pytest.mark.asyncio
async def test_get_role_by_name(db_session: AsyncSession):
    role_crud = RoleRepositoryImpl(db_session)
    role_domain = Role(name="viewer", description="Viewer role")
    created_role = await role_crud.create(role_domain)

    role = await role_crud.get_by_name(name="viewer")
    assert role.name == "viewer"

@pytest.mark.asyncio
async def test_get_role_by_name_not_found(db_session: AsyncSession):
    role_crud = RoleRepositoryImpl(db_session)
    role = await role_crud.get_by_name("nonexistent")
    assert role is None

@pytest.mark.asyncio
async def test_update_role(db_session: AsyncSession):
    role_crud = RoleRepositoryImpl(db_session)
    role_domain = Role(name="moderator", description="Moderator role")
    created_role = await role_crud.create(role_domain)

    updated_role_domain = Role(name=created_role.name, description="Updated Moderator role", id=created_role.id)
    updated_role = await role_crud.update(updated_role_domain)

    assert updated_role.description == "Updated Moderator role"
    assert updated_role.name == "moderator"

@pytest.mark.asyncio
async def test_delete_role(db_session: AsyncSession):
    role_crud = RoleRepositoryImpl(db_session)
    role_domain = Role(name="guest", description="Guest role")
    created_role = await role_crud.create(role_domain)

    deleted_role = await role_crud.delete(created_role.id)
    assert await role_crud.get(created_role.id) is None

@pytest.mark.asyncio
async def test_get_multi_roles(db_session: AsyncSession):
    role_crud = RoleRepositoryImpl(db_session)
    await role_crud.create(Role(name="role1", description="Role One"))
    await role_crud.create(Role(name="role2", description="Role Two"))
    await role_crud.create(Role(name="role3", description="Role Three"))

    roles = await role_crud.list()
    assert len(roles) == 3 # Debe contener exactamente los 3 roles creados en este test
    assert any(r.name == "role1" for r in roles)
    assert any(r.name == "role2" for r in roles)
    assert any(r.name == "role3" for r in roles)

    # La segunda llamada a list() debería devolver lo mismo si no hay offset/limit
    roles_offset = await role_crud.list()
    assert len(roles_offset) == 3
    assert any(r.name == "role1" for r in roles_offset)
    assert any(r.name == "role2" for r in roles_offset)
    assert any(r.name == "role3" for r in roles_offset)
    assert roles_offset[0].name == "role2"

@pytest.mark.asyncio
async def test_get_multi_roles_with_filter(db_session: AsyncSession):
    role_crud = RoleRepositoryImpl(db_session)
    await role_crud.create(Role(name="filtered_role", description="A role to be filtered"))
    await role_crud.create(Role(name="another_role", description="Another role"))

    roles = await role_crud.filter_by(name="filtered_role")
    assert len(roles) == 1
    assert roles[0].name == "filtered_role"

    roles_no_match = await role_crud.filter_by(name="nonexistent_role")
    assert len(roles_no_match) == 0
