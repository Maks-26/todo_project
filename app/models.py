# app/models.py
"""
from dataclasses import dataclass, field
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, registry

mapper_registry: registry = registry()


@mapper_registry.mapped
@dataclass
class User:
    __tablename__ = "users"
    __sa_dataclass_metadata_key__ = "sa"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(default="user", nullable=False)

    tasks: Mapped[List["Task"]] = field(
        default_factory=lambda: [],
        metadata={"sa": relationship("Task", back_populates="user")}
    )


@mapper_registry.mapped
@dataclass
class Task:
    __tablename__ = "tasks"
    __sa_dataclass_metadata_key__ = "sa"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(nullable=False)
    completed: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="tasks")
"""
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

    def __init__(self, email: str, hashed_password: str, role: str = "user") -> None:
        self.email = email
        self.hashed_password = hashed_password
        self.role = role

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

    def __init__(self, description: str, user_id: int) -> None:
        self.description = description
        self.user_id = user_id

    def __repr__(self) -> str:
        return f"[{self.id}] {self.description}, {self.completed}"
