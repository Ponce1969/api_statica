# Placeholder for User domain model tests
import time
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.exceptions.base import StructuralValidationError
from app.domain.models.user import User

# Test data
VALID_EMAIL = "test.user@example.com"
VALID_FULL_NAME = "Test User Name"

def test_create_valid_user_instance() -> None:
    """Test creating a User instance with valid minimal data."""
    user_id = uuid4()
    created_time = datetime.now(UTC)
    
    user = User(
        entity_id=user_id,
        email=VALID_EMAIL,
        full_name=VALID_FULL_NAME,
        created_at=created_time,
        updated_at=created_time
    )
    
    assert user.id == user_id
    assert user.email == VALID_EMAIL
    assert user.full_name == VALID_FULL_NAME
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.role_ids == set()
    assert user.created_at == created_time
    assert user.updated_at == created_time

def test_create_user_with_all_fields() -> None:
    """Test creating a User instance with all optional fields provided."""
    user_id = uuid4()
    role_id_1 = uuid4()
    role_id_2 = uuid4()
    
    user = User(
        entity_id=user_id,
        email="superuser@example.com",
        full_name="Super User",
        is_active=False,
        is_superuser=True,
        role_ids={role_id_1, role_id_2}
    )
    
    assert user.id == user_id
    assert user.email == "superuser@example.com"
    assert user.full_name == "Super User"
    assert user.is_active is False
    assert user.is_superuser is True
    assert user.role_ids == {role_id_1, role_id_2}

def test_create_user_invalid_email_empty() -> None:
    """Test creating a User with an empty email raises StructuralValidationError."""
    with pytest.raises(StructuralValidationError) as excinfo:
        User(email="", full_name=VALID_FULL_NAME)
    assert "email" in excinfo.value.errors
    assert (
        excinfo.value.errors["email"] == "El email es requerido y debe ser válido"
    )

def test_create_user_invalid_email_format() -> None:
    """Test creating a User with an invalid email format raises StructuralValidationError."""
    with pytest.raises(StructuralValidationError) as excinfo:
        User(email="invalidemail", full_name=VALID_FULL_NAME)
    assert "email" in excinfo.value.errors
    assert (
        excinfo.value.errors["email"] == "El email es requerido y debe ser válido"
    )

def test_create_user_invalid_full_name_empty() -> None:
    """Test creating a User with an empty full_name raises StructuralValidationError."""
    with pytest.raises(StructuralValidationError) as excinfo:
        User(email=VALID_EMAIL, full_name="")
    assert "full_name" in excinfo.value.errors
    assert (
        excinfo.value.errors["full_name"]
        == "El nombre completo no puede estar vacío"
    )

def test_create_user_invalid_full_name_whitespace() -> None:
    """Test creating a User with a whitespace full_name raises StructuralValidationError."""
    with pytest.raises(StructuralValidationError) as excinfo:
        User(email=VALID_EMAIL, full_name="   ")
    assert "full_name" in excinfo.value.errors
    assert (
        excinfo.value.errors["full_name"]
        == "El nombre completo no puede estar vacío"
    )

def test_assign_and_remove_role() -> None:
    """Test assigning and removing roles."""
    user = User(email=VALID_EMAIL, full_name=VALID_FULL_NAME)
    role_id = uuid4()
    
    assert not user.has_role(role_id)
    
    user.assign_role(role_id)
    assert user.has_role(role_id)
    assert role_id in user.role_ids
    
    user.remove_role(role_id)
    assert not user.has_role(role_id)
    assert role_id not in user.role_ids

def test_deactivate_and_activate_user() -> None:
    """Test deactivating and activating a user."""
    user = User(email=VALID_EMAIL, full_name=VALID_FULL_NAME)
    initial_updated_at = user.updated_at
    
    assert user.is_active is True
    
    user.deactivate()
    assert user.is_active is False
    time.sleep(0.001)  # Allow time for timestamp to change
    assert user.updated_at > initial_updated_at
    
    last_updated_at = user.updated_at
    user.activate()
    assert user.is_active is True
    time.sleep(0.001)  # Allow time for timestamp to change
    assert user.updated_at > last_updated_at

def test_update_email_valid() -> None:
    """Test updating email with a valid new email."""
    user = User(email=VALID_EMAIL, full_name=VALID_FULL_NAME)
    new_email = "new.valid.email@example.com"
    initial_updated_at = user.updated_at
    
    user.update_email(new_email)
    assert user.email == new_email
    time.sleep(0.001)  # Allow time for timestamp to change
    assert user.updated_at > initial_updated_at

@pytest.mark.parametrize(
    "invalid_email", ["", "plainaddress", " ", "test@.com"]
)
def test_update_email_invalid(invalid_email: str) -> None:
    """Test updating email with invalid emails raises StructuralValidationError."""
    user = User(email=VALID_EMAIL, full_name=VALID_FULL_NAME)
    with pytest.raises(StructuralValidationError) as excinfo:
        user.update_email(invalid_email)
    assert "email" in excinfo.value.errors
    assert excinfo.value.errors["email"] == "Debe ser un email válido con formato correcto (ej: usuario@dominio.com)"

def test_update_full_name_valid() -> None:
    """Test updating full_name with a valid new name."""
    user = User(email=VALID_EMAIL, full_name=VALID_FULL_NAME)
    new_full_name = "New Valid Full Name"
    initial_updated_at = user.updated_at
    
    user.update_full_name(new_full_name)
    assert user.full_name == new_full_name
    time.sleep(0.001)  # Allow time for timestamp to change
    assert user.updated_at > initial_updated_at

@pytest.mark.parametrize(
    "invalid_name", ["", "   "]
)
def test_update_full_name_invalid(invalid_name: str) -> None:
    """Test updating full_name with invalid names raises StructuralValidationError."""
    user = User(email=VALID_EMAIL, full_name=VALID_FULL_NAME)
    with pytest.raises(StructuralValidationError) as excinfo:
        user.update_full_name(invalid_name)
    assert "full_name" in excinfo.value.errors
    assert excinfo.value.errors["full_name"] == "No puede estar vacío"
