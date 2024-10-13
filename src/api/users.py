from datetime import datetime
from http import HTTPStatus
from typing import Optional, Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.user import User

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
        from_attributes = True


class UserLogin(BaseModel):
    login: str
    password: str


class UserSignin(BaseModel):
    login_at: datetime
    signin_data: str


class Token(BaseModel):
    token: Optional[str]


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
) -> ORJSONResponse:
    response = await service.check_user(user_login)
    return response


@router.get(
    path='/signin_history', response_model=list[UserSignin]
)
async def signin_history(
        login: str,
        page_number: Annotated[int, Query(title="Page number", ge=1)] = 1,
        page_size: Annotated[int, Query(title="Page size", ge=2, le=100)] = 50,
        service: UserService = Depends(get_user_service)
) -> Any:
    response = await service.login_history(login, page_number, page_size)
    return [UserSignin(
                login_at=user_login.login_at,
                signin_data=user_login.signin_data
            )  for user_login in response]


@router.post(
    path='/check_token'
)
async def check_token(
        token: Token,
        service: UserService = Depends(get_user_service)
) -> ORJSONResponse:
    response = await service.decode_access_token(token.token)

    return response


@router.post(
    path='/refresh',
)
async def refresh_token(
        token: Token,
        service: UserService = Depends(get_user_service)):
    response = await service.decode_refresh_token(token.token)

    return response


@router.post(path='/logout')
async def logout(
        token: Token,
        service: UserService = Depends(get_user_service)
) -> ORJSONResponse:
    response = await service.logout(token.token)

    return response
