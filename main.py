import argparse

from app import SessionLocal  # init_db
from app.tasks import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    search_tasks,
    update_task_description,
)


def main():
    # init_db()
    parser = argparse.ArgumentParser(description="TODO CLI")

    subparsers = parser.add_subparsers(dest="command")

    # Команда: add
    add_parser = subparsers.add_parser("add", help="Добавить задачу")
    add_parser.add_argument("description", help="Описание задачи")

    # Команда: list
    subparsers.add_parser("list", help="Показать все задачи")

    # Команда: update
    update_parser = subparsers.add_parser("update", help="Обновить задачу")
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("description", help="Новое описание")

    # Команда: complete
    complete_parser = subparsers.add_parser("complete", help="Отметить как выполненную")
    complete_parser.add_argument("id", type=int)

    # Команда: delete
    delete_parser = subparsers.add_parser("delete", help="Удалить задачу")
    delete_parser.add_argument("id", type=int)

    # Команда: search
    search_parser = subparsers.add_parser("search", help="Поиск по описанию")
    search_parser.add_argument("keyword", help="Ключевое слово")

    args = parser.parse_args()
    with SessionLocal() as session:
        match args.command:
            # Добавить задачу
            case "add":
                answer = add_task(session, args.description)
                if answer:
                    print("Задача добавлена.")
                else:
                    print("Нельзя добавить пустую задачу.")
            # Показать список задач
            case "list":
                result = list_tasks(session)
                if result:
                    for task in result:
                        state = "✔" if task.completed else "✘"
                        print(f"{task.id}. {task.description} [{state}]")
                else:
                    print("Список задач пуст.")
            # Изменить задачу
            case "update":
                result = update_task_description(session, args.id, args.description)
                if isinstance(result, str):
                    print(result)
                elif result is None:
                    print("Нельзя добавить пустую задачу.")
                else:
                    print("Задача обновлена.")
            # Отметить выполнненой
            case "complete":
                result = complete_task(session, args.id)
                if isinstance(result, str):
                    print(result)
                else:
                    print("Задача отмечена выполненной")
            # Удалить
            case "delete":
                result = delete_task(session, args.id)
                if result:
                    print(result)
                else:
                    print("Задача удалена")
            # Поиск по ключу
            case "search":
                result = search_tasks(session, args.keyword)
                if result:
                    for task in result:
                        state = "✔" if task.completed else "✘"
                        print(f"{task.id}. {task.description} [{state}]")
                else:
                    print("Ничего не найдено.")
            case _:
                parser.print_help()


if __name__ == "__main__":
    main()
