# app/models.py
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(default="user", nullable=False)

    # Список задач пользователя
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user")

    def __repr__(self) -> str:
        return f"[{self.id}] {self.email} ({self.role})"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(nullable=False)
    completed: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Связь с пользователем
    user: Mapped["User"] = relationship("User", back_populates="tasks")

    def __repr__(self) -> str:
        return f"[{self.id}] {self.description}, {self.completed}"
