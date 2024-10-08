from http import HTTPStatus
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.entity import User

from services.users import get_user_service, UserService

router = APIRouter()


class UserCreate(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    login: str
    password: str

    class Config:
        orm_mode = True


class Token:
    token: Optional[str]
    status: int


@router.post('/signup', response_model=UserInDB, status_code=HTTPStatus.CREATED)
async def create_user(
        user_create: UserCreate, db: AsyncSession = Depends(get_session)
):
    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post(
    path='/signin',
)
async def login_user(
        user_login: UserLogin,
        service: UserService = Depends(get_user_service)
) -> dict:
    response = await service.check_user(user_login)
    return response
