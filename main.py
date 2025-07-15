import argparse

from app import (
    SessionLocal,
    add_task,
    complete_task,
    delete_task,
    init_db,
    list_tasks,
    search_tasks,
    update_task_description,
)


def main():
    init_db()
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
    session = SessionLocal()

    match args.command:
        case "add":
            print(add_task(session, args.description))
        case "list":
            result = list_tasks(session)
            if result:
                for task in result:
                    state = "✔" if task.completed else "✘"
                    print(f"{task.id}. {task.description} [{state}]")
            else:
                print("Список задач пуст.")
        case "update":
            print(update_task_description(session, args.id, args.description))
        case "complete":
            print(complete_task(session, args.id))
        case "delete":
            print(delete_task(session, args.id))
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
