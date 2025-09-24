# app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from settings import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
