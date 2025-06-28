from app import (
    add_task,
    complete_task,
    create_table,
    delete_task,
    get_task_id,
    list_tasks,
    search_tasks,
    update_task_description,
)


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
            print(add_task(task))

        # Показать список задач
        elif choice == "2":
            My_list_tasks = list_tasks() if list_tasks() else ["Список пуст"]
            for task in My_list_tasks:
                print(task)

        # Изменить задачу
        elif choice == "3":
            task_id = get_task_id("Введите ID, которую хотите изменить: ")
            if task_id == "Некорректный ID" or task_id == "Отмена":
                print(task_id)
                continue
            new_description = input("Введите новое описание задачи: ")
            print(update_task_description(task_id, new_description))

        # Отметить задачу выполненной
        elif choice == "4":
            task_id = get_task_id()
            if task_id == "Некорректный ID" or task_id == "Отмена":
                print(task_id)
                continue
            print(complete_task(task_id))

        # Удалить задачу:
        elif choice == "5":
            task_id = get_task_id("Введите ID задачи для удаления: ")
            if task_id == "Некорректный ID" or task_id == "Отмена":
                print(task_id)
                continue
            print(delete_task(task_id))

        # Выход
        elif choice == "6":
            print("До свидания!")
            break

        # # Поиск по ключевому слову
        elif choice == "7":
            keyword = input("Введите слово для поиска: ")
            print(search_tasks(keyword))

        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()


