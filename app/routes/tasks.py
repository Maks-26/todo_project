# app/routes/tasks.py

from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_user
from app.models import User
from app.schemas import TaskCreate, TaskOnlyUpdate, TaskOut, TaskUpdate
from app.services import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    search_tasks,
    task_and_status,
    update_task_description,
)

router = APIRouter()


# получить все задачи
@router.get("/tasks", response_model=List[TaskOut])
def get_tasks(
    db: Session = Depends(get_db), current_user: User = Depends(require_user)
):
    tasks = list_tasks(db, current_user)
    return tasks


# добавить задачу
@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    new_task = add_task(db, task.description, current_user)
    return new_task


# Изменить задачу и статус
@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task_and_status(
    task_id: int,
    task_data: TaskUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    result = task_and_status(
        db, task_id, task_data.description, task_data.completed, current_user
    )
    return result


# Изменить задачу
@router.patch("/tasks/{task_id}/description", response_model=TaskOut)
def update_task(
    task_id: int,
    task_data: TaskOnlyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    result = update_task_description(db, task_id, task_data.description, current_user)
    return result


# Завершить задачу
@router.patch("/tasks/{task_id}/complete", response_model=TaskOut)
def finish_a_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    result = complete_task(db, task_id, current_user)
    return result


# Поиск по ключу
@router.get("/tasks/search", response_model=List[TaskOut])
def search_tasks_keyword(
    keyword: Optional[str] = Query(None, description="Ключевое слово для поиска"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    if keyword is None or not keyword.strip():
        raise HTTPException(
            status_code=400, detail="Ключевое слово не может быть пустым"
        )

    return search_tasks(db, keyword, current_user)


# Удалить задачу
@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_api(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    result = delete_task(db, task_id, current_user)
    return result
