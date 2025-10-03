# tests/conftest.py

import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app import Base
from app.api import app
from app.dependencies import get_db
from app.models import User
from app.utils.security import hash_password

# Загружаем переменные окружения
load_dotenv(".env.test")
DATABASE_URL = os.environ["DATABASE_URL"]

# Создаём движок SQLAlchemy для тестовой базы
TEST_ENGINE = create_engine(DATABASE_URL, poolclass=NullPool)

# Сессия для тестов
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=TEST_ENGINE,
)


# ------------------------------------------------------------------
# 1️⃣ Подготовка базы (создаём все таблицы один раз на сессию)
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    # drop_all безопасно вызывает после всех тестов
    Base.metadata.drop_all(bind=TEST_ENGINE)


# ------------------------------------------------------------------
# 2️⃣ Сессия на каждый тест (rollback после теста)
@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


# ------------------------------------------------------------------
# Чистим БД
@pytest.fixture(autouse=True)
def clean_db(db_session):
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


# ------------------------------------------------------------------
# 3️⃣ Админ-пользователь
@pytest.fixture
def admin_user(db_session):
    user = User(
        email="admin@example.com", hashed_password=hash_password("123"), role="admin"
    )
    db_session.add(user)
    db_session.commit()
    return user


# ------------------------------------------------------------------
# 4️⃣ Подмена get_db для FastAPI
@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


# ------------------------------------------------------------------
# 5️⃣ Синхронный клиент FastAPI
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
