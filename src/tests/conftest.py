import os
from dotenv import load_dotenv
load_dotenv('configs/.env.test')

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from sqlalchemy import select, text
from alembic.config import Config
from alembic import command
from typing import AsyncGenerator
from core.config import settings
from main import app
from db.postgres import get_session, Base, engine
from models.user import User




print('AMOKRYSHEV!!!: {}'.format(os.environ.get('POSTGRES_USER')))

dsn = (f'postgresql+asyncpg://{settings.postgres_user}:'
       f'{settings.postgres_password}@{settings.db_host}:'
       f'{settings.db_port}/{settings.postgres_db}')
dsn_adm = (f'postgresql+asyncpg://{settings.postgres_user}:'
       f'{settings.postgres_password}@{settings.db_host}:'
       f'{settings.db_port}/postgres')

engine = create_async_engine(dsn, echo=True)
engine_adm = create_async_engine(dsn_adm, echo=True, isolation_level="AUTOCOMMIT")

# fixture for the db engine
@pytest_asyncio.fixture(scope="session")
async def prepare_db():

    async with engine_adm.connect() as conn:
        query = text("SELECT 1 FROM pg_database WHERE datname = :db_name")
        result = await conn.execute(query, {'db_name': settings.postgres_db})
        exists = result.fetchall()
        if not exists:
            await conn.execute(text(f"CREATE DATABASE {settings.postgres_db}"))

    #async with engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.create_all)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option('sqlalchemy.url', dsn_adm)
    command.upgrade(alembic_cfg, "head")

    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# fixture for the db session
@pytest_asyncio.fixture(scope="function")
async def db_session(prepare_db) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(engine)
    try:
        yield async_session
    finally:
        await async_session.close()

# fixture for the FastAPI test client
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()

# fixture to create a superuser and get token
@pytest_asyncio.fixture(scope="function")
async def superuser_token(client: AsyncClient, db_session: AsyncSession):
    await client.post(
        "/signup",
        json={
            "login": "adminuser",
            "password": "adminpassword",
            "first_name": "Admin",
            "last_name": "User",
        }
    )

    result = await db_session.execute(
        select(User).filter_by(login="adminuser")
    )
    admin_user = result.scalars().first()
    admin_user.is_superuser = True
    await db_session.commit()

    response = await client.post(
        "/signin",
        json={
            "login": "adminuser",
            "password": "adminpassword"
        }
    )
    token = response.json()["token"]
    return token

# fixture to create a regular user and get token
@pytest_asyncio.fixture(scope="function")
async def regular_user_token(client: AsyncClient):
    await client.post(
        "/signup",
        json={
            "login": "regularuser",
            "password": "regularpassword",
            "first_name": "Regular",
            "last_name": "User"
        }
    )
    response = await client.post(
        "/signin",
        json={
            "login": "regularuser",
            "password": "regularpassword"
        }
    )
    token = response.json()["token"]
    return token
