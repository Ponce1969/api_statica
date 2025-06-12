from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: UUID

class RoleList(BaseModel):
    roles: list[RoleResponse]
