import pytest
from httpx import AsyncClient
from app.main import app
from app.crud.user import UserRepository
from app.crud.role import RoleRepositoryImpl
from app.domain.models.user import User
from app.domain.models.role import Role
from app.core.security.hashing import get_password_hash
from app.database.models import user_roles
from sqlalchemy import insert

@pytest.fixture(scope="module")
async def get_admin_token(test_app: AsyncClient, db_session_e2e: AsyncSession):
    # Create an admin user and a role for testing directly via repositories
    email = "admin_contact_e2e@example.com"
    password = "adminpassword"
    hashed_password = get_password_hash(password)

    user_repository = UserRepository(db=db_session_e2e)
    role_repository = RoleRepositoryImpl(session=db_session_e2e)

    admin_user = await user_repository.create(
        entity=User(email=email, full_name="Admin User Contact E2E"),
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
async def test_create_contact_e2e(test_app: AsyncClient):
    contact_data = {
        "full_name": "E2E Contact",
        "email": "e2e_contact@example.com",
        "message": "This is an E2E test message."
    }
    response = await test_app.post("/api/v1/contacts/", json=contact_data)
    assert response.status_code == 200 # Changed from 201 to 200 based on previous API behavior
    data = response.json()
    assert data["full_name"] == contact_data["full_name"]
    assert data["email"] == contact_data["email"]
    assert data["message"] == contact_data["message"]
    assert data["is_read"] is False

@pytest.mark.asyncio
async def test_get_contacts_e2e(test_app: AsyncClient, get_admin_token: str):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    response = await test_app.get("/api/v1/contacts/", headers=headers)
    assert response.status_code == 200
    contacts = response.json()
    assert isinstance(contacts, list)
    # Assuming at least one contact created by test_create_contact_e2e or manually
    assert len(contacts) >= 1

@pytest.mark.asyncio
async def test_update_contact_e2e(test_app: AsyncClient, get_admin_token: str):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    # Create a contact to update
    contact_data = {"full_name": "Update Me", "email": "update_me@example.com", "message": "Original message."}
    create_response = await test_app.post("/api/v1/contacts/", json=contact_data)
    assert create_response.status_code == 200
    contact_id = create_response.json()["id"]

    update_data = {"is_read": True, "message": "Updated message from E2E"}
    response = await test_app.put(f"/api/v1/contacts/{contact_id}", headers=headers, json=update_data)
    assert response.status_code == 200
    updated_contact = response.json()
    assert updated_contact["is_read"] is True
    assert updated_contact["message"] == "Updated message from E2E"

@pytest.mark.asyncio
async def test_delete_contact_e2e(test_app: AsyncClient, get_admin_token: str):
    headers = {"Authorization": f"Bearer {get_admin_token}"}
    # Create a contact to delete
    contact_data = {"full_name": "Delete Me", "email": "delete_me@example.com", "message": "Delete this message."}
    create_response = await test_app.post("/api/v1/contacts/", json=contact_data)
    assert create_response.status_code == 200
    contact_id = create_response.json()["id"]

    response = await test_app.delete(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200
    deleted_contact = response.json()
    assert deleted_contact["id"] == contact_id

    # Verify contact is actually deleted
    response = await test_app.get(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert response.status_code == 404 # Not Found
