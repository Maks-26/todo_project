# tests/test_auth_login.py

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import RefreshToken, User
from app.utils.security import hash_password

UTC = timezone.utc


def _assert_ok(resp):
    assert resp.status_code == 200, resp.text


def test_login_success(client, db_session: Session, clean_db):
    # 1. Создаём юзера прямо в БД
    user = User(
        email="login_ok@example.com",
        hashed_password=hash_password("goodpass"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    # 2. Пробуем залогиниться правильными данными
    resp = client.post(
        "/login",
        data={"username": "login_ok@example.com", "password": "goodpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    _assert_ok(resp)
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    # 3. Обновляем токен -> получаем новый refresh_token
    resp = client.post("/refresh", params={"refresh_token": data["refresh_token"]})
    new_token = resp.json()
    new_refresh = new_token["refresh_token"]
    assert "access_token" in new_token
    assert "refresh_token" in new_token
    assert new_token["token_type"] == "bearer"

    # 4. Искусственно создаём токен с naive datetime
    naive_token = RefreshToken(
        user_id=user.id,
        token="naive-refresh-token",
        expires_at=datetime.now() + timedelta(days=1),  # naive datetime без tzinfo
    )
    db_session.add(naive_token)
    db_session.commit()

    # Проверяем, что verify_refresh_token корректно обрабатывает naive datetime
    from app.auth_service import verify_refresh_token

    retrieved_user = verify_refresh_token(db_session, "naive-refresh-token")
    assert retrieved_user.id == user.id  # вернул пользователя
    db_session.delete(naive_token)
    db_session.commit()

    # 5. Делаем новый refresh-токен просроченным
    db_token = db_session.query(RefreshToken).filter_by(token=new_refresh).first()
    db_token.expires_at = datetime.now(UTC) - timedelta(days=1)
    db_session.commit()

    # 6. Теперь пытаемся обновить просроченный refresh-токен
    resp = client.post("/refresh", params={"refresh_token": new_refresh})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid refresh token"

    # 7. Проверяем, что токен удалён из БД
    deleted = db_session.query(RefreshToken).filter_by(token=new_refresh).first()
    assert deleted is None

    # 8. Старый refresh токен тоже должен быть недействителен
    resp = client.post("/refresh", params={"refresh_token": data["refresh_token"]})
    assert resp.status_code == 401


def test_login_wrong_password(client, db_session: Session, clean_db):
    user = User(
        email="login_wrong@example.com",
        hashed_password=hash_password("correct"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    resp = client.post(
        "/login",
        data={"username": "login_wrong@example.com", "password": "badpass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "❌ badpass Пароль не верный  !!!"


def test_login_nonexistent_user(client, db_session, clean_db):
    resp = client.post(
        "/login",
        data={"username": "nosuch@example.com", "password": "irrelevant"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401
    assert (
        resp.json()["detail"] == "❌ Пользователь с email nosuch@example.com не найден"
    )


def test_login_json(client, db_session: Session, clean_db):
    user = User(
        email="login_wrong@example.com",
        hashed_password=hash_password("correct"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    resp = client.post(
        "/login-json",
        json={"username": "login_wrong@example.com", "password": "correct"},
    )
    _assert_ok(resp)
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    resp = client.post(
        "/login-json",
        json={"username": "login_wrong@example.com", "password": "badpass"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "❌ badpass Пароль не верный  !!!"


def test_login_json_nonexistent_user(client, clean_db):
    resp = client.post(
        "/login-json",
        json={"username": "nosuch@example.com", "password": "irrelevant"},
    )
    assert resp.status_code == 401
    assert (
        resp.json()["detail"] == "❌ Пользователь с email nosuch@example.com не найден"
    )
