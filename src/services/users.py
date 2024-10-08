import datetime

from dataclasses import dataclass
from functools import lru_cache
from http import HTTPStatus

from jose import jwt
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import check_password_hash

from db.postgres import get_session
from models.entity import User

from core.config import settings

from models.refresh_token import RefreshToken


@dataclass
class UserService:
    session: AsyncSession

    async def check_user(self, user_data) -> dict:
        result = await self.session.execute(
            select(User).filter_by(
                login=user_data.login
            )
        )
        user = result.scalars().first()

        if check_password_hash(user.password, user_data.password):
            access_token = self._get_token(
                user.login,
                settings.access_token_lifetime
            )
            refresh_token = self._get_token(
                user.login,
                settings.refresh_token_lifetime
            )

            await self.save_refresh_token(refresh_token, user)

            return {
                'token': access_token,
                'refresh_token': refresh_token,
                'status': HTTPStatus.OK
            }

        return {'status': HTTPStatus.UNAUTHORIZED}

    async def save_refresh_token(self, token: str, user) -> None:
        refresh_token = RefreshToken(
            token=token,
            user_id=user.id,
            expires_at=(datetime.datetime.now()
                        + datetime.timedelta(
                        minutes=settings.refresh_token_lifetime
                        )))
        self.session.add(refresh_token)

        await self.session.commit()

    @staticmethod
    def _get_token(login, lifetime):
        expire = datetime.datetime.now() + datetime.timedelta(
            minutes=lifetime
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
        session: AsyncSession = Depends(get_session)
) -> UserService:
    return UserService(session)
