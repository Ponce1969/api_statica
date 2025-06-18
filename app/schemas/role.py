from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    name: str
    description: str | None = None

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID

class RoleList(BaseModel):
    roles: list[RoleResponse]
