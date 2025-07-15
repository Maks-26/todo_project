from sqlalchemy import Boolean, Column, Integer, String

from app import Base

"""Модель таблицы Task"""


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    completed = Column(Boolean, default=False)

    def __repr__(self):

        return f"[{self.id}], {self.description}, {self.completed}"
