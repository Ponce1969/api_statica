"""Schemas Pydantic para ContactRequest."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_serializer
from pydantic import ConfigDict


class ContactRequestCreate(BaseModel):
    """Datos entrantes desde el formulario del frontend."""

    full_name: str = Field(..., max_length=150, json_schema_extra={"examples": ["Juan Pérez"]})
    email: EmailStr = Field(..., json_schema_extra={"examples": ["juan@example.com"]})
    phone: str | None = Field(None, max_length=30, json_schema_extra={"examples": ["+54 11 5555-5555"]})
    message: str = Field(..., max_length=1000, json_schema_extra={"examples": ["Hola, tengo una consulta..."]})


class ContactRequestResponse(BaseModel):
    """Respuesta devuelta al frontend."""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v is not None else None
        }
    )
    
    id: str
    full_name: str
    email: EmailStr
    message: str
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
