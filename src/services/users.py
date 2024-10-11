import datetime
import logging

from dataclasses import dataclass
from functools import lru_cache
from http import HTTPStatus

from fastapi.responses import ORJSONResponse
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash

from db.Cache import Cache
from db.postgres import get_session
from db.redis.RedisCache import RedisCache
from models.entity import User

from core.config import settings

from models.refresh_token import RefreshToken


@dataclass
class UserService:
    pg_session: AsyncSession
    redis: Cache

    async def check_user(self, user_data) -> ORJSONResponse:
        result = await self.pg_session.execute(
            select(User).filter_by(
                login=user_data.login
            )
        )
        user = None
        if result:
            user = result.scalars().first()

        if user and check_password_hash(
                user.password,
                user_data.password
        ):
            access_token = self._get_token(
                user.login,
                settings.access_token_lifetime
            )
            refresh_token = self._get_token(
                user.login,
                settings.refresh_token_lifetime
            )

            await self.save_refresh_token(refresh_token, user)

            return ORJSONResponse({
                'token': access_token,
                'refresh_token': refresh_token,
            }, HTTPStatus.OK)

        return ORJSONResponse(
            {'message': 'Invalid login or password!'},
            HTTPStatus.UNAUTHORIZED
        )

    async def save_refresh_token(self, token: str, user) -> None:
        refresh_token = RefreshToken(
            token=token,
            user_id=user.id,
            expires_at=(datetime.datetime.now()
                        + datetime.timedelta(
                        minutes=settings.refresh_token_lifetime
                    )))
        self.pg_session.add(refresh_token)

    async def logout(self, token: str) -> ORJSONResponse:
        try:
            await self.redis.put(f'token:{token}', token, settings.access_token_lifetime)
            return ORJSONResponse({'logout': 'Successfully!'}, status_code=HTTPStatus.OK)
        except Exception as e:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    async def decode_jwt(self, token: str) -> ORJSONResponse:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
            expire = datetime.datetime.strptime(payload.get('expire'), "%Y-%m-%d %H:%M:%S.%f")
            token_in_storage = await self.redis.get(f'token:{token}')

            if datetime.datetime.now() > expire or token_in_storage:
                logging.debug(
                    f'TOKEN EXPIRED: current time: {datetime.datetime.now()},'
                    f' expired: {expire}, logout: {token_in_storage is None}'
                )
                return ORJSONResponse({'data': 'token expired!'}, HTTPStatus.UNAUTHORIZED)

            return ORJSONResponse({'user': payload.get('user')}, HTTPStatus.OK)

        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

    @staticmethod
    def _get_token(login, lifetime):
        expire = datetime.datetime.now() + datetime.timedelta(
            seconds=lifetime
        )
        data = {'user': login, 'expire': str(expire)}

        token = jwt.encode(
            data,
            settings.secret_key,
            settings.algorithm
        )

        return token


@lru_cache()
def get_user_service(
        pg_session: AsyncSession = Depends(get_session),
        redis: RedisCache = Depends(RedisCache)
) -> UserService:
    return UserService(pg_session, redis)