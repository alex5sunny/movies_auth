from core.config import settings
from db.Storage import Storage
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


class PostgresStorage(Storage):

    def __init__(self):
        self.dsn = (f'postgresql+asyncpg://'
                    f'{settings.postgres_user}:{settings.postgres_password}@{settings.db_host}:'
                    f'{settings.db_port}/{settings.postgres_db}')
        self.postgres = create_async_engine(self.dsn, echo=True, future=True)
        self.async_session = sessionmaker(
            self.postgres,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def open(self):
        async with self.async_session() as session:
            yield session

    async def close(self):
        await self.postgres.dispose()
