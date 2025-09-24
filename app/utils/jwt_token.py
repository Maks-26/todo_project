# app/utils/jwt_token.py — создание токена

from datetime import UTC, datetime, timedelta
from typing import cast

from jose import jwt

from settings import get_settings

settings = get_settings()


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=30)

    to_encode.update({"exp": expire})
    return cast(
        str, jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    )


# Старый стиль
"""
expire = datetime.utcnow() + timedelta(
    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
)
"""
