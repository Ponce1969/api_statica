"""Endpoints para solicitudes de contacto."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.deps import get_contact_request_service
from app.schemas.contact_request import ContactRequestCreate, ContactRequestResponse
from app.services.contact_request_service import ContactRequestService

router = APIRouter()


@router.post(
    "/",
    response_model=ContactRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact_request(
    payload: ContactRequestCreate,
    service: Annotated[ContactRequestService, Depends(get_contact_request_service)],  # noqa: B008
) -> ContactRequestResponse:
    obj = await service.create_request(payload)
    return ContactRequestResponse(
        id=str(obj.id),
        full_name=obj.full_name,
        email=obj.email,
        message=obj.message,
    )
