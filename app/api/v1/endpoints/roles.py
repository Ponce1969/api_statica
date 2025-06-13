from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_role_service
from app.schemas.role import RoleCreate, RoleResponse
from app.services.role_service import RoleService

router = APIRouter()

@router.post("/", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    service: RoleService = None,
) -> RoleResponse:
    if service is None:
        service = get_role_service()
    return await service.create_role(role)

from typing import Optional
from fastapi import Query

@router.get("/", response_model=list[RoleResponse])
async def list_roles(
    name: Optional[str] = Query(
        None,
        description="Filtrar roles por nombre exacto",
        example="admin"
    ),
    service: RoleService = Depends(get_role_service),
) -> list[RoleResponse]:
    return await service.list_roles(name=name)

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    role_service: RoleService = None,
) -> RoleResponse:
    if role_service is None:
        role_service = get_role_service()
    try:
        role = await role_service.get_role(role_id)
        return role
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
