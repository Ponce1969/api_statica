import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from app.domain.exceptions.base import EntityNotFoundError
from app.domain.models.contact import Contact
from app.domain.repositories.base import IContactRepository
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import ContactService

@pytest.fixture
def mock_contact_repository() -> AsyncMock:
    return AsyncMock(spec=IContactRepository)

@pytest.fixture
def contact_service(mock_contact_repository: AsyncMock) -> ContactService:
    return ContactService(contact_repository=mock_contact_repository)

@pytest.mark.asyncio
async def test_get_contact_success(contact_service: ContactService, mock_contact_repository: AsyncMock):
    contact_id = uuid4()
    mock_contact = Contact(id=contact_id, full_name="John Doe", email="john@example.com", message="Hello")
    mock_contact_repository.get.return_value = mock_contact

    result = await contact_service.get_contact(contact_id)
    assert result == mock_contact
    mock_contact_repository.get.assert_called_once_with(contact_id)

@pytest.mark.asyncio
async def test_get_contact_not_found(contact_service: ContactService, mock_contact_repository: AsyncMock):
    contact_id = uuid4()
    mock_contact_repository.get.return_value = None

    with pytest.raises(EntityNotFoundError):
        await contact_service.get_contact(contact_id)
    mock_contact_repository.get.assert_called_once_with(contact_id)

@pytest.mark.asyncio
async def test_get_contacts_no_filter(contact_service: ContactService, mock_contact_repository: AsyncMock):
    mock_contacts = [
        Contact(id=uuid4(), full_name="John", email="john@example.com", message="Msg1", is_read=False),
        Contact(id=uuid4(), full_name="Jane", email="jane@example.com", message="Msg2", is_read=True),
    ]
    mock_contact_repository.list.return_value = mock_contacts

    results = await contact_service.get_contacts()
    assert len(results) == 2
    assert all(isinstance(c, ContactResponse) for c in results)
    assert results[0].email == "john@example.com"
    mock_contact_repository.list.assert_called_once()

@pytest.mark.asyncio
async def test_get_contacts_filter_by_email(contact_service: ContactService, mock_contact_repository: AsyncMock):
    mock_contacts = [
        Contact(id=uuid4(), full_name="John", email="john@example.com", message="Msg1", is_read=False),
        Contact(id=uuid4(), full_name="Jane", email="jane@example.com", message="Msg2", is_read=True),
    ]
    mock_contact_repository.list.return_value = mock_contacts

    results = await contact_service.get_contacts(email="john@example.com")
    assert len(results) == 1
    assert results[0].email == "john@example.com"
    mock_contact_repository.list.assert_called_once()

@pytest.mark.asyncio
async def test_get_contacts_filter_by_is_read(contact_service: ContactService, mock_contact_repository: AsyncMock):
    mock_contacts = [
        Contact(id=uuid4(), full_name="John", email="john@example.com", message="Msg1", is_read=False),
        Contact(id=uuid4(), full_name="Jane", email="jane@example.com", message="Msg2", is_read=True),
    ]
    mock_contact_repository.list.return_value = mock_contacts

    results = await contact_service.get_contacts(is_read=True)
    assert len(results) == 1
    assert results[0].is_read is True
    mock_contact_repository.list.assert_called_once()

@pytest.mark.asyncio
async def test_get_contacts_filter_by_email_and_is_read(contact_service: ContactService, mock_contact_repository: AsyncMock):
    mock_contacts = [
        Contact(id=uuid4(), full_name="John", email="john@example.com", message="Msg1", is_read=False),
        Contact(id=uuid4(), full_name="Jane", email="jane@example.com", message="Msg2", is_read=True),
        Contact(id=uuid4(), full_name="Peter", email="john@example.com", message="Msg3", is_read=True),
    ]
    mock_contact_repository.list.return_value = mock_contacts

    results = await contact_service.get_contacts(email="john@example.com", is_read=True)
    assert len(results) == 1
    assert results[0].email == "john@example.com"
    assert results[0].is_read is True
    mock_contact_repository.list.assert_called_once()

@pytest.mark.asyncio
async def test_get_contacts_by_email_success(contact_service: ContactService, mock_contact_repository: AsyncMock):
    email = "test@example.com"
    mock_contacts = [
        Contact(id=uuid4(), full_name="Test1", email=email, message="Msg1"),
        Contact(id=uuid4(), full_name="Test2", email=email, message="Msg2"),
    ]
    mock_contact_repository.get_by_email.return_value = mock_contacts

    results = await contact_service.get_contacts_by_email(email)
    assert len(results) == 2
    assert all(c.email == email for c in results)
    mock_contact_repository.get_by_email.assert_called_once_with(email)

@pytest.mark.asyncio
async def test_create_contact_success(contact_service: ContactService, mock_contact_repository: AsyncMock):
    contact_create = ContactCreate(full_name="New Contact", email="new@example.com", message="New message")
    created_contact_model = Contact(id=uuid4(), full_name="New Contact", email="new@example.com", message="New message")
    mock_contact_repository.create.return_value = created_contact_model

    result = await contact_service.create_contact(contact_create)
    assert isinstance(result, ContactResponse)
    assert result.email == "new@example.com"
    mock_contact_repository.create.assert_called_once()

@pytest.mark.asyncio
async def test_update_contact_success(contact_service: ContactService, mock_contact_repository: AsyncMock):
    contact_id = uuid4()
    existing_contact = Contact(id=contact_id, full_name="Old Name", email="old@example.com", message="Old Msg")
    updated_contact_data = Contact(id=contact_id, full_name="Updated Name", email="updated@example.com", message="Updated Msg")

    mock_contact_repository.get.return_value = existing_contact
    mock_contact_repository.update.return_value = updated_contact_data

    result = await contact_service.update_contact(updated_contact_data)
    assert result == updated_contact_data
    mock_contact_repository.get.assert_called_once_with(contact_id)
    mock_contact_repository.update.assert_called_once_with(updated_contact_data)

@pytest.mark.asyncio
async def test_update_contact_not_found(contact_service: ContactService, mock_contact_repository: AsyncMock):
    contact_id = uuid4()
    contact_to_update = Contact(id=contact_id, full_name="Non Existent", email="no@example.com", message="Msg")
    mock_contact_repository.get.return_value = None

    with pytest.raises(EntityNotFoundError):
        await contact_service.update_contact(contact_to_update)
    mock_contact_repository.get.assert_called_once_with(contact_id)
    mock_contact_repository.update.assert_not_called()

@pytest.mark.asyncio
async def test_delete_contact_success(contact_service: ContactService, mock_contact_repository: AsyncMock):
    contact_id = uuid4()
    mock_contact_repository.get.return_value = Contact(id=contact_id, full_name="To Delete", email="delete@example.com", message="Msg")
    mock_contact_repository.delete.return_value = None

    await contact_service.delete_contact(contact_id)
    mock_contact_repository.get.assert_called_once_with(contact_id)
    mock_contact_repository.delete.assert_called_once_with(contact_id)

@pytest.mark.asyncio
async def test_delete_contact_not_found(contact_service: ContactService, mock_contact_repository: AsyncMock):
    contact_id = uuid4()
    mock_contact_repository.get.return_value = None

    with pytest.raises(EntityNotFoundError):
        await contact_service.delete_contact(contact_id)
    mock_contact_repository.get.assert_called_once_with(contact_id)
    mock_contact_repository.delete.assert_not_called()

@pytest.mark.asyncio
async def test_update_contact_message_success(contact_service: ContactService, mock_contact_repository: AsyncMock):
    contact_id = uuid4()
    original_contact = Contact(id=contact_id, full_name="Test", email="test@example.com", message="Old Message")
    updated_contact = Contact(id=contact_id, full_name="Test", email="test@example.com", message="New Message")

    mock_contact_repository.get.return_value = original_contact
    mock_contact_repository.update.return_value = updated_contact

    result = await contact_service.update_contact_message(contact_id, "New Message")
    assert result.message == "New Message"
    mock_contact_repository.get.assert_called_once_with(contact_id)
    mock_contact_repository.update.assert_called_once_with(original_contact) # original_contact should have its message updated internally

@pytest.mark.asyncio
async def test_update_contact_message_not_found(contact_service: ContactService, mock_contact_repository: AsyncMock):
    contact_id = uuid4()
    mock_contact_repository.get.return_value = None

    with pytest.raises(EntityNotFoundError):
        await contact_service.update_contact_message(contact_id, "New Message")
    mock_contact_repository.get.assert_called_once_with(contact_id)
    mock_contact_repository.update.assert_not_called()
