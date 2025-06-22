import sqlite3


# Создаёт сам файл
def create_table():
    conn = sqlite3.connect("tasks.db")
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
    conn.close()
