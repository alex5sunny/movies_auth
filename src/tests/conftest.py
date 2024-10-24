import os
import subprocess
import time

#слегка проверим что pytest запущен из папочки src и сгенерируем понятный текст исключения если это не так
if not os.path.isfile(os.path.join(os.getcwd(), 'main.py')):
    raise Exception("The file main.py doesnt exits in the context, go to the folder \"src\" before start pytest")

from datetime import datetime
from environs import Env
from dotenv import load_dotenv
load_dotenv('../configs/.env.test')
env_for_subprocess = Env()
env_for_subprocess.read_env('../configs/.env.test')

with open('diagnosis.txt', 'w') as f:
    print("{0} pytest приступил к работе".format(datetime.now()), file=f)

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
#from db.postgres import get_session
#from main import app

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


engine_adm = create_async_engine(dsn_adm, echo=True, isolation_level="AUTOCOMMIT", future=True)
engine = create_async_engine(dsn, echo=True, future=True, pool_size=10, max_overflow=20)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# fixture for the database preparation
@pytest_asyncio.fixture(scope="session")
async def prepare_db():
    async with engine_adm.connect() as conn:

        with open('diagnosis.txt', 'a') as f:
            print("{0} подключились к engine_adm, приступаем к создания базы данных movies_database_test".
                  format(datetime.now()), file=f)

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

    with open('diagnosis.txt', 'a') as f:
        print("{0} создана база данных movies_database_test, применены миграции".format(datetime.now()), file=f)

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

    with open('diagnosis.txt', 'a') as f:
        print("{0} созданы учетные записи admin user и regular user".format(datetime.now()), file=f)

    with open('diagnosis.txt', 'a') as f:
        print("{0} запускаем subprocess.Popen".format(datetime.now()), file=f)
    process = subprocess.Popen(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"], env=os.environ)
    time.sleep(3)
    with open('diagnosis.txt', 'a') as f:
        print("{0} запустили subprocess.Popen".format(datetime.now()), file=f)
    yield

    async with engine_adm.connect() as conn:
        with open('diagnosis.txt', 'a') as f:
            print("{0} подключились к engine_adm, приступаем к удалению базы данных movies_database_test".
                  format(datetime.now()), file=f)

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
        process.terminate()

        with open('diagnosis.txt', 'a') as f:
            print("{0} Удалили базу данных movies_database_test".
                  format(datetime.now()), file=f)



# fixture for the FastAPI test client
@pytest_asyncio.fixture(scope="function")
async def client(prepare_db) -> AsyncGenerator[AsyncClient, None]:
    #app.dependency_overrides[get_session] = testing_get_session_override
    async with AsyncClient(base_url="http://127.0.0.1:8000") as ac:
        with open('diagnosis.txt', 'a') as f:
            print("{0} Создали и отдали в тесты client: AsyncClient ".format(datetime.now()), file=f)
        yield ac

        with open('diagnosis.txt', 'a') as f:
            print("{0} Закрыли client: AsyncClient ".format(datetime.now()), file=f)

# fixture to create a superuser and get token
@pytest_asyncio.fixture(scope="function")
async def superuser_token(prepare_db,  client):
    with open('diagnosis.txt', 'a') as f:
        print("{0} Приступаем к запросу token для superuser.".format(datetime.now()), file=f)
    response = await client.post(
        "/api/users/signin",
        json={
            "login": TEST_ADM_LOGIN,
            "password": TEST_ADM_PASS
        }
    )

    token = response.json()["token"]
    with open('diagnosis.txt', 'a') as f:
        print("{0} Создали и отдали в тесты token для superuser. token=:[{1}]".format(datetime.now(), token), file=f)
    yield token
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/api/users/logout",
        headers=headers
    )


# fixture to create a regular user and get token
@pytest_asyncio.fixture(scope="function")
async def regular_user_token(prepare_db,  client):
    with open('diagnosis.txt', 'a') as f:
        print("{0} Приступаем к запросу token для regularuser".format(datetime.now()), file=f)
    response = await client.post(
        "/api/users/signin",
        json={
            "login": TEST_USR_LOGIN,
            "password": TEST_USR_PASS
        }
    )
    token = response.json()["token"]
    with open('diagnosis.txt', 'a') as f:
        print("{0} Создали и отдали в тесты token для regularuser. token=:[{1}]".format(datetime.now(), token), file=f)
    yield token
    headers = {"Authorization": f"Bearer {token}"}
    client.post(
        "/api/users/logout",
        headers=headers
    )
