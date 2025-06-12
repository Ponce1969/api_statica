from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional, List

class ContactBase(BaseModel):
    full_name: str
    email: EmailStr
    message: Optional[str] = None
    is_read: Optional[bool] = False

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: UUID

class ContactList(BaseModel):
    contacts: List[ContactResponse]
