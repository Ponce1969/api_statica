"""Schemas Pydantic para ContactRequest."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class ContactRequestCreate(BaseModel):
    """Datos entrantes desde el formulario del frontend."""

    full_name: str = Field(..., max_length=150, examples=["Juan Pérez"])
    email: EmailStr = Field(..., examples=["juan@example.com"])
    phone: str | None = Field(None, max_length=30, examples=["+54 11 5555-5555"])
    message: str = Field(..., max_length=1000, examples=["Hola, tengo una consulta..."])


class ContactRequestResponse(BaseModel):
    """Respuesta devuelta al frontend."""

    id: str
    full_name: str
    email: EmailStr
    message: str

    class Config:
        orm_mode = True
