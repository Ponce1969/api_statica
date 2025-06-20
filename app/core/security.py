"""Security utilities and reusable dependencies for FastAPI auth.

Defines the OAuth2 bearer scheme so that Swagger (OpenAPI) shows the
"Authorize" button. The token URL points to the login endpoint that
returns the JWT token.
"""
from fastapi.security import OAuth2PasswordBearer

# The login route is registered under /api/v1/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")
