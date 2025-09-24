from app.models import Task, User


# тестируем модель
def test_task_repr():
    task = Task(id=1, description="Test", completed=False, user_id=1)
    assert "[1] Test" in repr(task)


def test_user_repr():
    user = User(id=1, email="user@example.com", hashed_password="xxx", role="user")
    assert "[1] user@example.com" in repr(user)
