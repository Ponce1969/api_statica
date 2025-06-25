from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class ContactBase(BaseModel):
    full_name: str
    email: EmailStr
    message: str
    is_read: bool = False

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID

class ContactUpdate(ContactBase):
    full_name: str | None = None
    email: EmailStr | None = None
    message: str | None = None
    is_read: bool | None = None

class ContactList(BaseModel):
    contacts: list[ContactResponse]
