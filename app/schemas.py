# app/schemas.py

from enum import Enum
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, EmailStr, field_validator
from pydantic.config import ConfigDict
from pydantic.fields import Field


# 🎭 Роли
class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"


# 📥 Входные данные для регистрации
class UserCreate(BaseModel):
    username: EmailStr
    password: str


# 📤 Пользователь для вывода
class UserOut(BaseModel):
    email: str

    model_config = ConfigDict(from_attributes=True)


# 📤 Задача — ответ API
class TaskOut(BaseModel):
    id: int
    description: str
    completed: bool
    user_id: int
    user: UserOut

    model_config = ConfigDict(from_attributes=True)


# 🔧 Generic тип для пагинации
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    count: int
    items: List[T]


# 📥 Создание задачи
class TaskCreate(BaseModel):
    description: str = Field(min_length=1)

    @field_validator("description")
    def validate_desc(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Описание задачи не может быть пустым")
        return v


# 📥 Частичное обновление задачи
class TaskUpdate(BaseModel):
    description: Optional[str] = None
    completed: Optional[bool] = None

    @field_validator("description")
    def validate_description(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Description cannot be blank")
        return v


# 📥 Обновление только description
class TaskOnlyUpdate(BaseModel):
    description: str = Field(min_length=1)

    @field_validator("description")
    def validate_desc(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Описание задачи не может быть пустым")
        return v


# 📥 Логин
class LoginSchema(BaseModel):
    username: EmailStr
    password: str


# 📤 Токены
class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


# 📥 Обновление refresh токена
class RefreshTokenRequest(BaseModel):
    refresh_token: str


# 📤 Ответ о пользователе
class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    # позволяет работать с ORM-моделью User напрямую
    model_config = ConfigDict(from_attributes=True)
