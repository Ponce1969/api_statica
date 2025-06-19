# tests/unit/domain/models/test_contact_domain.py
import time
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.domain.exceptions.base import StructuralValidationError, ValidationError
from app.domain.models.contact import Contact

VALID_FULL_NAME = "Test User"
VALID_EMAIL = "test.user@example.com"
VALID_MESSAGE = "This is a valid test message."


@pytest.fixture
def sample_contact_data() -> dict[str, any]:
    return {
        "full_name": VALID_FULL_NAME,
        "email": VALID_EMAIL,
        "message": VALID_MESSAGE,
    }


def test_create_contact_minimal_valid_data(
    sample_contact_data: dict[str, any]
) -> None:
    """Test creating a Contact instance with minimal valid data."""
    contact = Contact(**sample_contact_data)
    assert isinstance(contact.id, UUID)
    assert contact.full_name == VALID_FULL_NAME
    assert contact.email == VALID_EMAIL
    assert contact.message == VALID_MESSAGE
    assert contact.is_read is False
    assert isinstance(contact.created_at, datetime)
    assert isinstance(contact.updated_at, datetime)
    assert contact.created_at == contact.updated_at
    assert (datetime.now(UTC) - contact.created_at).total_seconds() < 5


def test_create_contact_all_fields_provided() -> None:
    """Test creating a Contact with all fields provided."""
    entity_id = uuid4()
    created_at = datetime.now(UTC) - timedelta(days=1)
    updated_at = datetime.now(UTC) - timedelta(hours=12)
    contact = Contact(
        entity_id=entity_id,
        full_name=VALID_FULL_NAME,
        email=VALID_EMAIL,
        message=VALID_MESSAGE,
        created_at=created_at,
        updated_at=updated_at,
        is_read=True,
    )
    assert contact.id == entity_id
    assert contact.full_name == VALID_FULL_NAME
    assert contact.email == VALID_EMAIL
    assert contact.message == VALID_MESSAGE
    assert contact.is_read is True
    assert contact.created_at == created_at
    assert contact.updated_at == updated_at


@pytest.mark.parametrize(
    "field, value, error_message",
    [
        ("full_name", "", "El nombre no puede estar vacío"),
        ("full_name", "   ", "El nombre no puede estar vacío"),
        ("email", "", "Email inválido"),
        ("email", "invalidemail", "Email inválido"),
        ("message", "", "El mensaje no puede estar vacío"),
        ("message", "   ", "El mensaje no puede estar vacío"),
    ],
)
def test_create_contact_init_value_errors(
    sample_contact_data: dict[str, any],
    field: str,
    value: str,
    error_message: str,
) -> None:
    """Test __init__ raises ValueError for invalid initial field values."""
    invalid_data = sample_contact_data.copy()
    invalid_data[field] = value
    with pytest.raises(ValueError, match=error_message):
        Contact(**invalid_data)


@pytest.mark.parametrize(
    "field, value, error_key, error_detail",
    [
        (
            "full_name",
            "",
            "full_name",
            "El nombre es requerido y no puede estar vacío",
        ),
        (
            "email",
            "invalid",
            "email",
            "El email debe tener un formato válido",
        ),
        (
            "message",
            "",
            "message",
            "El mensaje es requerido y no puede estar vacío",
        ),
    ],
)
def test_contact_structural_validation_errors(
    sample_contact_data: dict[str, any],
    field: str,
    value: str,
    error_key: str,
    error_detail: str,
) -> None:
    """Test Contact validate() raises StructuralValidationError for specific fields."""
    data = sample_contact_data.copy()
    # Bypass __init__ direct checks to test validate() specifically
    contact = Contact(**data)  # Create a valid one first
    setattr(contact, field, value) # Then make it invalid
    with pytest.raises(StructuralValidationError) as excinfo:
        contact.validate()
    assert error_key in excinfo.value.errors
    assert excinfo.value.errors[error_key] == error_detail


def test_contact_business_validation_message_too_long(
    sample_contact_data: dict[str, any]
) -> None:
    """Test ValidationError for message exceeding 1000 characters."""
    data = sample_contact_data.copy()
    data["message"] = "a" * 1001
    # Bypass __init__ direct checks to test validate() specifically
    contact = Contact(**sample_contact_data) # Create a valid one first
    contact.message = data["message"]
    with pytest.raises(ValidationError) as excinfo:
        contact.validate()
    assert "message" in excinfo.value.errors
    error_msg = "El mensaje no puede exceder los 1000 caracteres"
    assert excinfo.value.errors["message"] == error_msg


def test_contact_business_validation_email_domain_test(
    sample_contact_data: dict[str, any]
) -> None:
    """Test ValidationError for email ending with .test."""
    data = sample_contact_data.copy()
    data["email"] = "user@example.test"
    # Bypass __init__ direct checks to test validate() specifically
    contact = Contact(**sample_contact_data) # Create a valid one first
    contact.email = data["email"]
    with pytest.raises(ValidationError) as excinfo:
        contact.validate()
    assert "email" in excinfo.value.errors
    assert excinfo.value.errors["email"] == "No se permiten emails de prueba"


def test_update_message(
    sample_contact_data: dict[str, any]
) -> None:
    """Test updating the message of a Contact."""
    contact = Contact(**sample_contact_data)
    original_updated_at = contact.updated_at
    new_message = "This is an updated message."

    contact.update_message(new_message)
    assert contact.message == new_message
    time.sleep(0.001) # Allow time for timestamp to change
    assert contact.updated_at > original_updated_at

    with pytest.raises(ValueError, match="El mensaje no puede estar vacío"):
        contact.update_message("   ")


def test_update_contact_info(
    sample_contact_data: dict[str, any]
) -> None:
    """Test updating contact info (name and email)."""
    contact = Contact(**sample_contact_data)
    original_updated_at = contact.updated_at

    new_name = "New Name"
    contact.update_contact_info(name=new_name)
    assert contact.full_name == new_name
    assert contact.email == VALID_EMAIL  # Email should be unchanged
    time.sleep(0.001) # Allow time for timestamp to change
    assert contact.updated_at > original_updated_at

    prev_updated_at = contact.updated_at
    new_email = "new.email@example.com"
    contact.update_contact_info(email=new_email)
    assert contact.full_name == new_name # Name should be unchanged
    assert contact.email == new_email
    time.sleep(0.001) # Allow time for timestamp to change
    assert contact.updated_at > prev_updated_at

    prev_updated_at = contact.updated_at
    updated_name = "Another Name"
    updated_email = "another.email@example.com"
    contact.update_contact_info(name=updated_name, email=updated_email)
    assert contact.full_name == updated_name
    assert contact.email == updated_email
    time.sleep(0.001) # Allow time for timestamp to change
    assert contact.updated_at > prev_updated_at

    with pytest.raises(ValueError, match="El nombre no puede estar vacío"):
        contact.update_contact_info(name="  ")
    with pytest.raises(ValueError, match="Email inválido"):
        contact.update_contact_info(email="invalid")


def test_mark_as_read_and_unread(
    sample_contact_data: dict[str, any]
) -> None:
    """Test marking a contact as read and unread."""
    contact = Contact(**sample_contact_data)
    assert contact.is_read is False
    original_updated_at = contact.updated_at

    contact.mark_as_read()
    assert contact.is_read is True
    time.sleep(0.001) # Allow time for timestamp to change
    assert contact.updated_at > original_updated_at

    # Calling again should not change updated_at if state doesn't change
    last_updated_at = contact.updated_at
    contact.mark_as_read()
    assert contact.updated_at == last_updated_at

    contact.mark_as_unread()
    assert contact.is_read is False
    time.sleep(0.001) # Allow time for timestamp to change
    assert contact.updated_at > last_updated_at

    # Calling again should not change updated_at
    final_updated_at = contact.updated_at
    contact.mark_as_unread()
    assert contact.updated_at == final_updated_at


def test_timestamps_default_and_update(
    sample_contact_data: dict[str, any]
) -> None:
    """Test created_at and updated_at default and update correctly."""
    contact = Contact(**sample_contact_data)
    assert isinstance(contact.created_at, datetime)
    assert isinstance(contact.updated_at, datetime)
    assert contact.created_at.tzinfo == UTC
    assert contact.updated_at.tzinfo == UTC
    assert (datetime.now(UTC) - contact.created_at).total_seconds() < 2
    initial_updated_at = contact.updated_at

    # Any action that should update timestamp
    contact.update_message("New message for timestamp test")
    time.sleep(0.001) # Allow time for timestamp to change
    assert contact.updated_at > initial_updated_at
