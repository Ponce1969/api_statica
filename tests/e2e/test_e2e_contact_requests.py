import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.crud.user import UserRepository
from app.domain.models.user import User
from app.core.security.hashing import get_password_hash
from app.domain.models.role import Role
from app.crud.role import RoleRepositoryImpl

@pytest_asyncio.fixture(scope="function")
async def create_admin_user_and_token(db_session_e2e: AsyncSession, test_app: AsyncClient):
    email = "admin_contact@example.com"
    password = "admin_password"
    hashed_password = get_password_hash(password)
    user_repository = UserRepository(db=db_session_e2e)
    admin_user = await user_repository.create(User(email=email, full_name="Admin Contact User"), hashed_password=hashed_password)

    # Assign admin role (assuming role management is setup)
    role_repository = RoleRepositoryImpl(db=db_session_e2e)
    admin_role = await role_repository.get_by_name(name="admin")
    if not admin_role:
        admin_role = await role_repository.create(Role(name="admin", description="Administrator"))
    
    admin_user.roles.append(admin_role)
    await db_session_e2e.commit()
    await db_session_e2e.refresh(admin_user)

    login_data = {
        "username": email,
        "password": password
    }
    response = await test_app.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"user": admin_user, "token": token}

@pytest.mark.asyncio
async def test_create_contact_request(test_app: AsyncClient):

    contact_data = {
        "full_name": "Test Contact",
        "email": "contact@example.com",
        "message": "This is a test message."
    }
    response = await test_app.post("/api/v1/contacts/", json=contact_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == contact_data["full_name"]
    assert data["email"] == contact_data["email"]
    assert data["message"] == contact_data["message"]
    assert data["is_read"] is False
    assert "id" in data

@pytest.mark.asyncio
async def test_get_contact_requests_unauthenticated(test_app: AsyncClient):
    response = await test_app.get("/api/v1/contacts/")
    assert response.status_code == 401 # Unauthorized

@pytest.mark.asyncio
async def test_get_contact_requests_authenticated_admin(test_app: AsyncClient, create_admin_user_and_token: dict):
    headers = {"Authorization": f"Bearer {create_admin_user_and_token['token']}"}
    
    # Create a contact first to ensure there's data
    contact_data = {
        "full_name": "Another Contact",
        "email": "another@example.com",
        "message": "Another test message."
    }
    await test_app.post("/api/v1/contacts/", json=contact_data)

    response = await test_app.get("/api/v1/contacts/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(c["email"] == "another@example.com" for c in data)

@pytest.mark.asyncio
async def test_update_contact_request_status(test_app: AsyncClient, create_admin_user_and_token: dict):
    headers = {"Authorization": f"Bearer {create_admin_user_and_token['token']}"}

    # Create a contact to update
    contact_data = {
        "full_name": "Update Contact",
        "email": "update@example.com",
        "message": "Message to update."
    }
    create_response = await test_app.post("/api/v1/contacts/", json=contact_data)
    contact_id = create_response.json()["id"]

    update_data = {"is_read": True}
    response = await test_app.put(f"/api/v1/contacts/{contact_id}", headers=headers, json=update_data)
    assert response.status_code == 200
    updated_contact = response.json()
    assert updated_contact["is_read"] is True
    assert updated_contact["id"] == contact_id

@pytest.mark.asyncio
async def test_delete_contact_request(test_app: AsyncClient, create_admin_user_and_token: dict):
    headers = {"Authorization": f"Bearer {create_admin_user_and_token['token']}"}

    # Create a contact to delete
    contact_data = {
        "full_name": "Delete Contact",
        "email": "delete@example.com",
        "message": "Message to delete."
    }
    create_response = await test_app.post("/api/v1/contacts/", json=contact_data)
    contact_id = create_response.json()["id"]

    response = await test_app.delete(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200
    deleted_contact = response.json()
    assert deleted_contact["id"] == contact_id

    # Verify it's actually deleted
    response = await test_app.get(f"/api/v1/contacts/{contact_id}", headers=headers)
    assert response.status_code == 404 # Not Found
