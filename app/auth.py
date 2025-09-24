# Проверка входа
# app/auth.py — логика аутентификации
from sqlalchemy.orm import Session

from app.models import User
from app.utils.security import verify_password


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.email == username).first()
    if not user:
        message = f"❌ Пользователь с email {username} не найден"
        return message
    if not verify_password(password, user.hashed_password):
        message = f"❌ {password} Пароль не верный  !!!"
        return message
    return user
