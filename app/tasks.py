import sqlite3

from utils.logger import log_action


# Добовляет задачу
def add_task(description):
    if not description.strip():  # пустая строка
        print("Нельзя добавить пустую задачу.")
        return
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
    conn.commit()
    conn.close()
    print("Задача добавлена.")
    log_action("Добавлена задача", description=description)


# Показать все задачи
def list_tasks():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT id, description, completed FROM tasks")
    tasks = c.fetchall()
    conn.close()

    if tasks:
        for task in tasks:
            status = "✔" if task[2] else "✘"
            print(f"[{task[0]}] {task[1]} {status}")
    else:
        print("Список задач пуст.")


# изменение текста задачи
def update_task_description(task_id, new_description):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = c.fetchone()

    if not task:
        print(f"Задача с ID {task_id} не найдена.")
        return

    c.execute(
        "UPDATE tasks SET description = ? WHERE id = ?", (new_description, task_id)
    )
    conn.commit()
    print(f"Задача ID {task_id} обновлена.")


# отмечаем задачю как выполненную.
def complete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    if c.rowcount == 0:
        print(f"Задача с ID {task_id} не найдена.")
    else:
        print(f"Задача {task_id} отмечена как выполненная.")
        log_action("Отмечена как выполненная", task_id=task_id)
    conn.commit()
    conn.close()


# Удаление столбца
def delete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    print(f"Задача {task_id} удалена.")
    log_action("Удалена задача", task_id=task_id)


# Поиск по ключевому слову
def search_tasks(keyword):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    query = """
        SELECT id, description, completed
        FROM tasks
        WHERE description LIKE ?
            """
    c.execute(
        query.strip(),
        f"%{keyword}%",
    )
    tasks = c.fetchall()
    conn.close()

    if tasks:
        for task in tasks:
            status = "✔" if task[2] else "✘"
            print(f"[{task[0]}] {task[1]} {status}")
    else:
        print("Ничего не найдено.")
