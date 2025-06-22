import sqlite3
import unittest

from app import add_task, complete_task, create_table, delete_task

DB_PATH = "tasks.db"


class TestTodoApp(unittest.TestCase):
    def setUp(self):
        """Перед каждым тестом очищаем таблицу и создаём заново."""
        create_table()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()

    def test_add_task(self):
        add_task("Тестовая задача")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE description = ?", ("Тестовая задача",))
        task = c.fetchone()
        conn.close()
        self.assertIsNotNone(task, "Задача не была добавлена в БД")

    def test_complete_task(self):
        add_task("Задача для выполнения")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT id FROM tasks WHERE description = ?", ("Задача для выполнения",)
        )
        result = c.fetchone()
        self.assertIsNotNone(result, "Задача не найдена в БД после добавления")
        task_id = result[0]

        complete_task(task_id)
        c.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
        status_result = c.fetchone()
        conn.close()
        self.assertIsNotNone(status_result, "Статус задачи не найден после выполнения")
        self.assertEqual(status_result[0], 1, "Задача не была помечена как выполненная")

    def test_delete_task(self):
        add_task("Задача для удаления")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "SELECT id FROM tasks WHERE description = ?", ("Задача для удаления",)
        )
        result = c.fetchone()
        self.assertIsNotNone(result, "Задача не найдена в БД после добавления")
        task_id = result[0]

        delete_task(task_id)
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()
        conn.close()
        self.assertIsNone(task, "Задача не была удалена")

    def test_add_empty_task(self):
        """Проверка добавления пустой задачи"""
        add_task("")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE description = ''")
        task = c.fetchone()
        conn.close()
        self.assertIsNone(task, "Пустая задача не должна быть добавлена")

    def test_complete_nonexistent_task(self):
        """Попытка завершить несуществующую задачу"""
        complete_task(9999)  # ID, которого точно нет
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id = 9999")
        task = c.fetchone()
        conn.close()
        self.assertIsNone(task, "Не должно быть задачи с ID 9999")


if __name__ == "__main__":
    import unittest

    unittest.main()
