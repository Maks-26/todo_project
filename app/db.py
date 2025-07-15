from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

"""Настройка SQLAlchemy"""
DATABASE_URL = "sqlite:///tasks.db"

engine = create_engine(DATABASE_URL, echo=False)  # Подключение к БД
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

"""Создание таблиц"""


def init_db():
    from app import Task  # noqa: F401 # Импортировать все модели

    Base.metadata.create_all(bind=engine)
