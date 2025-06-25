import pytest
from datetime import UTC, datetime, timedelta
from app.core.security.jwt import create_access_token, decode_access_token, ALGORITHM
from app.core.config import settings
from jose import jwt

# Mock settings for testing purposes if needed, though direct import is fine for unit tests
# settings.SECRET_KEY = "supersecretkey"
# settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30

def test_create_access_token_default_expiry():
    data = {"sub": "test@example.com", "user_id": "123"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0

    decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["sub"] == data["sub"]
    assert decoded_data["user_id"] == data["user_id"]
    assert "exp" in decoded_data

    # Check if expiry is roughly within expected range (e.g., 1 minute tolerance)
    expected_expiry = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    assert decoded_data["exp"] <= int(expected_expiry.timestamp() + 60) # Add a buffer for execution time
    assert decoded_data["exp"] >= int(expected_expiry.timestamp() - 60)

def test_create_access_token_custom_expiry():
    data = {"sub": "custom@example.com"}
    custom_delta = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=custom_delta)

    decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_data["sub"] == data["sub"]
    
    expected_expiry = datetime.now(UTC) + custom_delta
    assert decoded_data["exp"] <= int(expected_expiry.timestamp() + 60)
    assert decoded_data["exp"] >= int(expected_expiry.timestamp() - 60)

def test_create_access_token_missing_sub():
    data = {"user_id": "123"} # Missing 'sub'
    with pytest.raises(ValueError, match="El token debe incluir un 'sub' válido como string no vacío"):
        create_access_token(data)

def test_create_access_token_empty_sub():
    data = {"sub": "", "user_id": "123"} # Empty 'sub'
    with pytest.raises(ValueError, match="El token debe incluir un 'sub' válido como string no vacío"):
        create_access_token(data)

def test_decode_access_token_valid():
    data = {"sub": "decode@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=1))
    decoded_data = decode_access_token(token)
    assert decoded_data is not None
    assert decoded_data["sub"] == data["sub"]

def test_decode_access_token_expired():
    data = {"sub": "expired@example.com"}
    # Create a token that expires immediately
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    # Wait a moment to ensure it's expired
    import time
    time.sleep(1)
    decoded_data = decode_access_token(token)
    assert decoded_data is None

def test_decode_access_token_invalid_signature():
    data = {"sub": "invalid@example.com"}
    token = create_access_token(data)
    # Tamper with the token to invalidate signature
    tampered_token = token + "abc"
    decoded_data = decode_access_token(tampered_token)
    assert decoded_data is None

def test_decode_access_token_wrong_secret_key():
    original_secret_key = settings.SECRET_KEY
    settings.SECRET_KEY = "wrongsecretkey"
    data = {"sub": "wrongkey@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=1))
    settings.SECRET_KEY = original_secret_key # Restore original key
    decoded_data = decode_access_token(token)
    assert decoded_data is None

def test_decode_access_token_wrong_algorithm():
    data = {"sub": "wrongalgo@example.com"}
    token = jwt.encode(data, settings.SECRET_KEY, algorithm="HS512") # Encode with a different algorithm than ALGORITHM (which is HS256)
    decoded_data = decode_access_token(token)
    assert decoded_data is None
