from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.deps import get_role_service
from app.schemas.role import RoleCreate, RoleResponse
from app.services.role_service import RoleService

router = APIRouter()

@router.post("/", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    service: RoleService = Depends(get_role_service),  # noqa: B008
) -> RoleResponse:
    role_domain = await service.create_role(role)
    # Convertir el modelo de dominio a esquema de respuesta
    return RoleResponse(
        id=role_domain.id,
        name=role_domain.name,
        description=role_domain.description
    )



@router.get("/", response_model=list[RoleResponse])
async def list_roles(
    name: str | None = Query(
        None,
        description="Filtrar roles por nombre exacto",
        example="admin"
    ),
    service: RoleService = Depends(get_role_service),  # noqa: B008
) -> list[RoleResponse]:
    roles = await service.list_roles(name=name)
    # Convertir los modelos de dominio a esquemas de respuesta
    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description
        ) for role in roles
    ]

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),  # noqa: B008
) -> RoleResponse:
    try:
        role = await role_service.get_role(role_id)
        # Convertir el modelo de dominio a esquema de respuesta
        return RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
