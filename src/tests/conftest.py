import os
#слегка проверим что pytest запущен из папочки src и сгенерируем понятный текст исключения если это не так
if not os.path.isfile(os.path.join(os.getcwd(), 'main.py')):
    raise Exception("The file main.py doesnt exits in the context, go to the folder \"src\" before start pytest")

from dotenv import load_dotenv
load_dotenv('../configs/.env.test')

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, async_sessionmaker
)
from sqlalchemy import select, text
from alembic.config import Config
from alembic import command
from typing import AsyncGenerator
from werkzeug.security import generate_password_hash
from core.config import settings
from main import app

TEST_ADM_LOGIN = 'adminuser'
TEST_ADM_PASS = 'adminpassword'
TEST_USR_LOGIN = 'regularuser'
TEST_USR_PASS = 'regularpassword'


#Специально отказались от engine из db.postgres, строка подключения все равно зависит от environment,
# а код так гораздо понятнее.
dsn = (f'postgresql+asyncpg://{settings.postgres_user}:'
       f'{settings.postgres_password}@{settings.db_host}:'
       f'{settings.db_port}/{settings.postgres_db}')
dsn_adm = (f'postgresql+asyncpg://{settings.postgres_user}:'
       f'{settings.postgres_password}@{settings.db_host}:'
       f'{settings.db_port}/postgres')

engine = create_async_engine(dsn, echo=True, future=True)
engine_adm = create_async_engine(dsn_adm, echo=True, isolation_level="AUTOCOMMIT", future=True)

# fixture for the database preparation
@pytest_asyncio.fixture(scope="session")
async def prepare_db():
    async with engine_adm.connect() as conn:
        query = text("SELECT 1 FROM pg_database WHERE datname = :db_name")
        result = await conn.execute(query, {'db_name': settings.postgres_db})
        exists = result.fetchall()
        if not exists:
            # Не защищено от SQL-инъекций, но механизм sqlalchemy.text не позволяет делать такие запросы,
            # а риск практически нулевой, за то код простой и понятный
            await conn.execute(text(f"CREATE DATABASE {settings.postgres_db}"))

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option('sqlalchemy.url', dsn)
        command.upgrade(alembic_cfg, "head")

    async with engine.begin() as conn:
        query = text("INSERT INTO public.users(id, login, password, first_name, last_name, created_at, is_superuser)\n"
                     "VALUES (gen_random_uuid(), :adm_login, :adm_pass, 'Admin', 'User', NOW(), true),\n"
                     "(gen_random_uuid(), :reg_login, :reg_pass, 'Admin', 'User', NOW(), false)")
        await conn.execute(query, {
            'adm_login': TEST_ADM_LOGIN,
            'adm_pass': generate_password_hash(TEST_ADM_PASS),
            'reg_login': TEST_USR_LOGIN,
            'reg_pass': generate_password_hash(TEST_USR_PASS),
        })

    yield engine

    async with engine_adm.connect() as conn:
        query = text("SELECT 1 FROM pg_database WHERE datname = :db_name")
        result = await conn.execute(query, {'db_name': settings.postgres_db})
        exists = result.fetchall()
        if exists:
            query = text("SELECT pg_terminate_backend(pg_stat_activity.pid)\n"
                         "FROM pg_stat_activity\n"
                         "WHERE pg_stat_activity.datname = :db_name AND pid <> pg_backend_pid();\n")
            await conn.execute(query, {'db_name': settings.postgres_db})

            # Не защищено от SQL-инъекций, но механизм sqlalchemy.text не позволяет делать такие запросы,
            # а риск практически нулевой, за то код простой и понятный
            await conn.execute(text(f"DROP DATABASE {settings.postgres_db}"))


# fixture for the FastAPI test client
@pytest_asyncio.fixture(scope="session")
async def client(prepare_db) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

# fixture to create a superuser and get token
@pytest_asyncio.fixture(scope="function")
async def superuser_token(prepare_db,  client):
    response = await client.post(
        "/api/users/signin",
        json={
            "login": TEST_ADM_LOGIN,
            "password": TEST_ADM_PASS
        }
    )

    print("!!!AMO: {}".format(response.json()))
    token = response.json()["token"]
    return token

# fixture to create a regular user and get token
@pytest_asyncio.fixture(scope="function")
async def regular_user_token(prepare_db,  client):
    response = await client.post(
        "/api/users/signin",
        json={
            "login": TEST_USR_LOGIN,
            "password": TEST_USR_PASS
        }
    )
    token = response.json()["token"]
    return token
