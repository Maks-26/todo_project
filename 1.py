# generate_user_sqlalchemy.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import User
from app.utils.security import hash_password


def create_test_user(email: str, password: str, role: str = "user") -> list[str]:
    db: Session = SessionLocal()
    try:
        # проверим, есть ли такой пользователь
        existing_user: User | None = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
        if existing_user:
            print(f"❌ Пользователь {email} уже существует")
        else:
            # создаём нового
            new_user = User(
                email=email, hashed_password=hash_password(password), role=role
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(
                f"✅ Пользователь создан: {new_user.email},"
                f" id={new_user.id}, role={new_user.role}"
            )

        # возвращаем список всех email
        all_emails: list[str] = list(db.execute(select(User.email)).scalars().all())
        return all_emails
    finally:
        db.close()


def create_test_all_user(email: str, password: str, role: str = "user") -> list[str]:
    db: Session = SessionLocal()
    try:
        existing = list(db.execute(select(User.email)).scalars().all())
        return existing
    finally:
        db.close()


if __name__ == "__main__":
    all_name = create_test_all_user("test@example2.com", "password123", role="admin")
    for name in all_name:
        print(name)
