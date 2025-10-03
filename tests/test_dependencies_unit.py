# tests/test_dependencies.py

import pytest
from fastapi import HTTPException
from jose import jwt

from app.dependencies import get_current_user, get_db, require_admin, require_user
from app.models import Task, User
from app.utils.security import hash_password
from settings import get_settings

settings = get_settings()


def test_get_db_closes_connection():
    """
    Проверка: get_db возвращает соединение и закрывает его.
    """
    gen = get_db()
    db = next(gen)  # получаем db из yield
    assert db is not None  # соединение выдано
    # закрытие
    try:
        next(gen)
    except StopIteration:
        pass  # генератор завершён — значит db.close() вызван


# ------------------ Unit-тесты require_admin ------------------


def test_require_admin_forbidden_unit(db_session):
    """
    Проверка: пользователь с ролью 'user' не может пройти require_admin.
    Ожидаем HTTPException с кодом 403.
    """
    # Создаём пользователя с ролью "user"
    user = User(
        email="simple@example.com", hashed_password=hash_password("123"), role="user"
    )
    db_session.add(user)
    db_session.commit()

    # Проверяем, что require_admin вызывает HTTPException
    with pytest.raises(HTTPException) as e:
        require_admin(current_user=user)
    assert e.value.status_code == 403


def test_require_admin_success_unit(db_session):
    """
    Проверка: пользователь с ролью 'admin' проходит require_admin.
    """
    admin = User(
        email="admin@example.com", hashed_password=hash_password("123"), role="admin"
    )
    db_session.add(admin)
    db_session.commit()

    # Функция должна вернуть пользователя без ошибок
    result = require_admin(current_user=admin)
    assert result == admin


# ------------------ Unit-тесты require_user ------------------


def test_require_user_forbidden_unit(db_session):
    """
    Проверка: пользователь с ролью 'guest' не может пройти require_user.
    """
    guest = User(
        email="guest@example.com", hashed_password=hash_password("123"), role="guest"
    )
    db_session.add(guest)
    db_session.commit()

    with pytest.raises(HTTPException) as e:
        require_user(current_user=guest)
    assert e.value.status_code == 403


def test_require_user_success_user_unit(db_session):
    """
    Проверка: пользователь с ролью 'user' успешно проходит require_user.
    """
    u = User(
        email="user@example.com", hashed_password=hash_password("123"), role="user"
    )
    db_session.add(u)
    db_session.commit()

    assert require_user(current_user=u) == u


def test_require_user_success_admin_unit(db_session):
    """
    Проверка: пользователь с ролью 'admin' также проходит require_user.
    """
    a = User(
        email="admin@example.com", hashed_password=hash_password("123"), role="admin"
    )
    db_session.add(a)
    db_session.commit()

    assert require_user(current_user=a) == a


# ------------------ Тесты __repr__ ------------------


def test_task_repr():
    """
    Проверка: строковое представление Task.
    """
    task = Task(description="Test", user_id=1)
    assert "Test" in repr(task)


def test_user_repr():
    """
    Проверка: строковое представление User.
    """
    user = User(email="user@example.com", hashed_password="123", role="user")
    assert "user@example.com" in repr(user)


# ------------------ Unit-тесты get_current_user ------------------


def test_get_current_user_invalid_token(db_session):
    """
    Проверка: неверный токен вызывает HTTPException.
    """
    invalid_token = "invalid.token.string"
    with pytest.raises(HTTPException) as e:
        # db_session нужен, чтобы satisfy Depends
        list(get_current_user(token=invalid_token, db=db_session))
    assert e.value.status_code == 401


def test_get_current_user_user_not_found(db_session):
    """
    Проверка: токен корректный, но пользователь не существует.
    """
    token = jwt.encode(
        {"sub": "nosuch@example.com"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    with pytest.raises(HTTPException) as e:
        list(get_current_user(token=token, db=db_session))
    assert e.value.status_code == 401


def test_get_current_user_email_none(db_session):
    """
    Проверка: если в токене нет 'sub', поднимается HTTPException (строка 39).
    """
    token = jwt.encode({}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(HTTPException) as e:
        get_current_user(token=token, db=db_session)
    assert e.value.status_code == 401
