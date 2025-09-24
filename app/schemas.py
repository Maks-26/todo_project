# app/schemas.py
from enum import Enum
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict


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


# изменение статуса и задачи
class TaskUpdate(BaseModel):
    description: Annotated[
        Optional[str], Field(min_length=1, strip_whitespace=True)
    ] = None
    completed: Optional[bool] = None


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


"""
class UserBase(BaseModel):
    email: EmailStr
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
"""
