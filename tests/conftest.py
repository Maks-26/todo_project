# tests/conftest.py — ФИНАЛЬНАЯ ВЕРСИЯ (30/30)

# ruff: noqa: E402

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

IN_DOCKER = os.getenv("DOCKER_ENV") == "true"
DB_URL = (
    "postgresql+psycopg2://test_user:test_pass@db_test:5432/test_db"
    if IN_DOCKER
    else "postgresql+psycopg2://test_user:test_pass@localhost:5435/test_db"
)

"""
def override_settings():
    from pydantic_settings import BaseSettings

    class TestSettings(BaseSettings):
        DATABASE_URL: str = DB_URL
        SECRET_KEY: str = "test-secret-2025"
        ALGORITHM: str = "HS256"

    return TestSettings()
"""

from app.api import app
from app.db import Base, get_db
from app.models import User
from app.utils.security import hash_password

# app.dependency_overrides[get_settings] = override_settings

engine = create_engine(DB_URL, pool_pre_ping=True, future=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Session:
    session = TestingSessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


# Чисти БД только где нужно (не autouse!)
@pytest.fixture
def clean_db(db_session: Session):
    # Чистим ДО теста — ГАРАНТИРОВАННО чистая БД
    db_session.execute(
        text(
            """
        TRUNCATE TABLE refresh_tokens, tasks, users
        RESTART IDENTITY CASCADE;
    """
        )
    )
    db_session.commit()

    yield  # ← тест стартует с 100% чистой БД

    # Чистим ещё раз ПОСЛЕ — чтобы следующий тест не словил мусор
    db_session.execute(
        text(
            """
        TRUNCATE TABLE refresh_tokens, tasks, users
        RESTART IDENTITY CASCADE;
    """
        )
    )
    db_session.commit()


@pytest.fixture(autouse=True)
def override_get_db(db_session: Session):
    def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def admin_user(db_session: Session):
    """Создаёт администратора в БД и возвращает его"""
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("admin123"),
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c
