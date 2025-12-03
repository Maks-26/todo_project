# app/utils/jwt_token.py

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt

from app.settings import get_settings

UTC = timezone.utc


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    settings = get_settings()  # ленивый вызов
    expire = datetime.now(UTC) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }

    return str(jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM))


# Старый стиль
"""
expire = datetime.utcnow() + timedelta(
    minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
)
"""
