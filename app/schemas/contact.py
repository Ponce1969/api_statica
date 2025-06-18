from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class ContactBase(BaseModel):
    full_name: str
    email: EmailStr
    message: str | None = None
    is_read: bool | None = False

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID

class ContactList(BaseModel):
    contacts: list[ContactResponse]
