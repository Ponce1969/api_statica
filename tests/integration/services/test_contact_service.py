import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.base import EntityNotFoundError
from app.domain.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import ContactService
from app.crud.contact import ContactRepository # Assuming ContactRepository is the concrete implementation of IContactRepository

@pytest.fixture
async def contact_service_integration(db_session: AsyncSession) -> ContactService:
    # Use the actual CRUDContact for integration tests
    contact_repository = ContactRepository(Contact, db_session)
    return ContactService(contact_repository=contact_repository)

@pytest.mark.asyncio
async def test_integration_get_contact(db_session: AsyncSession, contact_service_integration: ContactService):
    # Create a contact directly in DB for testing
    new_contact = Contact(entity_id=uuid4(), full_name="Integration Contact", email="integration@example.com", message="Test message")
    await ContactRepository(Contact, db_session).create(obj_in=new_contact)
    
    # Get the contact using the service
    fetched_contact = await contact_service_integration.get_contact(new_contact.id)
    assert fetched_contact.email == "integration@example.com"
    assert fetched_contact.full_name == "Integration Contact"

@pytest.mark.asyncio
async def test_integration_get_contact_not_found(contact_service_integration: ContactService):
    with pytest.raises(EntityNotFoundError):
        await contact_service_integration.get_contact(uuid4())

@pytest.mark.asyncio
async def test_integration_get_contacts_no_filter(db_session: AsyncSession, contact_service_integration: ContactService):
    await ContactRepository(Contact, db_session).create(obj_in=Contact(entity_id=uuid4(), full_name="Contact1", email="contact1@example.com", message="Msg1"))
    await ContactRepository(Contact, db_session).create(obj_in=Contact(entity_id=uuid4(), full_name="Contact2", email="contact2@example.com", message="Msg2"))

    contacts = await contact_service_integration.get_contacts()
    assert len(contacts) >= 2 # May contain contacts from other tests if not properly isolated
    assert any(c.email == "contact1@example.com" for c in contacts)

@pytest.mark.asyncio
async def test_integration_get_contacts_filter_by_email(db_session: AsyncSession, contact_service_integration: ContactService):
    email_to_filter = "filtered@example.com"
    await ContactRepository(Contact, db_session).create(obj_in=Contact(entity_id=uuid4(), full_name="Filtered Contact", email=email_to_filter, message="Filtered Msg"))
    await ContactRepository(Contact, db_session).create(obj_in=Contact(entity_id=uuid4(), full_name="Other Contact", email="other@example.com", message="Other Msg"))

    contacts = await contact_service_integration.get_contacts(email=email_to_filter)
    assert len(contacts) == 1
    assert contacts[0].email == email_to_filter

@pytest.mark.asyncio
async def test_integration_get_contacts_filter_by_is_read(db_session: AsyncSession, contact_service_integration: ContactService):
    await ContactRepository(Contact, db_session).create(obj_in=Contact(entity_id=uuid4(), full_name="Read Contact", email="read@example.com", message="Read Msg", is_read=True))
    await ContactRepository(Contact, db_session).create(obj_in=Contact(entity_id=uuid4(), full_name="Unread Contact", email="unread@example.com", message="Unread Msg", is_read=False))

    contacts = await contact_service_integration.get_contacts(is_read=True)
    assert len(contacts) == 1
    assert contacts[0].email == "read@example.com"

@pytest.mark.asyncio
async def test_integration_create_contact(db_session: AsyncSession, contact_service_integration: ContactService):
    contact_in = ContactCreate(full_name="New Service Contact", email="newservice@example.com", message="Created via service")
    created_contact = await contact_service_integration.create_contact(contact_in)

    assert created_contact.email == "newservice@example.com"
    # Verify it's in the DB
    retrieved_contact = await ContactRepository(Contact, db_session).get(id=created_contact.id)
    assert retrieved_contact.email == "newservice@example.com"

@pytest.mark.asyncio
async def test_integration_update_contact(db_session: AsyncSession, contact_service_integration: ContactService):
    original_contact = Contact(entity_id=uuid4(), full_name="Update Me", email="updateme@example.com", message="Original Msg")
    await ContactRepository(Contact, db_session).create(obj_in=original_contact)

    updated_contact_data = Contact(entity_id=original_contact.id, full_name="Updated Service Contact", email="updatedservice@example.com", message="Updated Msg", is_read=True)
    updated_contact = await contact_service_integration.update_contact(updated_contact_data)

    assert updated_contact.email == "updatedservice@example.com"
    assert updated_contact.is_read is True
    # Verify it's updated in the DB
    retrieved_contact = await ContactRepository(Contact, db_session).get(id=original_contact.id)
    assert retrieved_contact.email == "updatedservice@example.com"

@pytest.mark.asyncio
async def test_integration_delete_contact(db_session: AsyncSession, contact_service_integration: ContactService):
    contact_to_delete = Contact(entity_id=uuid4(), full_name="Delete Me", email="deleteme@example.com", message="To be deleted")
    await ContactRepository(Contact, db_session).create(obj_in=contact_to_delete)

    await contact_service_integration.delete_contact(contact_to_delete.id)
    
    # Verify it's deleted from the DB
    retrieved_contact = await ContactRepository(Contact, db_session).get(id=contact_to_delete.id)
    assert retrieved_contact is None

@pytest.mark.asyncio
async def test_integration_delete_contact_not_found(contact_service_integration: ContactService):
    with pytest.raises(EntityNotFoundError):
        await contact_service_integration.delete_contact(uuid4())

@pytest.mark.asyncio
async def test_integration_update_contact_message(db_session: AsyncSession, contact_service_integration: ContactService):
    contact_id = uuid4()
    original_contact = Contact(entity_id=contact_id, full_name="Test", email="test@example.com", message="Old Message")
    await ContactRepository(Contact, db_session).create(obj_in=original_contact)

    updated_contact = await contact_service_integration.update_contact_message(contact_id, "New Integration Message")
    assert updated_contact.message == "New Integration Message"

    retrieved_contact = await ContactRepository(Contact, db_session).get(id=contact_id)
    assert retrieved_contact.message == "New Integration Message"
