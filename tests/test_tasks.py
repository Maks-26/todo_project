# tests/test_tasks.py

import pytest
from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


@pytest.fixture
def auth_header(client):
    """Создаёт пользователя (если его нет) и возвращает заголовок авторизации."""

    def _auth_header(
        email: str = "test@example.com", password: str = "password", role: str = "user"
    ):
        # 1️⃣ пробуем зарегистрировать
        resp = client.post(
            "/register",
            params={"role": role},
            json={"username": email, "password": password},
        )

        if resp.status_code == 200:
            # регистрация прошла успешно
            pass
        elif resp.status_code == 400:
            # пользователь уже существует — это норм
            pass
        else:
            raise AssertionError(
                f"Unexpected register response: {resp.status_code}, body={resp.text}"
            )

        # 2️⃣ теперь логинимся
        login = client.post(
            "/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if login.status_code != 200:
            raise AssertionError(
                f"Login failed: {login.status_code}, body={login.text}"
            )

        token = login.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth_header


@pytest.fixture
def create_task(client, auth_header):
    """Создаёт задачу и возвращает (task_dict, headers)"""

    def _create_task(
        description: str = "Test Description",
        email: str = "test@example.com",
        password: str = "password",
        role: str = "user",
    ):
        headers = auth_header(email=email, password=password, role=role)
        response = client.post(
            "/tasks/",
            json={"description": description},
            headers=headers,
        )
        assert response.status_code == 201
        return response.json(), headers

    return _create_task
    # ---------------------- ТЕСТЫ ----------------------
    """ Получить задачи """


#  Пользователь видит только свои задачи
def test_get_tasks_only_user_tasks(client, db_session, clean_db, create_task):
    # user A
    _, headers = create_task(
        description="A1",
        email="a@example.com",
        password="1",
    )
    create_task(
        description="A2",
        email="a@example.com",
        password="1",
    )
    # user B
    create_task(
        description="B1",
        email="b@example.com",
        password="1",
    )

    resp = client.get("/tasks", headers=headers)

    assert resp.status_code == 200
    data = resp.json()
    save_headers = headers
    get_first_id = data["items"][0]["id"]

    # total = только A1 и A2
    assert data["total"] == 2
    assert data["count"] == 2
    assert {t["description"] for t in data["items"]} == {"A1", "A2"}

    # Админ видит все задачи
    _, headers = create_task(
        description="Admin_1",
        email="admin@example.com",
        password="1",
        role="admin",
    )
    resp = client.get("/tasks", headers=headers)
    data = resp.json()

    assert data["total"] == 4
    assert data["count"] == 4

    # Фильтрация completed
    task = client.patch(f"/tasks/{get_first_id}/complete", headers=save_headers)

    assert task.status_code == 200

    resp = client.get("/tasks?completed=true", headers=save_headers)
    data = resp.json()

    assert data["total"] == 1
    assert data["items"][0]["completed"] is True

    # Поиск по description
    _, headers = create_task(
        description="Buy milk",
        email="s@example.com",
        password="1",
    )
    create_task(
        description="Buy bread",
        email="s@example.com",
        password="1",
    )
    create_task(
        description="Sleep",
        email="s@example.com",
        password="1",
    )

    resp = client.get("/tasks?search=buy", headers=headers)
    data = resp.json()

    assert data["total"] == 2
    assert {t["description"] for t in data["items"]} == {"Buy milk", "Buy bread"}

    # Пагинация skip+limit и корректное total
    p = 1
    _, headers = create_task(
        description=f"T{p}",
        email="p@example.com",
        password="1",
    )
    for i in range(19):
        n = i + p
        client.post("/tasks/", json={"description": f"T{n}"}, headers=headers)
    resp = client.get("/tasks?skip=5&limit=5", headers=headers)
    data = resp.json()

    assert data["total"] == 20  # total без учета offset/limit
    assert data["count"] == 5  # ровно limit элементов
    assert data["items"][0]["description"] == "T5"

    """  Добавить задачу  """


def test_create_and_list_tasks(client, create_task, auth_header):
    # Пробуем добавить пустую задачу
    headers = auth_header()
    task = client.post("/tasks/", json={"description": "   "}, headers=headers)
    assert task.status_code == 422
    error_detail = task.json().get("detail")[0]
    assert error_detail["loc"] == ["body", "description"]
    assert error_detail["msg"] == "Value error, Описание задачи не может быть пустым"
    assert error_detail["type"] == "value_error"

    task, headers = create_task("Hello world")
    resp = client.get("/tasks/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()["items"]
    assert len(data) == 1
    assert data[0]["description"] == "Hello world"

    """  Изменить задачу и статус  """


def test_update_task(client, create_task, auth_header):
    # Пробуем изменить задачу и статус
    task, headers = create_task("Old title")
    resp = client.patch(
        f"/tasks/{task['id']}",
        json={"description": "New title", "completed": True},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "New title"
    assert resp.json()["completed"]

    # Пробуем добавить пустую задачу
    empty_task = client.patch(
        f"/tasks/{task["id"]}", json={"description": "   "}, headers=headers
    )
    assert empty_task.status_code == 422
    error_detail = empty_task.json().get("detail")[0]
    assert error_detail["loc"] == ["body", "description"]
    assert error_detail["msg"] == "Value error, Description cannot be blank"
    assert error_detail["type"] == "value_error"

    # Задачи нет
    resp = client.patch(
        f"/tasks/{200}",
        json={"description": "New title"},
        headers=headers,
    )
    assert resp.status_code == 404

    # задача принадлежит другому пользователю
    headers = auth_header(email="test@example2.com")
    resp = client.patch(
        f"/tasks/{task['id']}", json={"description": "New title"}, headers=headers
    )
    assert resp.status_code == 403

    """ изменить задачу """


def test_update_task_description(client, create_task):
    task, headers = create_task("Task")
    resp = client.patch(
        f"/tasks/{task['id']}/description",
        json={"description": "   "},
        headers=headers,
    )
    assert resp.status_code == 422

    resp = client.patch(
        f"/tasks/{task['id']}/description",
        json={"description": "New task"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "New task"

    """ Удалить задачу """


def test_delete_task(client, create_task):
    task, headers = create_task("To delete")
    resp = client.delete(f"/tasks/{task['id']}", headers=headers)
    assert resp.status_code == 204
    # Проверим, что задача удалена
    resp = client.get("/tasks/", headers=headers)
    print(resp)
    assert all(t["id"] != task["id"] for t in resp.json()["items"])

    """ Отметить как выполненную """


def test_complete_task(client, create_task):
    task, headers = create_task("Incomplete task")
    resp = client.patch(f"/tasks/{task['id']}/complete", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["completed"] is True

    """ Поиск по ключу """


def test_search_task(client, create_task, auth_header, clean_db):
    # БД пустая
    headers = auth_header()
    resp = client.get("/tasks/search?keyword=world", headers=headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Таблица задач пуста"

    # Поиск удачный
    create_task("Hello world")
    _, headers = create_task()
    # Поиск не удачный
    resp = client.get("/tasks/search?keyword=My task", headers=headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Задачи с ключом 'My task' не найдены"

    # # Поиск с пустым данными
    resp = client.get("/tasks/search", headers=headers)
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Ключевое слово не может быть пустым"

    # Поиск удачный
    resp = client.get("/tasks/search?keyword=world", headers=headers)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["description"] == "Hello world"
