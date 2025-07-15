from .db import Base, SessionLocal, init_db
from .models import Task
from .tasks import (
    add_task,
    complete_task,
    delete_task,
    get_task_id,
    list_tasks,
    search_tasks,
    update_task_description,
)

__all__ = [
    "Base",
    "SessionLocal",
    "init_db",
    "Task",
    "add_task",
    "complete_task",
    "delete_task",
    "get_task_id",
    "list_tasks",
    "search_tasks",
    "update_task_description",
]


menu = (
    "Меню:\n"
    "1. Добавить задачу\n"
    "2. Показать список задач\n"
    "3. Изменить задачу\n"
    "4. Отметить задачу выполненной\n"
    "5. Удалить задачу\n"
    "6. Поиск задач\n"
    "7. Выход 👉\n"
    "Ввод: "
)
message = "\nИли введите Enter для отмены.\nВвод: "
