from datetime import datetime


def log_action(action, task_id=None, description=None):
    with open("log.txt", "a", encoding="utf-8") as f:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{time}] Действие: {action}"
        if task_id is not None:
            line += f", ID: {task_id}"
        if description:
            line += f", Задача: {description}"
        f.write(line + "\n")
