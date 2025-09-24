# tests/test_dependencies.py
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jose import jwt

from app.api import app
from app.dependencies import get_current_user, get_db, require_admin, require_user
from app.models import Task, User
from app.utils.jwt_token import create_access_token
from app.utils.security import hash_password
from settings import get_settings

client = TestClient(app)
settings = get_settings()


# ---------- get_current_user через API ----------
# тест: неверный токен -> 401
def test_get_current_user_invalid_token():
    resp = client.get("/tasks", headers={"Authorization": "Bearer WRONGTOKEN"})
    assert resp.status_code == 401
    assert "Не удалось проверить" in resp.json()["detail"]


# тест: токен без sub -> 401
def test_get_current_user_missing_sub(db_session):
    token = jwt.encode({}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    resp = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


# тест: токен с sub=None -> 401
def test_get_current_user_sub_none(db_session):
    token = jwt.encode({"sub": None}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    resp = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


# тест: токен с юзером, которого нет в БД -> 401
def test_get_current_user_user_not_in_db(db_session):
    token = jwt.encode(
        {"sub": "ghost@example.com"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    resp = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


# ---------- require_admin / require_user через API ----------
# тест: пользователь с ролью "user" заходит в админку -> 403
def test_require_admin_forbidden(db_session):
    user = User(
        email="simple@example.com", hashed_password=hash_password("123"), role="user"
    )
    db_session.add(user)
    db_session.commit()

    token = create_access_token({"sub": user.email})
    resp = client.get("/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert "Admins only" in resp.json()["detail"]


# тест: пользователь с ролью "guest" заходит в /tasks -> 403
def test_require_user_forbidden(db_session):
    user = User(
        email="guest@example.com", hashed_password=hash_password("123"), role="guest"
    )
    db_session.add(user)
    db_session.commit()

    token = create_access_token({"sub": user.email})
    resp = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
    assert "Users only" in resp.json()["detail"]


# ---------- Unit-тесты get_db ----------
# тестируем подключение к БД (генератор yield/close)
def test_get_db_finally_called():
    gen = get_db()
    db = next(gen)
    # проверяем возврат подключения к БД
    assert db is not None
    # закрываем генератор -> должен вызваться finally: db.close()
    gen.close()


# ---------- Unit-тесты get_current_user ----------
# тест: битый токен вызывает 401
def test_get_current_user_invalid_jwt(db_session):
    with pytest.raises(HTTPException) as e:
        get_current_user(token="WRONGTOKEN", db=db_session)
    assert e.value.status_code == 401


# тест: токен без sub вызывает 401
def test_get_current_user_missing_sub_unit(db_session):
    token = jwt.encode({}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(HTTPException):
        get_current_user(token=token, db=db_session)


# тест: токен с sub=None вызывает 401
def test_get_current_user_sub_none_unit(db_session):
    token = jwt.encode({"sub": None}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    with pytest.raises(HTTPException):
        get_current_user(token=token, db=db_session)


# тест: пользователь отсутствует в БД -> 401
def test_get_current_user_user_missing_unit(db_session):
    token = jwt.encode(
        {"sub": "ghost@example.com"}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    with pytest.raises(HTTPException):
        get_current_user(token=token, db=db_session)


# тест: успешное получение юзера из БД
def test_get_current_user_success_unit(db_session):
    user = User(
        email="user@example.com", hashed_password=hash_password("123"), role="user"
    )
    db_session.add(user)
    db_session.commit()

    token = jwt.encode(
        {"sub": user.email}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    result = get_current_user(token=token, db=db_session)
    assert result.email == user.email


# ---------- Unit-тесты require_admin ----------
# тест: require_admin падает, если роль не admin
def test_require_admin_forbidden_unit():
    user = User(id=1, email="simple@example.com", hashed_password="123", role="user")
    with pytest.raises(HTTPException) as e:
        require_admin(current_user=user)
    assert e.value.status_code == 403


# тест: require_admin пропускает admin
def test_require_admin_success_unit():
    admin = User(id=1, email="admin@example.com", hashed_password="123", role="admin")
    result = require_admin(current_user=admin)
    assert result == admin


# ---------- Unit-тесты require_user ----------
# тест: require_user падает, если роль "guest"
def test_require_user_forbidden_unit():
    guest = User(id=1, email="guest@example.com", hashed_password="123", role="guest")
    with pytest.raises(HTTPException) as e:
        require_user(current_user=guest)
    assert e.value.status_code == 403


# тест: require_user пропускает "user"
def test_require_user_success_user_unit():
    u = User(id=2, email="user@example.com", hashed_password="123", role="user")
    assert require_user(current_user=u) == u


# тест: require_user пропускает "admin"
def test_require_user_success_admin_unit():
    a = User(id=3, email="admin@example.com", hashed_password="123", role="admin")
    assert require_user(current_user=a) == a


# ---------- Repr ----------
# тест: строковое представление Task
def test_task_repr():
    task = Task(id=1, description="Test", completed=False, user_id=1)
    assert "[1] Test" in repr(task)


# тест: строковое представление User
def test_user_repr():
    user = User(id=1, email="user@example.com", hashed_password="xxx", role="user")
    assert "[1] user@example.com" in repr(user)
