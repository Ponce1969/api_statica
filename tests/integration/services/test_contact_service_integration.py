"""
Tests de integración para ContactService.
Estos tests prueban la interacción entre el servicio y la base de datos real.
"""
import uuid
from datetime import datetime, UTC

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.contact import ContactRepository
from app.domain.exceptions.base import EntityNotFoundError
from app.domain.models.contact import Contact as ContactDomain
from app.schemas.contact import ContactCreate
from app.services.contact_service import ContactService


@pytest.fixture
async def contact_repository(db_session: AsyncSession) -> ContactRepository:
    """Fixture para crear un repositorio de contactos real."""
    return ContactRepository(db=db_session)


@pytest.fixture
async def contact_service(contact_repository: ContactRepository) -> ContactService:
    """Fixture para crear un ContactService con un repositorio real."""
    return ContactService(contact_repository=contact_repository)


@pytest.fixture
async def sample_contact(contact_repository: ContactRepository) -> ContactDomain:
    """Fixture para crear un contacto de prueba en la base de datos."""
    contact = ContactDomain(
        id=uuid.uuid4(),
        full_name="Test Contact",
        email="test@contact.com",
        message="This is a test message."
    )
    return await contact_repository.create(contact)


@pytest.fixture
async def read_contact(contact_repository: ContactRepository) -> ContactDomain:
    """Fixture para crear un contacto leído de prueba en la base de datos."""
    contact = ContactDomain(
        id=uuid.uuid4(),
        full_name="Read Contact",
        email="read@contact.com",
        message="This is a read message.",
        is_read=True
    )
    return await contact_repository.create(contact)


@pytest.mark.asyncio
async def test_get_contact_integration(
    contact_service: ContactService, sample_contact: ContactDomain
) -> None:
    """Test de integración para get_contact."""
    found_contact = await contact_service.get_contact(sample_contact.id)
    assert found_contact is not None
    assert found_contact.id == sample_contact.id
    assert found_contact.email == sample_contact.email


@pytest.mark.asyncio
async def test_get_contact_not_found_integration(contact_service: ContactService) -> None:
    """Test de integración para get_contact cuando el contacto no existe."""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundError) as excinfo:
        await contact_service.get_contact(non_existent_id)
    assert str(non_existent_id) in str(excinfo.value)
    assert "Contacto" in str(excinfo.value)


@pytest.mark.asyncio
async def test_create_contact_integration(
    contact_service: ContactService, contact_repository: ContactRepository
) -> None:
    """Test de integración para create_contact."""
    contact_create = ContactCreate(
        full_name="New Contact",
        email="new@contact.com",
        message="A new message."
    )
    created_contact = await contact_service.create_contact(contact_create)

    assert created_contact is not None
    assert created_contact.full_name == contact_create.full_name
    assert created_contact.email == contact_create.email

    db_contact = await contact_repository.get(created_contact.id)
    assert db_contact is not None
    assert db_contact.email == created_contact.email


@pytest.mark.asyncio
async def test_update_contact_integration(
    contact_service: ContactService, sample_contact: ContactDomain, contact_repository: ContactRepository
) -> None:
    """Test de integración para update_contact."""
    updated_full_name = "Updated Contact Name"
    updated_email = "updated@contact.com"
    updated_message = "Updated message content."

    contact_to_update = ContactDomain(
        id=sample_contact.id,
        full_name=updated_full_name,
        email=updated_email,
        message=updated_message,
        is_read=True
    )

    updated_contact = await contact_service.update_contact(contact_to_update)

    assert updated_contact.id == sample_contact.id
    assert updated_contact.full_name == updated_full_name
    assert updated_contact.email == updated_email
    assert updated_contact.message == updated_message
    assert updated_contact.is_read is True

    db_contact = await contact_repository.get(sample_contact.id)
    assert db_contact is not None
    assert db_contact.full_name == updated_full_name
    assert db_contact.email == updated_email
    assert db_contact.message == updated_message
    assert db_contact.is_read is True


@pytest.mark.asyncio
async def test_update_contact_not_found_integration(contact_service: ContactService) -> None:
    """Test de integración para update_contact cuando el contacto no existe."""
    non_existent_id = uuid.uuid4()
    contact_to_update = ContactDomain(
        id=non_existent_id,
        full_name="Non Existent",
        email="nonexistent@contact.com",
        message="Message"
    )
    with pytest.raises(EntityNotFoundError) as excinfo:
        await contact_service.update_contact(contact_to_update)
    assert str(non_existent_id) in str(excinfo.value)


@pytest.mark.asyncio
async def test_delete_contact_integration(
    contact_service: ContactService, contact_repository: ContactRepository
) -> None:
    """Test de integración para delete_contact."""
    contact_to_delete = ContactDomain(
        id=uuid.uuid4(),
        full_name="To Delete",
        email="todelete@contact.com",
        message="Delete this."
    )
    created_contact = await contact_repository.create(contact_to_delete)

    await contact_service.delete_contact(created_contact.id)

    with pytest.raises(EntityNotFoundError):
        await contact_repository.get(created_contact.id)


@pytest.mark.asyncio
async def test_delete_contact_not_found_integration(contact_service: ContactService) -> None:
    """Test de integración para delete_contact cuando el contacto no existe."""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundError) as excinfo:
        await contact_service.delete_contact(non_existent_id)
    assert str(non_existent_id) in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_contacts_by_email_integration(
    contact_service: ContactService, sample_contact: ContactDomain
) -> None:
    """Test de integración para get_contacts_by_email."""
    found_contacts = await contact_service.get_contacts_by_email(sample_contact.email)
    assert len(found_contacts) == 1
    assert found_contacts[0].id == sample_contact.id


@pytest.mark.asyncio
async def test_get_contacts_integration(
    contact_service: ContactService, sample_contact: ContactDomain, read_contact: ContactDomain
) -> None:
    """Test de integración para get_contacts sin filtros."""
    contacts = await contact_service.get_contacts()
    assert len(contacts) >= 2
    contact_ids = [c.id for c in contacts]
    assert sample_contact.id in contact_ids
    assert read_contact.id in contact_ids


@pytest.mark.asyncio
async def test_get_contacts_with_email_filter_integration(
    contact_service: ContactService, sample_contact: ContactDomain, read_contact: ContactDomain
) -> None:
    """Test de integración para get_contacts con filtro de email."""
    contacts = await contact_service.get_contacts(email=sample_contact.email)
    assert len(contacts) == 1
    assert contacts[0].id == sample_contact.id

    contacts_read = await contact_service.get_contacts(email=read_contact.email)
    assert len(contacts_read) == 1
    assert contacts_read[0].id == read_contact.id


@pytest.mark.asyncio
async def test_get_contacts_with_is_read_filter_integration(
    contact_service: ContactService, sample_contact: ContactDomain, read_contact: ContactDomain
) -> None:
    """Test de integración para get_contacts con filtro de is_read."""
    unread_contacts = await contact_service.get_contacts(is_read=False)
    assert any(c.id == sample_contact.id for c in unread_contacts)
    assert not any(c.id == read_contact.id for c in unread_contacts)

    read_contacts = await contact_service.get_contacts(is_read=True)
    assert any(c.id == read_contact.id for c in read_contacts)
    assert not any(c.id == sample_contact.id for c in read_contacts)


@pytest.mark.asyncio
async def test_update_contact_message_integration(
    contact_service: ContactService, sample_contact: ContactDomain, contact_repository: ContactRepository
) -> None:
    """Test de integración para update_contact_message."""
    new_message = "This is the updated message."
    updated_contact = await contact_service.update_contact_message(
        sample_contact.id, new_message
    )

    assert updated_contact.id == sample_contact.id
    assert updated_contact.message == new_message
    assert updated_contact.updated_at > sample_contact.updated_at

    db_contact = await contact_repository.get(sample_contact.id)
    assert db_contact is not None
    assert db_contact.message == new_message
    assert db_contact.updated_at == updated_contact.updated_at


@pytest.mark.asyncio
async def test_update_contact_message_not_found_integration(contact_service: ContactService) -> None:
    """Test de integración para update_contact_message cuando el contacto no existe."""
    non_existent_id = uuid.uuid4()
    with pytest.raises(EntityNotFoundError) as excinfo:
        await contact_service.update_contact_message(non_existent_id, "Any message")
    assert str(non_existent_id) in str(excinfo.value)
