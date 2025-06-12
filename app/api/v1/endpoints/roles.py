from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from app.services.role_service import RoleService
from app.core.deps import get_role_service
from app.schemas.role import RoleResponse, RoleCreate, RoleList

router = APIRouter()

@router.post("/", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    service: RoleService = Depends(get_role_service)
):
    return await service.create_role(role)

@router.get("/", response_model=list[RoleResponse])
async def list_roles(
    service: RoleService = Depends(get_role_service)
):
    return await service.list_roles()

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(role_id: UUID, role_service: RoleService = Depends(get_role_service)):
    try:
        role = await role_service.get_role(role_id)
        return role
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
