from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from sqlalchemy.orm import declarative_base

from core.config import settings

Base = declarative_base()

dsn = (f'postgresql+asyncpg://{settings.postgres_user}:'
       f'{settings.postgres_password}@{settings.db_host}:'
       f'{settings.db_port}/{settings.postgres_db}')
engine = create_async_engine(dsn, echo=True, future=True)
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
