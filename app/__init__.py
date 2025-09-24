from .db import Base, SessionLocal
from .models import Task, User

__all__ = ["Base", "SessionLocal", "Task", "User"]


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
