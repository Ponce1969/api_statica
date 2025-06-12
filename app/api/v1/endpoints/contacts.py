from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.services.contact_service import ContactService
from app.core.deps import get_contact_service
from app.schemas.contact import ContactResponse, ContactCreate, ContactList

router = APIRouter()

@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact: ContactCreate,
    service: ContactService = Depends(get_contact_service)
):
    return await service.create_contact(contact)

@router.get("/", response_model=list[ContactResponse])
async def list_contacts(
    service: ContactService = Depends(get_contact_service)
):
    return await service.list_contacts()

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: UUID, contact_service: ContactService = Depends(get_contact_service)):
    try:
        contact = await contact_service.get_contact(contact_id)
        return contact
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
