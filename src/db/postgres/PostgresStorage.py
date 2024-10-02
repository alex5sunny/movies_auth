from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)

from core.config import settings
from db.Storage import Storage
from db.postgres.Base import Base


class PostgresStorage(Storage):

    def __init__(self):
        self.dsn = (f'postgresql+asyncpg://'
                    f'{settings.postgres_user}:{settings.postgres_password}@{settings.db_host}:'
                    f'{settings.db_port}/{settings.postgres_db}')
        self.postgres = create_async_engine(self.dsn, echo=True, future=True)
        self.async_session = async_sessionmaker(
            self.postgres,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def __create_schema__(self) -> None:
        async with self.postgres.begin() as session:
            await session.run_sync(Base.metadata.create_all)

    async def __purge_database__(self) -> None:
        async with self.postgres.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def open(self):
        # await self.__create_schema__()
        async with self.async_session() as session:
            yield session

    async def close(self):
        # await self.__purge_database__()
        await self.postgres.dispose()
