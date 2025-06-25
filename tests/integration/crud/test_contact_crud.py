import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.contact import ContactRepository
from app.schemas.contact import ContactCreate, ContactUpdate
from app.domain.models.contact import Contact
from uuid import UUID

@pytest.mark.asyncio
async def test_create_contact(db_session: AsyncSession):
    contact_crud = ContactRepository(db_session)
    contact_domain = Contact(full_name="Test Contact", email="test@example.com", message="This is a test message.")
    contact = await contact_crud.create(contact_domain)
    assert contact.full_name == "Test Contact"
    assert contact.email == "test@example.com"
    assert contact.message == "This is a test message."
    assert contact.is_read is False

@pytest.mark.asyncio
async def test_get_contact(db_session: AsyncSession):
    contact_crud = ContactRepository(db_session)
    contact_domain = Contact(full_name="Get Contact", email="get@example.com", message="Message for get.")
    created_contact = await contact_crud.create(contact_domain)

    contact = await contact_crud.get(created_contact.id)
    assert contact.email == "get@example.com"

@pytest.mark.asyncio
async def test_get_contact_not_found(db_session: AsyncSession):
    contact_crud = ContactRepository(db_session)
    contact = await contact_crud.get(UUID("00000000-0000-0000-0000-000000000000"))
    assert contact is None

@pytest.mark.asyncio
async def test_update_contact(db_session: AsyncSession):
    contact_crud = ContactRepository(db_session)
    contact_domain = Contact(full_name="Update Contact", email="update@example.com", message="Original message.")
    created_contact = await contact_crud.create(contact_domain)

    updated_contact_domain = Contact(full_name=created_contact.full_name, email=created_contact.email, message="Updated message.", id=created_contact.id, is_read=True)
    updated_contact = await contact_crud.update(updated_contact_domain)

    assert updated_contact.message == "Updated message."
    assert updated_contact.is_read is True
    assert updated_contact.email == "update@example.com"

@pytest.mark.asyncio
async def test_delete_contact(db_session: AsyncSession):
    contact_crud = ContactRepository(db_session)
    contact_domain = Contact(full_name="Delete Contact", email="delete@example.com", message="Message for delete.")
    created_contact = await contact_crud.create(contact_domain)

    await contact_crud.delete(created_contact.id)
    assert await contact_crud.get(created_contact.id) is None

@pytest.mark.asyncio
async def test_get_multi_contacts(db_session: AsyncSession):
    contact_crud = ContactRepository(db_session)
    await contact_crud.create(Contact(full_name="Contact 1", email="c1@example.com", message="Msg 1"))
    await contact_crud.create(Contact(full_name="Contact 2", email="c2@example.com", message="Msg 2"))
    await contact_crud.create(Contact(full_name="Contact 3", email="c3@example.com", message="Msg 3"))

    contacts = await contact_crud.list()
    assert len(contacts) == 3
    assert contacts[0].email == "c1@example.com"
    assert contacts[1].email == "c2@example.com"
    assert contacts[2].email == "c3@example.com"

    # Test filtering with limit and skip if the repository supported it, or use filter_by
    # For now, just assert on the full list
    # contacts_offset = await contact_crud.list()
    # assert len(contacts_offset) == 3
    # assert contacts_offset[0].email == "c1@example.com"

@pytest.mark.asyncio
async def test_get_multi_contacts_with_filter(db_session: AsyncSession):
    contact_crud = ContactRepository(db_session)
    await contact_crud.create(Contact(full_name="Filtered Contact", email="filtered@example.com", message="Filtered message."))
    await contact_crud.create(Contact(full_name="Another Contact", email="another@example.com", message="Another message."))

    contacts = await contact_crud.filter_by(full_name="Filtered Contact")
    assert len(contacts) == 1
    assert contacts[0].email == "filtered@example.com"

    contacts_no_match = await contact_crud.filter_by(full_name="Non Existent")
    assert len(contacts_no_match) == 0
