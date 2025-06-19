import unittest
from utils import add_task

class TestTodoApp(unittest.TestCase):
    def test_add_task(self):
        # add_task() возвращает None, поэтому проверим, что не выбрасывает исключение
        self.assertIsNone(add_task("Тестовая задача"))

if __name__ == '__main__':
    unittest.main()
