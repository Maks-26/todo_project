# app/schemas.py
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, validator
from pydantic.config import ConfigDict
from pydantic.fields import Field


# 🎭 Перечисление ролей
class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"


class UserCreate(BaseModel):
    username: EmailStr
    password: str


# Выдача с БД
class UserOut(BaseModel):
    email: str
    model_config = ConfigDict(from_attributes=True)


class TaskOut(BaseModel):
    id: int
    description: str
    completed: bool
    user_id: int
    user: UserOut
    model_config = ConfigDict(from_attributes=True)


# добавление задачи
class TaskCreate(BaseModel):
    description: Annotated[str, Field(min_length=1, strip_whitespace=True)]
    model_config = ConfigDict(from_attributes=True)

    @validator("description")
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError("Описание задачи не может быть пустым")
        return v.strip()


# изменение статуса и задачи
class TaskUpdate(BaseModel):
    description: Optional[str] = None
    completed: Optional[bool] = None

    @validator("description")
    def not_blank(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Description cannot be blank")
        return v


# изменение задачи
class TaskOnlyUpdate(BaseModel):
    description: Annotated[str, Field(min_length=1, strip_whitespace=True)]


class LoginSchema(BaseModel):
    username: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    model_config = ConfigDict(
        from_attributes=True
    )  # позволяет работать с ORM-моделью User напрямую
