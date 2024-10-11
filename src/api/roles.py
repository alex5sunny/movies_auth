from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres import get_session
from models.role import Role

router = APIRouter()


class RoleCreate(BaseModel):
    name: str


class RoleInDB(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


@router.post("/roles/", response_model=RoleInDB, status_code=HTTPStatus.CREATED)
async def create_role(role: RoleCreate, db: AsyncSession = Depends(get_session)):
    existing_role = await db.execute(select(Role).where(Role.name == role.name))
    if existing_role.scalar_one_or_none():
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Role with this name already exists."
        )

    new_role = Role(name=role.name)
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return new_role


@router.get("/roles/", response_model=list[RoleInDB])
async def get_roles(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return roles
