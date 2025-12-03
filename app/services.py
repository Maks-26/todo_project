# app/services.py
from typing import List, Optional, Tuple

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Task, User
from app.schemas import RoleEnum, UserCreate
from app.utils.security import hash_password


# добавление пользователя
def create_user(
    db: Session, user_data: UserCreate, role: RoleEnum = RoleEnum.user
) -> User:
    existing_user = db.execute(
        select(User).where(User.email == user_data.username)
    ).scalar_one_or_none()
    if existing_user:
        raise ValueError("Пользователь с таким email уже существует")
    hashed_pw = hash_password(user_data.password)
    db_user = User(
        email=user_data.username, hashed_password=hashed_pw, role=role
    )  # type: ignore
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Показать все задачи
def list_tasks(
    db: Session,
    user: User,
    skip: int = 0,
    limit: int = 10,
    completed: Optional[bool] = None,
    search: Optional[str] = None,
) -> Tuple[List[Task], int]:
    """
    Возвращает задачи + общее количество (для пагинации на фронтенде)
    """
    query = select(Task).options(joinedload(Task.user))

    # 1️⃣ Если не админ — показываем только свои задачи
    if user.role != "admin":
        query = query.where(Task.user_id == user.id)

    # 2️⃣ Фильтрация по выполненности
    if completed is not None:
        query = query.filter(Task.completed == completed)

    # 3️⃣ Поиск по названию
    if search:
        query = query.filter(Task.description.ilike(f"%{search}%"))

    # 4️⃣ Общее количество (до лимита/offset)
    total = db.scalar(select(func.count()).select_from(query.subquery()))

    # 5️⃣ Пагинация
    query = query.offset(skip).limit(limit)

    # 6️⃣ Получаем список задач
    tasks = db.execute(query).scalars().all()

    tasks_list = list(tasks)
    return tasks_list, int(total or 0)


# Добавить задачу
def add_task(
    db: Session,
    new_description: str,
    user: User,
) -> Task:
    new_task = Task(
        description=new_description.strip(),
        user_id=user.id,
    )  # type: ignore
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    new_task.user = user
    return new_task


# Найти задачу:
def find_task(db: Session, task_id: int, user: User) -> Task:
    task = db.execute(select(Task).where(Task.id == task_id)).scalar_one_or_none()
    if not task:
        detail = f"Задача {task_id} не найдена"
        raise HTTPException(status_code=404, detail=detail)
    if user.role == "admin" or task.user_id == user.id:
        return task
    detail = f"Задача {task_id} не принадлежит пользователю"
    raise HTTPException(status_code=403, detail=detail)


# Изменить задачу и статус
def task_and_status(
    db: Session,
    task_id: int,
    new_description: str | None,
    completed: bool | None,
    user: User,
) -> Task:
    task = find_task(db, task_id, user)
    if new_description is not None:
        task.description = new_description.strip()
    if completed is not None:
        task.completed = completed
    db.commit()
    db.refresh(task)
    return task


# Изменить задачу
def update_task_description(
    db: Session, task_id: int, new_description: str, user: User
) -> Task:
    task = find_task(db, task_id, user)
    task.description = new_description.strip()
    db.commit()
    db.refresh(task)
    return task


# Отметить задачу как выполненную
def complete_task(db: Session, task_id: int, user: User) -> Task:
    task = find_task(db, task_id, user)
    task.completed = True
    db.commit()
    db.refresh(task)
    return task


# Удалить задачу
def delete_task(db: Session, task_id: int, user: User) -> Task:
    task = find_task(db, task_id, user)
    db.delete(task)
    db.commit()
    return task


# Поиск по ключу
def search_tasks(
    db: Session,
    keyword: str,
    user: User,
):
    # Проверка существования задач в базе данных
    existing_tasks = db.execute(select(Task)).scalars().first()
    if not existing_tasks:
        detail = "Таблица задач пуста"
        raise HTTPException(status_code=404, detail=detail)

    query = select(Task).where(Task.description.ilike(f"%{keyword}%"))
    # Если не админ — фильтруем по user_id
    if user.role != "admin":
        query = query.where(Task.user_id == user.id)

    tasks = db.execute(query).scalars().all()
    if not tasks:
        detail = f"Задачи с ключом '{keyword}' не найдены"
        raise HTTPException(status_code=404, detail=detail)
    return tasks
