import pytest
from httpx import AsyncClient
import uuid
from datetime import datetime

@pytest.mark.asyncio
async def test_create_role_success(client: AsyncClient,
                                   superuser_token: str):
    headers = {"Authorization": f"Bearer {superuser_token}"}
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_create_role_success Начинаем запрос для теста, headers:[{1}]"
              .format(datetime.now(), headers), file=f)
    response = await client.post(
        "/api/roles/roles/",
        json={"name": "testrole", "description": "Test Role"},
        headers=headers
    )
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_create_role_success Получили ответ сервера для теста:[{1}]"
              .format(datetime.now(), response.text), file=f)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "testrole"

@pytest.mark.asyncio
async def test_create_role_unauthorized(client: AsyncClient,
                                        regular_user_token: str):

    headers = {"Authorization": f"Bearer {regular_user_token}"}
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_create_role_unauthorized Начинаем запрос для теста, headers:[{1}]"
              .format(datetime.now(), headers), file=f)
    response = await client.post(
        "/api/roles/roles/",
        json={"name": "testrole", "description": "Test Role"},
        headers=headers
    )
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_create_role_unauthorized Получили ответ сервера для теста:[{1}]"
              .format(datetime.now(), response.text), file=f)
    assert response.status_code == 403
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action")

@pytest.mark.asyncio
async def test_get_roles(client: AsyncClient):
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_get_roles Начинаем запрос для теста"
              .format(datetime.now()), file=f)
    response = await client.get("/api/roles/roles/")
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_get_roles Получили ответ сервера для теста:[{1}]"
              .format(datetime.now(), response.text), file=f)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_role_by_id(client: AsyncClient, superuser_token: str):
    headers = {"Authorization": f"Bearer {superuser_token}"}
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_get_role_by_id Начинаем запрос для теста, headers:[{1}]"
              .format(datetime.now(), headers), file=f)

    #TODO: вот здесь сам rest спроектирован через зад, это get запрос должен быть
    response_create = await client.post(
        "/api/roles/roles/",
        json={"name": "getrole", "description": "Get Role"},
        headers=headers
    )
    role_id = response_create.json()["id"]

    response = await client.get(f"/api/roles/roles/{role_id}")
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_get_role_by_id Получили ответ сервера для теста:[{1}]"
              .format(datetime.now(), response.text), file=f)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == role_id
    assert data["name"] == "getrole"

@pytest.mark.asyncio
async def test_get_role_not_found(client: AsyncClient):
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_get_role_not_found Начинаем запрос для теста"
              .format(datetime.now()), file=f)
    fake_role_id = str(uuid.uuid4())
    response = await client.get(f"/api/roles/roles/{fake_role_id}")
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_get_role_not_found Получили ответ сервера для теста:[{1}]"
              .format(datetime.now(), response.text), file=f)
    assert response.status_code == 404
    assert response.json()["detail"] == "Role not found."

@pytest.mark.asyncio
async def test_update_role_success(client: AsyncClient,
                                   superuser_token: str):
    headers = {"Authorization": f"Bearer {superuser_token}"}
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_update_role_success Начинаем запрос создания роли для теста, headers:[{1}]"
              .format(datetime.now(), headers), file=f)
    response_create = await client.post(
        "/api/roles/roles/",
        json={"name": "updaterole", "description": "Update Role"},
        headers=headers
    )
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_update_role_success Получили ответ сервера на создание роли для теста:[{1}]"
              .format(datetime.now(), response_create.text), file=f)

    role_id = response_create.json()["id"]

    with open('diagnosis.txt', 'a') as f:
        print("{0} test_update_role_success Начинаем запрос обновления роли {1} для теста, headers:[{2}]"
              .format(datetime.now(), role_id, headers), file=f)

    response_update = await client.put(
        f"/api/roles/roles/{role_id}",
        json={"name": "updatedrole", "description": "Updated Role"},
        headers=headers
    )

    with open('diagnosis.txt', 'a') as f:
        print("{0} test_update_role_success Получили ответ сервера на обновление роли для теста:[{1}]"
              .format(datetime.now(), response_update.text), file=f)

    assert response_update.status_code == 200
    data = response_update.json()
    assert data["name"] == "updatedrole"
    assert data["description"] == "Updated Role"

@pytest.mark.asyncio
async def test_update_role_unauthorized(client: AsyncClient,
                                        regular_user_token: str):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_update_role_unauthorized Начинаем запрос для теста, headers:[{1}]"
              .format(datetime.now(), headers), file=f)
    fake_role_id = str(uuid.uuid4())
    response = await client.put(
        f"/api/roles/roles/{fake_role_id}",
        json={"name": "shouldfail", "description": "Should Fail"},
        headers=headers
    )
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_update_role_unauthorized Получили ответ сервера для теста:[{1}]"
              .format(datetime.now(), response.text), file=f)
    assert response.status_code == 403
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action")

@pytest.mark.asyncio
async def test_delete_role_success(client: AsyncClient, superuser_token: str):
    headers = {"Authorization": f"Bearer {superuser_token}"}
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_delete_role_success Начинаем запрос для теста, headers:[{1}]"
              .format(datetime.now(), headers), file=f)
    response_create = await client.post(
        "/api/roles/roles/",
        json={"name": "deleterole", "description": "Delete Role"},
        headers=headers
    )
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_delete_role_success Получили ответ сервера на создание роли для теста:[{1}]"
              .format(datetime.now(), response_create.text), file=f)

    role_id = response_create.json()["id"]

    with open('diagnosis.txt', 'a') as f:
        print("{0} test_delete_role_success Начинаем запрос обновления роли {1} для теста, headers:[{2}]"
              .format(datetime.now(), role_id, headers), file=f)

    response_delete = await client.delete(f"/api/roles/roles/{role_id}", headers=headers)
    assert response_delete.status_code == 204

    with open('diagnosis.txt', 'a') as f:
        print("{0} test_delete_role_success Получили ответ сервера на обновление роли для теста:[{1}]"
              .format(datetime.now(), response_delete.text), file=f)

    with open('diagnosis.txt', 'a') as f:
        print("{0} test_delete_role_success Делаем запрос существования удаленной роли: client.get(\"/api/roles/roles/{1}\")"
              .format(datetime.now(), role_id), file=f)
    response_get = await client.get(f"/api/roles/roles/{role_id}")

    with open('diagnosis.txt', 'a') as f:
        print("{0} test_delete_role_success Получили ответ сервера о существовании удаленной роли для теста:[{1}]"
              .format(datetime.now(), response_get.text), file=f)

    assert response_get.status_code == 404
    assert response_get.json()["detail"] == "Role not found."

@pytest.mark.asyncio
async def test_delete_role_unauthorized(client: AsyncClient,
                                        regular_user_token: str):
    headers = {"Authorization": f"Bearer {regular_user_token}"}
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_delete_role_unauthorized Начинаем запрос для теста, headers:[{1}]"
              .format(datetime.now(), headers), file=f)
    fake_role_id = str(uuid.uuid4())
    response = await client.delete(f"/api/roles/roles/{fake_role_id}", headers=headers)
    with open('diagnosis.txt', 'a') as f:
        print("{0} test_delete_role_unauthorized Получили ответ сервера для теста:[{1}]"
              .format(datetime.now(), response.text), file=f)
    assert response.status_code == 403
    assert (response.json()["detail"] ==
            "You do not have permission to perform this action")
