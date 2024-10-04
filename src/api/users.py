from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

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


# @router.post('/signup', response_model=UserInDB, status_code=HTTPStatus.CREATED)
# async def create_user(user_create: UserCreate, db: AsyncSession = Depends(get_session)) -> UserInDB:
#     user_dto = jsonable_encoder(user_create)
#     user = User(**user_dto)
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)
#     return user

