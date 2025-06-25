import pytest
from app.core.security.hashing import verify_password, get_password_hash

def test_get_password_hash():
    password = "test_password"
    hashed_password = get_password_hash(password)
    assert isinstance(hashed_password, str)
    assert hashed_password != password # Hashed password should not be the same as plain password
    assert hashed_password.startswith("$argon2id$") # Should start with argon2id prefix

def test_verify_password_correct():
    password = "test_password"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password) is True

def test_verify_password_incorrect():
    password = "test_password"
    wrong_password = "wrong_password"
    hashed_password = get_password_hash(password)
    assert verify_password(wrong_password, hashed_password) is False

def test_verify_password_with_different_hash():
    password = "test_password"
    another_password = "another_password"
    hashed_password = get_password_hash(password)
    another_hashed_password = get_password_hash(another_password)
    assert verify_password(password, another_hashed_password) is False

