# test_models.py

from app.models import Task, User


# ------------------ Task ------------------
def test_task_repr():
    """
    Проверяем строковое представление задачи.
    Ожидаем формат "[id] description".
    """
    task = Task(description="Test", user_id=1, completed=False)
    assert "Test" in repr(task)


# ------------------ User ------------------
def test_user_repr():
    """
    Проверяем строковое представление пользователя.
    Ожидаем формат "[id] email".
    """
    user = User(email="user@example.com", hashed_password="xxx", role="user")
    assert "user@example.com" in repr(user)
