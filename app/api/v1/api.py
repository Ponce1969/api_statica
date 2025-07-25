from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    contact_requests,
    contacts,
    roles,
    users,
)

api_router = APIRouter()
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    contact_requests.router, prefix="/contact-requests", tags=["contact_requests"]
)
