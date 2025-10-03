# tests/test_admin_route.py

from app.models import User
from app.utils.security import hash_password


def test_admin_dashboard_success(client, db_session):
    """
    Проверка: админ может зайти на /admin/dashboard.
    """
    # создаём админа
    admin = User(
        email="admin@example.com", hashed_password=hash_password("123"), role="admin"
    )
    db_session.add(admin)
    db_session.commit()

    # логинимся (используем вспомогательную функцию _auth_header)
    resp = client.post(
        "/login",
        data={"username": admin.email, "password": "123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # проверяем доступ
    r = client.get("/admin/dashboard", headers=headers)
    assert r.status_code == 200
    assert "Welcome, admin" in r.json()["message"]


def test_admin_dashboard_forbidden(client, db_session):
    """
    Проверка: обычный пользователь не имеет доступа к /admin/dashboard.
    """
    user = User(
        email="user@example.com", hashed_password=hash_password("123"), role="user"
    )
    db_session.add(user)
    db_session.commit()

    resp = client.post(
        "/login",
        data={"username": user.email, "password": "123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/admin/dashboard", headers=headers)
    assert r.status_code == 403
    assert r.json()["detail"] == "Access forbidden: Admins only"
