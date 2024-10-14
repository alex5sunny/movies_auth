import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    response = await client.post(
        "/signup",
        json={
            "login": "testuser",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"

@pytest.mark.asyncio
async def test_signup_duplicate_user(client: AsyncClient):
    await client.post(
        "/signup",
        json={
            "login": "testuser",
            "password": "testpassword",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    response = await client.post(
        "/signup",
        json={
            "login": "testuser",
            "password": "testpassword2",
            "first_name": "Test2",
            "last_name": "User2"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this login already exists."

@pytest.mark.asyncio
async def test_signin_success(client: AsyncClient):
    await client.post(
        "/signup",
        json={
            "login": "signinuser",
            "password": "signinpassword",
            "first_name": "Sign",
            "last_name": "In"
        }
    )
    response = await client.post(
        "/signin",
        json={
            "login": "signinuser",
            "password": "signinpassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_signin_wrong_password(client: AsyncClient):
    await client.post(
        "/signup",
        json={
            "login": "signinuser2",
            "password": "signinpassword",
            "first_name": "Sign",
            "last_name": "In"
        }
    )
    response = await client.post(
        "/signin",
        json={
            "login": "signinuser2",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password"

@pytest.mark.asyncio
async def test_signin_history(client: AsyncClient):
    await client.post(
        "/signup",
        json={
            "login": "historyuser",
            "password": "historypassword",
            "first_name": "History",
            "last_name": "User"
        }
    )
    response_signin = await client.post(
        "/signin",
        json={
            "login": "historyuser",
            "password": "historypassword"
        }
    )
    token = response_signin.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/signin_history", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least one login event

@pytest.mark.asyncio
async def test_check_token_valid(client: AsyncClient):
    await client.post(
        "/signup",
        json={
            "login": "tokenuser",
            "password": "tokenpassword",
            "first_name": "Token",
            "last_name": "User"
        }
    )
    response_signin = await client.post(
        "/signin",
        json={
            "login": "tokenuser",
            "password": "tokenpassword"
        }
    )
    token = response_signin.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/check_token", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "tokenuser"

@pytest.mark.asyncio
async def test_check_token_invalid(client: AsyncClient):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.get("/check_token", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token!"

@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    await client.post(
        "/signup",
        json={
            "login": "refreshuser",
            "password": "refreshpassword",
            "first_name": "Refresh",
            "last_name": "User"
        }
    )
    response_signin = await client.post(
        "/signin",
        json={
            "login": "refreshuser",
            "password": "refreshpassword"
        }
    )
    refresh_token = response_signin.json()["refresh_token"]
    headers = {"Authorization": f"Bearer {refresh_token}"}

    response = await client.post("/refresh", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.post("/refresh", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token!"

@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient):
    await client.post(
        "/signup",
        json={
            "login": "logoutuser",
            "password": "logoutpassword",
            "first_name": "Logout",
            "last_name": "User"
        }
    )
    response_signin = await client.post(
        "/signin",
        json={
            "login": "logoutuser",
            "password": "logoutpassword"
        }
    )
    token = response_signin.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post("/logout", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Successfully logged out"

    response_protected = await client.get("/signin_history", headers=headers)
    assert response_protected.status_code == 401
    assert response_protected.json()["detail"] in [
        "Token has been invalidated!",
        "Invalid token!",
        "Token expired!",
    ]

@pytest.mark.asyncio
async def test_logout_invalid_token(client: AsyncClient):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.post("/logout", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token!"
