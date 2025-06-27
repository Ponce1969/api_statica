from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer
from datetime import timezone


class ContactBase(BaseModel):
    full_name: str
    email: EmailStr
    message: str
    is_read: bool = False

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v is not None else None
        }
    )
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Asegurar que las fechas sean timezone-aware
    @field_serializer('created_at', 'updated_at')
    def serialize_dt(self, dt: Optional[datetime], _info) -> Optional[str]:
        if dt is None:
            return None
        if dt.tzinfo is None:
            # Si la fecha no tiene zona horaria, asumir UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

class ContactUpdate(ContactBase):
    full_name: str | None = None
    email: EmailStr | None = None
    message: str | None = None
    is_read: bool | None = None

class ContactList(BaseModel):
    contacts: list[ContactResponse]
