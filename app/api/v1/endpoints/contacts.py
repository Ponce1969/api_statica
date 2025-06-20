from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import get_contact_service
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import ContactService

router = APIRouter()

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact: ContactCreate,
    service: ContactService = Depends(get_contact_service),  # noqa: B008
) -> ContactResponse:
    return await service.create_contact(contact)

@router.get("/", response_model=list[ContactResponse])
async def list_contacts(
    email: str | None = Query(
        None,
        description="Filtrar contactos por email exacto",
        example="ejemplo@correo.com"
    ),
    is_read: bool | None = Query(
        None,
        description="Filtrar por estado leído (True o False)",
        example=True
    ),
    service: ContactService = Depends(get_contact_service),  # noqa: B008
) -> list[ContactResponse]:
    return await service.get_contacts(email=email, is_read=is_read)

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    service: ContactService = Depends(get_contact_service),  # noqa: B008
) -> ContactResponse:
    try:
        contact = await service.get_contact(contact_id)
        # Convertir el modelo de dominio a esquema de respuesta
        return ContactResponse(
            id=contact.id,
            email=contact.email,
            message=contact.message,
            full_name=contact.full_name,
            is_read=contact.is_read
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
