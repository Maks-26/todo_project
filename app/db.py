import sqlite3

from utils import log_action


# Потклюкение к БД
def get_connection():
    return sqlite3.connect("tasks.db")


# Создаёт сам файл
def create_table():
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    completed INTEGER DEFAULT 0
                )
            """
            )
            conn.commit()
        log_action("Таблица успешно создана.")
    except Exception as e:
        log_action(f"Произошла ошибка при создании таблицы: {e}")
