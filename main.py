from app import (add_task, complete_task, create_table, delete_task,
                 list_tasks, update_task_description)


def main():
    create_table()
    while True:
        print("\nМеню:")
        print("1. Добавить задачу")
        print("2. Показать список задач")
        print("3. Изменить задачу")
        print("4. Отметить задачу выполненной")
        print("5. Удалить задачу")
        print("6. Выход")
        print("7. Поиск задач")

        choice = input("Выберите действие: ")

        # Добавить задачу
        if choice == "1":
            task = input("Введите задачу: ")
            add_task(task)

        # Показать список задач
        elif choice == "2":
            list_tasks()

        # Изменить задачу
        elif choice == "3":
            task_id = int(input("Введите ID задачи, которую хотите изменить: "))
            new_description = input("Введите новое описание задачи: ")
            update_task_description(task_id, new_description)

        # Отметить задачу выполненной
        elif choice == "4":
            try:
                task_id = int(input("Введите ID задачи для отметки как выполненной: "))
                complete_task(task_id)
            except ValueError:
                print("Введите корректный ID.")

        # Удалить задачу:
        elif choice == "5":
            try:
                task_id = input(
                    "Введите ID задачи для удаления:\n" "Введите Enter для отмены:"
                )
                delete_task(int(task_id)) if task_id else print("Отмена")
            except ValueError:
                print("Введите корректный ID.")

        # Выход
        elif choice == "6":
            print("До свидания!")
            break

        # # Поиск по ключевому слову
        elif choice == "7":
            keyword = input("Введите слово для поиска: ")
            search_tasks(keyword)

        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()
