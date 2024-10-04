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

    async def create_schema(self) -> None:
        async with self.postgres.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def purge_schema(self) -> None:
        async with self.postgres.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def open(self):
        async with self.async_session() as session:
            yield session

    async def close(self):
        await self.postgres.dispose()
