from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
