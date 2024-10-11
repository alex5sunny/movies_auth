from http import HTTPStatus
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from services.roles import RoleService, get_role_service

router = APIRouter()

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class RoleInDB(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


@router.post("/roles/", response_model=RoleInDB, status_code=HTTPStatus.CREATED)
async def create_role(
    role: RoleCreate,
    role_service: RoleService = Depends(get_role_service)
):
    try:
        new_role = await role_service.create_role(name=role.name, description=role.description)
        return new_role
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/roles/", response_model=list[RoleInDB])
async def get_roles(
    role_service: RoleService = Depends(get_role_service)
):
    roles = await role_service.get_roles()
    return roles


@router.get("/roles/{role_id}", response_model=RoleInDB)
async def get_role(
    role_id: int,
    role_service: RoleService = Depends(get_role_service)
):
    role = await role_service.get_role(role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Role not found."
        )
    return role


@router.put("/roles/{role_id}", response_model=RoleInDB)
async def update_role(
    role_id: int,
    role: RoleCreate,
    role_service: RoleService = Depends(get_role_service)
):
    updated_role = await role_service.update_role(role_id=role_id, name=role.name, description=role.description)
    if not updated_role:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Role not found."
        )
    return updated_role


@router.delete("/roles/{role_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_role(
    role_id: int,
    role_service: RoleService = Depends(get_role_service)
):
    deleted = await role_service.delete_role(role_id=role_id)
    if not deleted:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Role not found."
        )
