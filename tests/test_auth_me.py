from app.models import User
from app.utils.security import hash_password


def _assert_ok(resp):
    assert resp.status_code == 200, resp.text


def test_me_with_valid_token(client, db_session):
    # 1. Создаём пользователя
    user = User(
        email="me_ok@example.com",
        hashed_password=hash_password("12345"),
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    # 2. Логинимся, получаем токен
    login_resp = client.post(
        "/login",
        data={"username": "me_ok@example.com", "password": "12345"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    _assert_ok(login_resp)
    token = login_resp.json()["access_token"]

    # 3. Обращаемся к /me с токеном
    me_resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    _assert_ok(me_resp)

    data = me_resp.json()
    assert data["email"] == "me_ok@example.com"
    assert data["role"] == "user"


def test_me_without_token(client):
    # Если токен не передан
    resp = client.get("/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"


def test_me_with_invalid_token(client):
    # Если токен поддельный
    resp = client.get("/me", headers={"Authorization": "Bearer FAKE_TOKEN"})
    assert resp.status_code == 401
    # Обычно detail = "Could not validate credentials"
    assert "detail" in resp.json()
