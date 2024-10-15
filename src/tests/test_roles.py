import pytest
from httpx import AsyncClient
import uuid


@pytest.mark.asyncio
async def test_create_role_success(client: AsyncClient,
                                   superuser_token: str):
    headers = {"Authorization": f"Bearer {superuser_token}"}
    response = await client.post(
        "/roles/",
        json={"name": "testrole", "description": "Test Role"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "testrole"

@pytest.mark.asyncio
async def test_create_role_unauthorized(client: AsyncClient,
                                        regular_user_token: str):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    response = await client.post(
        "/roles/",
        json={"name": "testrole", "description": "Test Role"},
        headers=headers
    )
    assert response.status_code == 403
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action")

@pytest.mark.asyncio
async def test_get_roles(client: AsyncClient):
    response = await client.get("/roles/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_role_by_id(client: AsyncClient, superuser_token: str):
    headers = {"Authorization": f"Bearer {superuser_token}"}
    response_create = await client.post(
        "/roles/",
        json={"name": "getrole", "description": "Get Role"},
        headers=headers
    )
    role_id = response_create.json()["id"]

    response = await client.get(f"/roles/{role_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == role_id
    assert data["name"] == "getrole"

@pytest.mark.asyncio
async def test_get_role_not_found(client: AsyncClient):
    fake_role_id = str(uuid.uuid4())
    response = await client.get(f"/roles/{fake_role_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Role not found."

@pytest.mark.asyncio
async def test_update_role_success(client: AsyncClient,
                                   superuser_token: str):
    headers = {"Authorization": f"Bearer {superuser_token}"}
    response_create = await client.post(
        "/roles/",
        json={"name": "updaterole", "description": "Update Role"},
        headers=headers
    )
    role_id = response_create.json()["id"]

    response_update = await client.put(
        f"/roles/{role_id}",
        json={"name": "updatedrole", "description": "Updated Role"},
        headers=headers
    )
    assert response_update.status_code == 200
    data = response_update.json()
    assert data["name"] == "updatedrole"
    assert data["description"] == "Updated Role"

@pytest.mark.asyncio
async def test_update_role_unauthorized(client: AsyncClient,
                                        regular_user_token: str):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    fake_role_id = str(uuid.uuid4())
    response = await client.put(
        f"/roles/{fake_role_id}",
        json={"name": "shouldfail", "description": "Should Fail"},
        headers=headers
    )
    assert response.status_code == 403
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action")

@pytest.mark.asyncio
async def test_delete_role_success(client: AsyncClient, superuser_token: str):
    headers = {"Authorization": f"Bearer {superuser_token}"}
    response_create = await client.post(
        "/roles/",
        json={"name": "deleterole", "description": "Delete Role"},
        headers=headers
    )
    role_id = response_create.json()["id"]

    response_delete = await client.delete(f"/roles/{role_id}", headers=headers)
    assert response_delete.status_code == 204

    response_get = await client.get(f"/roles/{role_id}")
    assert response_get.status_code == 404
    assert response_get.json()["detail"] == "Role not found."

@pytest.mark.asyncio
async def test_delete_role_unauthorized(client: AsyncClient,
                                        regular_user_token: str):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    fake_role_id = str(uuid.uuid4())
    response = await client.delete(f"/roles/{fake_role_id}", headers=headers)
    assert response.status_code == 403
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action")
