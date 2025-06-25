import pytest
from pydantic import ValidationError
from app.domain.value_objects.email import Email

def test_valid_email_creation():
    email_str = "test@example.com"
    email_obj = Email(email_str)
    assert email_obj.email == email_str

def test_invalid_email_creation():
    invalid_email_str = "invalid-email"
    with pytest.raises(ValueError, match="Invalid email format"):
        Email(invalid_email_str)

def test_email_str_representation():
    email_str = "another@example.com"
    email_obj = Email(email_str)
    assert str(email_obj) == email_str

def test_email_equality():
    email1 = Email("test@example.com")
    email2 = Email("test@example.com")
    email3 = Email("different@example.com")
    assert email1 == email2
    assert email1 != email3

def test_email_hashability():
    email1 = Email("test@example.com")
    email2 = Email("test@example.com")
    email_set = {email1}
    assert email2 in email_set

def test_email_case_insensitivity_pydantic_behavior():
    # Pydantic's EmailStr normalizes to lowercase, so this test reflects that behavior
    email_obj = Email("Test@Example.com")
    assert email_obj.email == "test@example.com"
