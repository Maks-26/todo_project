import logging

# Настройка логгера
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


def log_action(action, task_id=None, description=None, completed=None):
    parts = [f"Действие: {action}"]
    if task_id is not None:
        parts.append(f"ID: {task_id}")
    if completed is not None:
        parts.append(f"Статус: {completed}")
    if description:
        parts.append(f"Задача: {description}")
    message = ", ".join(parts)
    logging.info(message)
