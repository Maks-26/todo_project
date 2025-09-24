# tests/test_auth_login.py

from sqlalchemy.orm import Session

from app.models import User
from app.utils.security import hash_password


def _assert_ok(resp):
    assert resp.status_code == 200, resp.text


def test_login_success(client, db_session: Session):
    # Создаём юзера прямо в БД
    user = User(
        email="login_ok@example.com",
        hashed_password=hash_password("goodpass"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    # Пробуем залогиниться правильными данными
    resp = client.post(
        "/login",
        data={"username": "login_ok@example.com", "password": "goodpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    _assert_ok(resp)
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, db_session: Session):
    # Создаём юзера
    user = User(
        email="login_wrong@example.com",
        hashed_password=hash_password("correct"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    # Логинимся с неправильным паролем
    resp = client.post(
        "/login",
        data={"username": "login_wrong@example.com", "password": "badpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "❌ badpass Пароль не верный  !!!"


def test_login_nonexistent_user(client):
    # Юзер вообще не создан
    resp = client.post(
        "/login",
        data={"username": "nosuch@example.com", "password": "irrelevant"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401
    assert (
        resp.json()["detail"] == "❌ Пользователь с email nosuch@example.com не найден"
    )
