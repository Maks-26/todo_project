# маршруты для регистрации и логина
# app/routes/auth.py — Эндпоинт /login

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import authenticate_user
from app.dependencies import get_current_user, get_db
from app.models import User
from app.schemas import RoleEnum, Token, UserCreate, UserResponse
from app.services import create_user
from app.utils.jwt_token import create_access_token
from utils.logger import log_error, log_info

router = APIRouter()


# 🔐 Регистрация
@router.post("/register", response_model=Token)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    role: RoleEnum = Query(
        RoleEnum.user,
        description=(
            "Выберите роль пользователя:\n"
            "- **user** — обычный пользователь,"
            " может только управлять своими задачами\n"
            "- **admin** — администратор, имеет доступ к задачам всех пользователей"
        ),
    ),
):
    try:
        user = create_user(db, user_data, role)
        log_info(
            f"✅ Успешная регистрация пользователя: {user.email} с ролью {user.role}"
        )
    except ValueError as e:
        log_error(f"❌ Ошибка регистрации: email '{user_data.username}' уже существует")
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# 🔑 Логин (совместим с OAuth2PasswordRequestForm)
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if isinstance(user, str):
        log_error(f"❌ Неудачная попытка входа: {user}")
        raise HTTPException(status_code=401, detail=user)

    token = create_access_token({"sub": user.email})
    log_info(f"✅ Пользователь вошёл в систему: {user.email}")
    return {"access_token": token, "token_type": "bearer"}


# 👤 Текущий пользователь
@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
