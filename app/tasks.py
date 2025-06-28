import sqlite3  # noqa: F401

from app import get_connection
from utils import log_action


# Проверка корректности ввода
def get_task_id(prompt="Введите ID задачи:"):
    try:
        task_id = input(f"Введите Enter - 'Отмена'\n{prompt}")
        if not task_id:
            return "Отмена"
        return int(task_id)
    except ValueError:
        return "Некорректный ID"


# 1 Добавляет задачу
def add_task(description):
    if not description.strip():  # пустая строка
        return "Нельзя добавить пустую задачу."
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
        conn.commit()
        log_action("Добавлена задача", description=description)
        return "Задача добавлена"


# 2 Показать все задачи
def list_tasks():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, description, completed FROM tasks")
        tasks = c.fetchall()

    if tasks:
        My_list_tasks = []
        for task in tasks:
            status = "✔" if task[2] else "✘"
            My_list_tasks.append(f"[{task[0]}] {task[1]} {status}")
        return My_list_tasks
    else:
        return tasks


# 3 изменение текста задачи
def update_task_description(task_id, new_description):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()

        if not task:
            return f"Задача с ID {task_id} не найдена."

        query = """
            UPDATE tasks
            SET description = ?, completed = 0
            WHERE id = ?
        """
        c.execute(
            query.strip(),
            (
                new_description,
                task_id,
            ),
        )
        conn.commit()
        log_action("Задача обновлена", task_id=task_id)
    return f"Задача ID {task_id} обновлена."


# 4 отмечаем задачу как выполненную.
def complete_task(task_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        if c.rowcount == 0:
            return f"Задача с ID {task_id} не найдена."
        else:
            log_action("Отмечена как выполненная", task_id=task_id)
            conn.commit()
        return f"Задача {task_id} отмечена как выполненная."


# 5 Удаление столбца
def delete_task(task_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        log_action("Удалена задача", task_id=task_id)
    return f"Задача {task_id} удалена."


# 6 Поиск по ключевому слову
def search_tasks(keyword):
    with get_connection() as conn:
        c = conn.cursor()
        query = """
            SELECT id, description, completed
            FROM tasks
            WHERE description LIKE ?
        """
        c.execute(
            query.strip(),
            (f"%{keyword}%",)
        )
        tasks = c.fetchall()

    if tasks:
        for task in tasks:
            status = "✔" if task[2] else "✘"
            return f"[{task[0]}] {task[1]} {status}"
    else:
        return "Ничего не найдено."
