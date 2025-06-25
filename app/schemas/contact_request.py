"""Schemas Pydantic para ContactRequest."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict


class ContactRequestCreate(BaseModel):
    """Datos entrantes desde el formulario del frontend."""

    full_name: str = Field(..., max_length=150, json_schema_extra={"examples": ["Juan Pérez"]})
    email: EmailStr = Field(..., json_schema_extra={"examples": ["juan@example.com"]})
    phone: str | None = Field(None, max_length=30, json_schema_extra={"examples": ["+54 11 5555-5555"]})
    message: str = Field(..., max_length=1000, json_schema_extra={"examples": ["Hola, tengo una consulta..."]})


class ContactRequestResponse(BaseModel):
    """Respuesta devuelta al frontend."""

    id: str
    full_name: str
    email: EmailStr
    message: str

    model_config = ConfigDict(from_attributes=True)
