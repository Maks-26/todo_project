# tests/test_tasks.py
from app.models import Task, User
from app.utils.security import hash_password


# добавляем пользователя в БД
def _auth_header(
    client, db_session, email="tasks@example.com", password="12345", role="user"
):
    """Создаёт юзера если нету"""
    user = db_session.query(User).filter_by(email=email).first()
    if not user:
        """Создаёт юзера, логинитса и возвращает headers с токеном."""
        user = User(email=email, hashed_password=hash_password(password), role=role)
        db_session.add(user)
        db_session.commit()

    resp = client.post(
        "/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# добавить задачу
def test_create_task(client, db_session):
    headers = _auth_header(client, db_session)

    # пробуем создать задачу с пустым описанием
    resp = client.post("/tasks", json={"description": ""}, headers=headers)
    assert resp.status_code == 422

    # пробуем создать задачу с пробелами
    resp = client.post("/tasks", json={"description": "   "}, headers=headers)
    assert resp.status_code == 422

    # пробуем создать задачу
    resp = client.post("/tasks", json={"description": "My first task"}, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["description"] == "My first task"
    assert data["completed"] is False


# список задач
def test_list_tasks(client, db_session):
    headers = _auth_header(client, db_session)
    # создаём пару задач
    client.post("/tasks", json={"description": "Task A"}, headers=headers)
    client.post("/tasks", json={"description": "Task B"}, headers=headers)

    resp = client.get("/tasks", headers=headers)
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) >= 2
    assert any(t["description"] == "Task A" for t in tasks)


# изменить задачу и статус
def test_update_task_and_status(client, db_session):
    headers = _auth_header(client, db_session)
    user_headers = _auth_header(
        client, db_session, email="user@example.com", password="123", role="user"
    )
    create_resp = client.post(
        "/tasks", json={"description": "Old desc"}, headers=headers
    )
    task_id = create_resp.json()["id"]

    # пробуем изменить задачу с пустым описанием
    resp = client.patch(
        f"/tasks/{task_id}",
        json={"description": "", "completed": True},
        headers=headers,
    )
    assert resp.status_code == 422

    # пробуем изменить задачу с пробелами
    resp = client.patch(
        f"/tasks/{task_id}",
        json={"description": "   ", "completed": True},
        headers=headers,
    )
    assert resp.status_code == 422

    # пробуем изменить задачу с несуществующим id
    not_resp = client.patch(
        "/tasks/99", json={"description": "New desc"}, headers=headers
    )
    data = not_resp.json()
    assert not_resp.status_code == 404
    assert data["detail"] == "Задача 99 не найдена"

    # пробуем изменить задачу другим пользователем
    resp = client.patch(
        f"/tasks/{task_id}",
        json={"description": "New desc", "completed": True},
        headers=user_headers,
    )
    assert resp.status_code == 403

    # пробуем изменить задачу пользователем
    resp = client.patch(
        f"/tasks/{task_id}",
        json={"description": "New desc", "completed": True},
        headers=headers,
    )
    assert resp.status_code == 200

    data = resp.json()
    assert data["description"] == "New desc"
    assert data["completed"]


# изменить задачу
def test_update_task(client, db_session):
    headers = _auth_header(client, db_session)
    user_headers = _auth_header(
        client, db_session, email="user@example.com", password="123", role="user"
    )
    create_resp = client.post(
        "/tasks", json={"description": "Old desc"}, headers=headers
    )
    task_id = create_resp.json()["id"]

    # пробуем изменить задачу другим пользователем
    resp = client.patch(
        f"/tasks/{task_id}/description",
        json={"description": "New desc"},
        headers=user_headers,
    )
    assert resp.status_code == 403

    # пробуем изменить задачу с несуществующим id
    not_resp = client.patch(
        "/tasks/99/description", json={"description": "New desc"}, headers=headers
    )
    assert not_resp.status_code == 404

    # пробуем изменить задачу
    resp = client.patch(
        f"/tasks/{task_id}/description",
        json={"description": "New desc"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "New desc"


# завершить задачу
def test_complete_task(client, db_session):
    """Добавляем двух пользователей и задачу"""
    headers = _auth_header(client, db_session)
    user_headers = _auth_header(
        client, db_session, email="user@example.com", password="123", role="user"
    )
    create_resp = client.post(
        "/tasks", json={"description": "Incomplete"}, headers=headers
    )

    # Проверяем создание задачи
    task_id = create_resp.json()["id"]
    data = db_session.query(Task).filter_by(id=task_id).first()

    assert create_resp.status_code == 201
    assert not data.completed

    # Пробуем изминаем другим пользователем
    resp = client.patch(f"/tasks/{task_id}/complete", headers=user_headers)
    data = db_session.query(Task).filter_by(id=task_id).first()

    assert resp.status_code == 403
    assert not data.completed

    # Меняем самим пользователем
    resp = client.patch(f"/tasks/{task_id}/complete", headers=headers)
    data = db_session.query(Task).filter_by(id=task_id).first()

    assert resp.status_code == 200
    assert data.completed


# Поиск по ключу
def test_search_tasks_keyword(client, db_session):
    headers = _auth_header(client, db_session)
    user_headers = _auth_header(
        client, db_session, email="user@example.com", password="123", role="user"
    )

    # Проверяем пустую базу пользователем
    tasks = client.get("/tasks/search/my", headers=headers, params={"mode": "slow"})
    assert tasks.status_code == 404

    resp = client.post("/tasks", json={"description": "My task"}, headers=headers)
    assert resp.status_code == 201

    # Проверяем пользователем
    tasks = client.get("/tasks/search/my", headers=headers)
    assert tasks.status_code == 200
    data = tasks.json()
    assert len(data) == 1
    assert data[0]["description"] == "My task"

    # Проверяем не найдено другим пользователем
    tasks = client.get("/tasks/search/My", headers=user_headers)
    assert tasks.status_code == 404

    tasks = client.get(f"/tasks/search/{" "}", headers=headers)
    assert tasks.status_code == 400


# тест удалить задачу
def test_delete_task(client, db_session):
    headers = _auth_header(client, db_session)
    user_headers = _auth_header(
        client, db_session, email="user@example.com", password="123", role="user"
    )
    create_resp = client.post(
        "/tasks", json={"description": "To delete"}, headers=headers
    )
    task_id = create_resp.json()["id"]

    # пробуем удалить задачу другим пользователем
    resp = client.delete(f"/tasks/{task_id}", headers=user_headers)
    assert resp.status_code == 403

    # пробуем удалить задачу не существующей id
    resp = client.delete("/tasks/99", headers=headers)
    assert resp.status_code == 404

    # пробуем удалить задачу
    resp = client.delete(f"/tasks/{task_id}", headers=headers)
    assert resp.status_code == 204

    # проверим, что задачи больше нет
    list_resp = client.get("/tasks", headers=headers)
    tasks = list_resp.json()
    assert all(t["id"] != task_id for t in tasks)


# проверка права
def test_require_admin(client, db_session):
    # user
    user_headers = _auth_header(
        client, db_session, email="user@example.com", password="123", role="user"
    )
    # admin
    admin_headers = _auth_header(
        client, db_session, email="admin@example.com", password="123", role="admin"
    )

    # обычный пользователь → 403
    resp = client.get("/admin/dashboard", headers=user_headers)
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Access forbidden: Admins only"

    # админ → 200
    resp = client.get("/admin/dashboard", headers=admin_headers)
    assert resp.status_code == 200
    assert "welcome" in resp.json()["message"].lower()
