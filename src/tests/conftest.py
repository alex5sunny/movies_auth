import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from main import app
from db.postgres import get_session, Base, engine
from models.user import User
from typing import AsyncGenerator

# fixture for the db engine
@pytest.fixture(scope="session")
async def db_engine():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# fixture for the db session
@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSession(bind=db_engine)
    try:
        yield async_session
    finally:
        await async_session.close()

# fixture for the FastAPI test client
@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()

# fixture to create a superuser and get token
@pytest.fixture(scope="function")
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
@pytest.fixture(scope="function")
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
