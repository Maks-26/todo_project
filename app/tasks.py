from sqlalchemy.orm import Session

from app import Task
from utils import log_action


# Добавить задачу
def add_task(session: Session, description):
    description = description.strip()

    if not description:
        return "Нельзя добавить пустую задачу."

    task = Task(description=description)
    session.add(task)
    session.commit()

    if task:
        state = "✔" if task.completed else "✘"
        log_action("Задача добавлена", task.id, task.description, state)
        return "Задача добавлена."


# Показать все задачи
def list_tasks(session: Session):
    tasks = session.query(Task).all()
    return tasks if tasks else []


# Изменить задачу
def update_task_description(session: Session, task_id: int, new_description: str):
    new_description = new_description.strip()

    if not new_description:
        return "Нельзя добавить пустую задачу."

    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        task.description, task.completed = new_description, False
        session.commit()
        log_action("Задача обновлена", task.id, task.description, "✘")
        return "Задача обновлена."
    return "Задача с таким ID не найдена."


# Отметить задачу как выполненную
def complete_task(session: Session, task_id: int):
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        task.completed = True
        session.commit()
        log_action("Задача отмечена выполненной", task.id, task.description, "✔")
        return "Задача отмечена выполненной"
    return f"Задача с ID {task_id} не найдена."


# Удолить задачю
def delete_task(session: Session, task_id: int):
    task = session.query(Task).filter(Task.id == task_id).first()
    if task:
        session.delete(task)
        session.commit()
        state = "✔" if task.completed else "✘"
        log_action("Задача удалена", task.id, task.description, state)
        return "Задача удалена"
    return f"Задача с ID {task_id} не найдена."


# Поиск по ключевому слову
def search_tasks(session: Session, keyword: str):
    keyword = f"%{keyword}%"
    tasks = session.query(Task).filter(Task.description.ilike(keyword)).all()
    return tasks


# Проверить ввод get_task_id
def get_task_id(prompt="Введите ID задачи: \nВвод: "):
    try:
        task_id = input(f"Введите Enter - 'Отмена'\n{prompt}")
        if not task_id:
            return "Отмена"
        return int(task_id)
    except ValueError:
        return "Ошибка: ID должен быть числом."
