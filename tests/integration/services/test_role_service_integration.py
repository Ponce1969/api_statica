"""
Tests de integración para RoleService.
Estos tests prueban la interacción entre el servicio y la base de datos real.
"""
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.role import RoleRepositoryImpl
from app.domain.exceptions.base import EntityNotFoundError, ValidationError
from app.domain.models.role import Role as RoleDomain
from app.schemas.role import RoleCreate
from app.services.role_service import RoleService


@pytest.fixture
async def role_repository(db_session: AsyncSession) -> RoleRepositoryImpl:
    """Fixture para crear un repositorio de roles real."""
    return RoleRepositoryImpl(db_session)


@pytest.fixture
async def role_service(role_repository: RoleRepositoryImpl) -> RoleService:
    """Fixture para crear un RoleService con un repositorio real."""
    return RoleService(role_repository=role_repository)


@pytest.fixture
async def sample_role(role_repository: RoleRepositoryImpl) -> RoleDomain:
    """Fixture para crear un rol de prueba en la base de datos."""
    role = RoleDomain(
        id=uuid.uuid4(),
        name="sample_role",
        description="A sample role for testing"
    )
    return await role_repository.create(role)


@pytest.mark.asyncio
async def test_get_role_integration(
    role_service: RoleService, sample_role: RoleDomain
) -> None:
    """Test de integración para get_role."""
    found_role = await role_service.get_role(sample_role.id)
    assert found_role is not None
    assert found_role.id == sample_role.id
    assert found_role.name == sample_role.name


@pytest.mark.asyncio
async def test_get_role_not_found_integration(role_service: RoleService) -> None:
    """Test de integración para get_role cuando el rol no existe."""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundError) as excinfo:
        await role_service.get_role(non_existent_id)
    assert str(non_existent_id) in str(excinfo.value)
    assert "Rol" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_role_by_name_integration(
    role_service: RoleService, sample_role: RoleDomain
) -> None:
    """Test de integración para get_role_by_name."""
    found_role = await role_service.get_role_by_name(sample_role.name)
    assert found_role is not None
    assert found_role.id == sample_role.id
    assert found_role.name == sample_role.name


@pytest.mark.asyncio
async def test_get_role_by_name_not_found_integration(role_service: RoleService) -> None:
    """Test de integración para get_role_by_name cuando el rol no existe."""
    found_role = await role_service.get_role_by_name("non_existent_role")
    assert found_role is None


@pytest.mark.asyncio
async def test_create_role_integration(
    role_service: RoleService, role_repository: RoleRepositoryImpl
) -> None:
    """Test de integración para create_role."""
    role_create = RoleCreate(
        name="new_role",
        description="A newly created role"
    )
    created_role = await role_service.create_role(role_create)

    assert created_role is not None
    assert created_role.name == role_create.name
    assert created_role.description == role_create.description

    db_role = await role_repository.get_by_name(role_create.name)
    assert db_role is not None
    assert db_role.id == created_role.id


@pytest.mark.asyncio
async def test_create_role_name_exists_integration(
    role_service: RoleService, sample_role: RoleDomain
) -> None:
    """Test de integración para create_role cuando el nombre del rol ya existe."""
    role_create = RoleCreate(
        name=sample_role.name, # Nombre que ya existe
        description="Another role with existing name"
    )
    with pytest.raises(ValidationError) as excinfo:
        await role_service.create_role(role_create)
    expected_msg = f"Ya existe un rol con el nombre {sample_role.name}"
    assert expected_msg in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_role_integration(
    role_service: RoleService, sample_role: RoleDomain, role_repository: RoleRepositoryImpl
) -> None:
    """Test de integración para update_role."""
    updated_name = "updated_sample_role"
    updated_description = "Updated description for sample role"
    
    # Crear una instancia de RoleDomain con los datos actualizados
    role_to_update = RoleDomain(
        id=sample_role.id,
        name=updated_name,
        description=updated_description
    )
    
    updated_role = await role_service.update_role(role_to_update)

    assert updated_role.id == sample_role.id
    assert updated_role.name == updated_name
    assert updated_role.description == updated_description

    db_role = await role_repository.get(sample_role.id)
    assert db_role is not None
    assert db_role.name == updated_name
    assert db_role.description == updated_description


@pytest.mark.asyncio
async def test_update_role_not_found_integration(role_service: RoleService) -> None:
    """Test de integración para update_role cuando el rol no existe."""
    non_existent_id = uuid.uuid4()
    role_to_update = RoleDomain(
        id=non_existent_id,
        name="non_existent_role",
        description="Description"
    )
    with pytest.raises(EntityNotFoundError) as excinfo:
        await role_service.update_role(role_to_update)
    assert str(non_existent_id) in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_role_name_exists_integration(
    role_service: RoleService, sample_role: RoleDomain, role_repository: RoleRepositoryImpl
) -> None:
    """Test de integración para update_role cuando el nuevo nombre ya existe."""
    # Crear un segundo rol para tener un nombre existente
    existing_role_name = "another_role"
    another_role = RoleDomain(
        id=uuid.uuid4(),
        name=existing_role_name,
        description="Another role"
    )
    await role_repository.create(another_role)

    # Intentar actualizar sample_role con el nombre de another_role
    role_to_update = RoleDomain(
        id=sample_role.id,
        name=existing_role_name,
        description="Updated description"
    )
    with pytest.raises(ValidationError) as excinfo:
        await role_service.update_role(role_to_update)
    expected_msg = f"Ya existe un rol con el nombre {existing_role_name}"
    assert expected_msg in str(excinfo.value)


@pytest.mark.asyncio
async def test_delete_role_integration(
    role_service: RoleService, role_repository: RoleRepositoryImpl
) -> None:
    """Test de integración para delete_role."""
    role_to_delete = RoleDomain(
        id=uuid.uuid4(),
        name="to_delete_role",
        description="Role to be deleted"
    )
    created_role = await role_repository.create(role_to_delete)

    await role_service.delete_role(created_role.id)

    with pytest.raises(EntityNotFoundError):
        await role_repository.get(created_role.id)


@pytest.mark.asyncio
async def test_delete_role_not_found_integration(role_service: RoleService) -> None:
    """Test de integración para delete_role cuando el rol no existe."""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundError) as excinfo:
        await role_service.delete_role(non_existent_id)
    assert str(non_existent_id) in str(excinfo.value)

