import sqlite3  # noqa: F401
import unittest

from app import (add_task, complete_task, create_table, delete_task, get_connection,
update_task_description, search_tasks)

class TestTodoApp(unittest.TestCase):
    
    def setUp(self):
        """Перед каждым тестом очищаем таблицу и создаём заново."""
        create_table()
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM tasks")
            conn.commit()
    
    def add_and_get_task_id(self, description):
        """Добавить задачу и вернуть её ID"""
        add_task(description)
        with get_connection() as conn:
            c = conn.cursor()
            query = """
                SELECT id
                FROM tasks
                WHERE description = ?
            """
            c.execute(query.strip(), (description,))
            result = c.fetchone()
            return result[0] if result else None

    def get_task_by_id(self, task_id):
        """Получить задачу по ID"""
        with get_connection() as conn:
            c = conn.cursor()
            query = """
                SELECT *
                FROM tasks
                WHERE id = ?
            """
            c.execute(query.strip(), (task_id,))
            task = c.fetchone()
            return task

    def get_completed_status(self, task_id):
        """Изменить статус задачи"""
        with get_connection() as conn:
            c = conn.cursor()
            query = """
                SELECT completed
                FROM tasks
                WHERE id = ?
            """
            c.execute(query.strip(), (task_id,))
            result = c.fetchone()
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

    def test_update_task_description(self):
        task_id = self.add_and_get_task_id("Старая задача")

        new_text = "Обновлённая задача"
        update_task_description(task_id, new_text)

        updated_task = self.get_task_by_id(task_id)
        self.assertEqual(updated_task[1], new_text)
        self.assertEqual(updated_task[2], 0)  # completed должен быть сброшен

    def test_search_tasks(self):

        self.add_and_get_task_id("Купить молоко")
        self.add_and_get_task_id("Позвонить маме")
        
        result = search_tasks("молоко")
        self.assertIn("молоко", result.lower())


if __name__ == "__main__":
    import unittest

    unittest.main()
