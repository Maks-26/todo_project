import unittest
import sqlite3
from app import add_task, complete_task, delete_task, create_table

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

    def add_and_get_task_id(self, description):
        """Добавить задачу и вернуть её ID"""
        add_task(description)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM tasks WHERE description = ?", (description,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    def get_task_by_id(self, task_id):
        """Получить задачу по ID"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()
        conn.close()
        return task

    def get_completed_status(self, task_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None

    def test_add_task(self):
        task_id = self.add_and_get_task_id("Тестовая задача")
        self.assertIsNotNone(task_id, "Задача не была добавлена")

    def test_complete_task(self):
        task_id = self.add_and_get_task_id("Задача для выполнения")
        self.assertIsNotNone(task_id, "Задача не найдена после добавления")

        complete_task(task_id)
        status = self.get_completed_status(task_id)
        self.assertEqual(status, 1, "Задача не была помечена как выполненная")

    def test_delete_task(self):
        task_id = self.add_and_get_task_id("Задача для удаления")
        self.assertIsNotNone(task_id, "Задача не найдена после добавления")

        delete_task(task_id)
        task = self.get_task_by_id(task_id)
        self.assertIsNone(task, "Задача не была удалена")

if __name__ == "__main__":
    import unittest

    unittest.main()
