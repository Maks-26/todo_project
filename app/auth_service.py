# app/auth_service.py

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import RefreshToken, User
from app.settings import get_settings

UTC = timezone.utc


def create_refresh_token(db: Session, user: User) -> str:
    settings = get_settings()
    token = secrets.token_urlsafe(32)

    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshToken(user_id=user.id, token=token, expires_at=expires_at)

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token.token


def verify_refresh_token(db: Session, token: str) -> User | None:
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not db_token:
        return None

    # Сравниваем сразу с aware datetime
    if db_token.expires_at < datetime.now(UTC):
        db.delete(db_token)
        db.commit()
        return None

    return db_token.user


def revoke_refresh_token(db: Session, token: str):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()

    if db_token:
        db.delete(db_token)
        db.commit()
