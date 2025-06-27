from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_serializer


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v is not None else None
        }
    )
    id: UUID
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime | None = None
    
    # Asegurar que las fechas sean timezone-aware
    @field_serializer('created_at', 'updated_at')
    def serialize_dt(self, dt: datetime | None, _info) -> str | None:
        if dt is None:
            return None
        if dt.tzinfo is None:
            # Si la fecha no tiene zona horaria, asumir UTC
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None
