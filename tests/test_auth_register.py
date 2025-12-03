# tests/test_auth_register.py

from sqlalchemy.orm import Session

from app.models import User


def _assert_ok(resp):
    """
    Проверка: статус 200, иначе покажем текст ответа.
    """
    assert resp.status_code == 200, resp.text


def test_register_user_default_role(client, db_session: Session):
    """
    ✅ Позитивная проверка: регистрация пользователя с ролью 'user'.
    """
    resp = client.post(
        "/register?role=user",
        json={"username": "u1@example.com", "password": "pass123"},
    )
    _assert_ok(resp)
    data = resp.json()
    assert "access_token" in data

    # Проверяем, что пользователь появился в БД
    user = db_session.query(User).filter_by(email="u1@example.com").first()
    assert user is not None
    assert user.role == "user"


def test_register_admin_role(clean_db, admin_user, db_session: Session):
    """
    ✅ Проверка через фикстуру: администратор создан в БД с ролью 'admin'.
    """
    # admin_user уже создан фикстурой → проверим в базе
    user = db_session.query(User).filter_by(email=admin_user.email).first()
    assert user is not None
    assert user.role == "admin"


def test_register_duplicate_email(client, db_session: Session):
    """
    ❌ Негативная проверка: повторная регистрация с тем же email → 400.
    """
    # Первый запрос проходит успешно
    first = client.post(
        "/register?role=user",
        json={"username": "dup@example.com", "password": "x"},
    )
    _assert_ok(first)

    # Повторный запрос с тем же email должен упасть
    second = client.post(
        "/register?role=admin",
        json={"username": "dup@example.com", "password": "x"},
    )

    assert second.status_code == 400, second.text
    assert "уже существует" in second.json()["detail"]
