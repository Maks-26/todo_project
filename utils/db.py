import sqlite3

# Создаёт сам файл
def create_table():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


# Добовляет задачу
def add_task(description):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
    conn.commit()
    conn.close()
    print("Задача добавлена.")


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
def update_task_description( task_id, new_description):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = c.fetchone()

    if not task:
        print(f"Задача с ID {task_id} не найдена.")
        return

    c.execute("UPDATE tasks SET description = ? WHERE id = ?", (new_description, task_id))
    conn.commit()
    print(f"Задача ID {task_id} обновлена.")


# отмечаем задачю как выполненную. 
def complete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    print(f"Задача {task_id} отмечена как выполненная.")
 

# Удаление столбца
def delete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    print(f"Задача {task_id} удалена.")
 

# Поиск по ключевому слову
def search_tasks(keyword):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT id, description, completed FROM tasks WHERE description LIKE ?", (f"%{keyword}%",))
    tasks = c.fetchall()
    conn.close()

    if tasks:
        for task in tasks:
            status = "✔" if task[2] else "✘"
            print(f"[{task[0]}] {task[1]} {status}")
    else:
        print("Ничего не найдено.")




