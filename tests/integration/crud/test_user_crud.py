import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.domain.models.user import User
from app.database.models import User as UserORM
from uuid import UUID
from app.core.security.hashing import get_password_hash

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user_crud = UserRepository(db_session)
    user_domain = User(email="test@example.com", full_name="Test User")
    hashed_password = get_password_hash("testpassword")
    user = await user_crud.create(user_domain, hashed_password=hashed_password)
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"

    assert user.is_active is True

@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession):
    user_crud = UserRepository(db_session)
    user_domain = User(email="get@example.com", full_name="Get User")
    hashed_password = get_password_hash("getpassword")
    created_user = await user_crud.create(user_domain, hashed_password=hashed_password)

    user = await user_crud.get(created_user.id)
    assert user.email == "get@example.com"

@pytest.mark.asyncio
async def test_get_user_not_found(db_session: AsyncSession):
    user_crud = UserRepository(db_session)
    user = await user_crud.get(UUID("00000000-0000-0000-0000-000000000000"))
    assert user is None

@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession):
    user_crud = UserRepository(db_session)
    user_domain = User(email="byemail@example.com", full_name="User By Email")
    hashed_password = get_password_hash("byemailpassword")
    created_user = await user_crud.create(user_domain, hashed_password=hashed_password)

    user = await user_crud.get_by_email(email="byemail@example.com")
    assert user is not None
    assert user.email == "byemail@example.com"

@pytest.mark.asyncio
async def test_get_user_by_email_not_found(db_session: AsyncSession):
    user_crud = UserRepository(db_session)
    user = await user_crud.get_by_email(email="nonexistent@example.com")
    assert user is None

@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    user_crud = UserRepository(db_session)
    user_domain = User(email="update@example.com", full_name="Update User")
    hashed_password = get_password_hash("updatepassword")
    created_user = await user_crud.create(user_domain, hashed_password=hashed_password)

    updated_user_domain = User(email=created_user.email, full_name="Updated User Name", id=created_user.id, is_active=False)
    updated_user = await user_crud.update(updated_user_domain)

    assert updated_user.full_name == "Updated User Name"
    assert updated_user.is_active is False
    assert updated_user.email == "update@example.com" # Email should not change if not provided in update

@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    user_crud = UserRepository(db_session)
    user_domain = User(email="delete@example.com", full_name="Delete User")
    hashed_password = get_password_hash("deletepassword")
    created_user = await user_crud.create(user_domain, hashed_password=hashed_password)

    deleted_user = await user_crud.delete(created_user.id)
    assert await user_crud.get(created_user.id) is None

@pytest.mark.asyncio
async def test_get_multi_users(db_session: AsyncSession):
    user_crud = UserRepository(db_session)
    await user_crud.create(User(email="multi1@example.com", full_name="User One"), hashed_password=get_password_hash("multi1pass"))
    await user_crud.create(User(email="multi2@example.com", full_name="User Two"), hashed_password=get_password_hash("multi2pass"))
    await user_crud.create(User(email="multi3@example.com", full_name="User Three"), hashed_password=get_password_hash("multi3pass"))

    users = await user_crud.list()
    assert len(users) == 3 # Should contain exactly the 3 users created in this test
    assert any(u.email == "multi1@example.com" for u in users)
    assert any(u.email == "multi2@example.com" for u in users)
    assert any(u.email == "multi3@example.com" for u in users)

@pytest.mark.asyncio
async def test_get_multi_users_with_filter(db_session: AsyncSession):
    user_crud = UserRepository(db_session)
    await user_crud.create(User(email="filter1@example.com", full_name="Filter User One"), hashed_password=get_password_hash("filter1pass"))
    await user_crud.create(User(email="filter2@example.com", full_name="Another User"), hashed_password=get_password_hash("filter2pass"))

    users = await user_crud.filter_by(full_name="Filter User One")
    assert len(users) == 1
    assert users[0].email == "filter1@example.com"

    users_no_match = await user_crud.filter_by(full_name="Non Existent")
    assert len(users_no_match) == 0
