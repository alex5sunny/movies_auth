from http import HTTPStatus
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from services.roles import RoleService, get_role_service
from src.services.decorators import superuser_required

router = APIRouter()


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class RoleInDB(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


@router.post("/roles/", response_model=RoleInDB, status_code=HTTPStatus.CREATED)
@superuser_required
async def create_role(
    role: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
):
    new_role = await role_service.create_role(name=role.name, description=role.description)
    return new_role


@router.get("/roles/", response_model=List[RoleInDB])
async def get_roles(
    role_service: RoleService = Depends(get_role_service),
):
    roles = await role_service.get_roles()
    return roles


@router.get("/roles/{role_id}", response_model=RoleInDB)
async def get_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
):
    role = await role_service.get_role(role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Role not found."
        )
    return role


@router.put("/roles/{role_id}", response_model=RoleInDB)
@superuser_required
async def update_role(
    role_id: UUID,
    role: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
):
    updated_role = await role_service.update_role(role_id=role_id, name=role.name, description=role.description)
    return updated_role


@router.delete("/roles/{role_id}", status_code=HTTPStatus.NO_CONTENT)
@superuser_required
async def delete_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
):
    await role_service.delete_role(role_id=role_id)
