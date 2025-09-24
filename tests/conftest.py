# tests/conftest.py

"""
# Для загруски тестовой БД без плагина poetry add --dev pytest-dotenv
import os
from dotenv import load_dotenv

# Явно грузим .env.test
load_dotenv(".env.test")

# Теперь os.environ["DATABASE_URL"] и другие доступны
"""
import os

# tests/conftest.py
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import Base  # общий Base для моделей
from app.api import app  # наш FastAPI-приложение
from app.dependencies import get_db  # оригинальная зависимость доступа к БД

# 1) Создаём engine на основе DATABASE_URL из окружения
load_dotenv(".env.test")
DATABASE_URL = os.environ["DATABASE_URL"]

connect_args = {}
poolclass = None

# Если это SQLite in-memory — нужны специальные параметры
# - check_same_thread=False — разрешает доступ из разных потоков (TestClient)
# - StaticPool — все сессии используют одно и то же подключение (иначе таблицы "исчезнут") # noqa: E501
if DATABASE_URL.startswith("sqlite") and ":memory:" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
    poolclass = StaticPool

elif "test" not in DATABASE_URL:
    raise RuntimeError(f"Refusing to run tests on non-test database: {DATABASE_URL}")

TEST_ENGINE = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    poolclass=poolclass,
)

# Создаём фабрику сессий, привязанную к нашему тестовому engine
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=TEST_ENGINE,
)


# ==========================
# Глобальная настройка БД (один раз на всю сессию тестов)
# ==========================
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():

    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


# ==========================
# Фикстура для отдельного теста: отдаём чистую сессию
# ==========================
@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ==========================
# 6. Переопределяем get_db внутри FastAPI на нашу тестовую сессию
# ==========================
@pytest.fixture(autouse=True)
def override_get_db(db_session):
    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


# 5) Клиент для вызова API внутри тестов
@pytest.fixture
def client():
    # TestClient поднимает ASGI-приложение в тестовом режиме
    with TestClient(app) as c:
        yield c
