import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app
from app.crud.user import UserRepository
from app.crud.role import RoleRepositoryImpl
from app.domain.models.user import User
from app.domain.models.role import Role
from app.core.security.hashing import get_password_hash
from app.database.models import user_roles
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture(scope="module")
async def get_admin_token(test_app: AsyncClient, db_session_e2e: AsyncSession):
    # Create an admin user and a role for testing directly via repositories
    email = "admin_e2e@example.com"
    password = "adminpassword"
    hashed_password = get_password_hash(password)

    user_repository = UserRepository(db=db_session_e2e)
    role_repository = RoleRepositoryImpl(session=db_session_e2e)

    admin_user = await user_repository.create(
        entity=User(email=email, full_name="Admin User E2E"),
        hashed_password=hashed_password
    )

    admin_role = await role_repository.get_by_name(name="admin")
    if not admin_role:
        admin_role = await role_repository.create(entity=Role(name="admin", description="Administrator role"))

    # Associate role with user
    if admin_user and admin_role:
        stmt = insert(user_roles).values(user_id=admin_user.id, role_id=admin_role.id)
        await db_session_e2e.execute(stmt)
        await db_session_e2e.commit()
        await db_session_e2e.refresh(admin_user)

    login_data = {
        "username": email,
        "password": password
    }
    response = await test_app.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_role_e2e(test_app: AsyncClient, get_admin_token: str):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    role_data = {"name": "new_role", "description": "A newly created role"}
    response = await test_app.post("/api/v1/roles/", headers=headers, json=role_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == role_data["name"]
    assert data["description"] == role_data["description"]

@pytest.mark.asyncio
async def test_get_roles_e2e(test_app: AsyncClient, get_admin_token: str):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    response = await test_app.get("/api/v1/roles/", headers=headers)
    assert response.status_code == 200
    roles = response.json()
    assert isinstance(roles, list)
    assert len(roles) > 0 # Should at least contain the 'admin' role created by fixture

@pytest.mark.asyncio
async def test_update_role_e2e(test_app: AsyncClient, get_admin_token: str):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    # Create a role to update
    role_data = {"name": "to_update", "description": "Role to be updated"}
    create_response = await test_app.post("/api/v1/roles/", headers=headers, json=role_data)
    assert create_response.status_code == 200
    role_id = create_response.json()["id"]

    update_data = {"description": "Updated description"}
    response = await test_app.put(f"/api/v1/roles/{role_id}", headers=headers, json=update_data)
    assert response.status_code == 200
    updated_role = response.json()
    assert updated_role["description"] == "Updated description"

@pytest.mark.asyncio
async def test_delete_role_e2e(test_app: AsyncClient, get_admin_token: str):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    # Create a role to delete
    role_data = {"name": "to_delete", "description": "Role to be deleted"}
    create_response = await test_app.post("/api/v1/roles/", headers=headers, json=role_data)
    assert create_response.status_code == 200
    role_id = create_response.json()["id"]

    response = await test_app.delete(f"/api/v1/roles/{role_id}", headers=headers)
    assert response.status_code == 200
    deleted_role = response.json()
    assert deleted_role["id"] == role_id

    # Verify role is actually deleted
    response = await test_app.get(f"/api/v1/roles/{role_id}", headers=headers)
    assert response.status_code == 404 # Not Found
