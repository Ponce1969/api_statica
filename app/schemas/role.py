from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_serializer


class RoleBase(BaseModel):
    name: str
    description: str | None = None

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v is not None else None
        }
    )
    id: UUID
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

class RoleUpdate(RoleBase):
    name: str | None = None
    description: str | None = None

class RoleList(BaseModel):
    roles: list[RoleResponse]
