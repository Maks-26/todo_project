# tests/test_auth_register.py

from sqlalchemy.orm import Session

from app.models import User


def _assert_ok(resp):
    # Если упадёт, сразу увидишь причину от FastAPI
    assert resp.status_code == 200, resp.text


# Позитив: регистрация обычного пользователя (role=user по dropdown/query
def test_register_user_default_role(client, db_session: Session):
    # Отправляем JSON-тело + выбираем роль через query (?role=user)
    resp = client.post(
        "/register?role=user",
        json={"email": "u1@example.com", "password": "pass123"},
    )
    _assert_ok(resp)
    data = resp.json()
    assert "access_token" in data

    user = db_session.query(User).filter_by(email="u1@example.com").first()
    assert user is not None
    assert user.role == "user"


# Позитив: регистрация администратора (role=admin через dropdown/query)
def test_register_admin_role(client, db_session: Session):
    resp = client.post(
        "/register?role=admin",
        json={"email": "admin@example.com", "password": "secret123"},
    )
    _assert_ok(resp)

    # Проверяем, что пользователь записан в БД с правильной ролью
    user = db_session.query(User).filter_by(email="admin@example.com").first()
    assert user is not None
    assert user.role == "admin"


# Негатив: повторная регистрация с тем же email → 400
def test_register_duplicate_email_(client, db_session: Session):
    first = client.post(
        "/register?role=user",
        json={"email": "dup@example.com", "password": "x"},
    )
    _assert_ok(first)

    second = client.post(
        "/register?role=admin",
        json={"email": "dup@example.com", "password": "x"},
    )
    print(">>>>", second.status_code, second.json())
    # Должна быть 400, а если не так — покажем тело ответа
    assert second.status_code == 400, second.text
    assert "уже существует" in second.json()["detail"]
