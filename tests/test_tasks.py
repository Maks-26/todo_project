# tests/test_tasks.py
from app import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    search_tasks,
    update_task_description,
)


def test_add_task(test_session):
    """Проверяю добовление задачи"""
    description = ["Тестовая задача", "   ", "Новая задача"]
    message = add_task(test_session, description[0])
    empty_message = add_task(test_session, description[1])

    assert "Задача добавлена." in message
    assert "Нельзя добавить пустую задачу." in empty_message

    """Проверяю сохранение задачи"""
    tasks = list_tasks(test_session)
    assert len(tasks) == 1
    assert tasks[0].id == 1
    assert tasks[0].description == description[0]
    assert tasks[0].completed is False

    """Меняю статус задачи"""
    complete = complete_task(test_session, 1)
    tasks = list_tasks(test_session)
    assert "Задача отмечена выполненной" == complete
    assert tasks[0].completed is True

    """Проверяю изменения задачи"""
    update_task = update_task_description(test_session, 1, description[2])
    empty_update_task = update_task_description(test_session, 1, description[1])
    tasks = list_tasks(test_session)
    assert "Задача обновлена." == update_task
    assert "Нельзя добавить пустую задачу." == empty_update_task
    assert tasks[0].completed is False

    """Поиск по ключевому слову"""
    tasks = search_tasks(test_session, "Новая")
    assert "Новая задача" == tasks[0].description

    """Удаление задачи"""
    tasks = delete_task(test_session, 1)
    assert "Задача удалена" == tasks

    """Финиш"""
    finish = list_tasks(test_session)
    assert [] == finish
