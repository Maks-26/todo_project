# 🧩 Todo Project — FastAPI + PostgreSQL + Docker + Alembic + Poetry

Полнофункциональное приложение для управления задачами (todo) с использованием **FastAPI**, **SQLAlchemy**, **Alembic**, **Docker** и **Poetry**.  
Поддерживает регистрацию, аутентификацию (JWT), CRUD-операции над задачами, логирование и тестирование.

---

Скриншот Swagger UI: 
![Swagger UI](docs/swagger_ui.png)

---

## 🚀 Стек технологий

- 🐍 **Python 3.13**
- ⚡ **FastAPI**
- 🧱 **SQLAlchemy ORM**
- 🔄 **Alembic (миграции БД)**
- 🐘 **PostgreSQL 16**
- 📦 **Poetry (управление зависимостями)**
- 🧪 **Pytest (тесты)**
- 🐳 **Docker / Docker Compose**
- 🧰 **GitHub Actions (CI/CD)**

---

## 📂 Структура проекта

todo_project/
├── app/
│ ├── api.py
│ ├── models.py
│ ├── schemas.py
│ ├── services.py
│ └── ...
├── utils/
│ └── logger.py
├── alembic/
│ ├── versions/
│ └── env.py
├── tests/
│ └── test_tasks.py
├── Dockerfile
├── docker-compose.full.yml
├── docker-compose.db.yml
├── docker-compose.test.yml
├── pyproject.toml
├── alembic.ini
├── .env
├── .env.test
└── README.md

yaml
Копировать код

---

## ⚙️ Установка и запуск

### 🔹 1. Клонировать репозиторий
```bash
git clone https://github.com/your_username/todo_project.git
cd todo_project

🧰 Вариант 1 — Запуск локально (API без Docker)
  1️⃣ Установить зависимости
    poetry install
  2️⃣ Запустить контейнер с БД
    docker-compose -f docker-compose.db.yml up -d
  3️⃣ Применить миграции Alembic
    poetry run alembic upgrade head
  4️⃣ Запустить сервер FastAPI
    poetry run uvicorn app.api:app --reload
    Теперь API доступен по адресу:
    👉 http://127.0.0.1:8000/docs

🧪 Запуск тестов локально
    1 Запустить контейнер с Тестовой БД
      docker compose -f docker-compose.test.yml up -d db_test
    2 Запустить тесты 
      poetry run pytest -v

🐳 Вариант 2 — Полный запуск через Docker
  1️⃣ Запуск проекта целиком
    docker-compose -f docker-compose.full.yml up --build
    После сборки API доступен по адресу:
    👉 http://127.0.0.1:8000/docs
  2️⃣ Применить миграции вручную (если требуется)
    docker exec -it todo_project-api poetry run alembic upgrade head

  🧪 Запуск тестов в Docker
  Отдельный тестовый стенд с собственной базой (test_db).
  1️⃣ Запустить тесты
    docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
  2️⃣ Очистить после тестов
    docker-compose -f docker-compose.test.yml down -v

🧾 Пример .env
  Файл .env.local

  DATABASE_URL=postgresql+psycopg2://myuser:mypassword@localhost:5432/mydb
  SECRET_KEY=supersecret
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  REFRESH_TOKEN_EXPIRE_DAYS = 7   # 7 дней (настраиваемо)

  Файл .env.test.local

  DATABASE_URL=postgresql+psycopg2://test_user:test_pass@localhost:5433/test_db
  SECRET_KEY=testsecret
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  REFRESH_TOKEN_EXPIRE_DAYS = 7   # 7 дней (настраиваемо)

  Файл .env.docker

  DATABASE_URL=postgresql+psycopg2://myuser:mypassword@db:5432/mydb
  ENV_FILE=.env.docker
  SECRET_KEY=supersecret
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  REFRESH_TOKEN_EXPIRE_DAYS = 7   # 7 дней (настраиваемо)

  Файл .env.test.docker

  DATABASE_URL=postgresql+psycopg2://test_user:test_pass@db:5432/test_db
  ENV_FILE_TEST =.env.test.docker
  SECRET_KEY=testsecret
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  REFRESH_TOKEN_EXPIRE_DAYS = 7   # 7 дней (настраиваемо)

⚡ Полезные команды
Команда	Описание
docker ps	Просмотр запущенных контейнеров
docker-compose down	Остановка контейнеров
docker exec -it todo_project-db psql -U myuser -d mydb	Подключение к БД
poetry run alembic revision --autogenerate -m "comment"	Создать миграцию
poetry run alembic upgrade head	Применить все миграции
poetry run pytest -v	Локальный запуск тестов

🌐 API Документация
После запуска API:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

🔁 CI/CD (GitHub Actions)
Файл: .github/workflows/tests.yml

name: Lint and Test

on: [push, pull_request]

jobs:
  lint_and_test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        ports:
          - 5432:5432

    env:
      ENV_FILE_TEST: .env.test.local
      DATABASE_URL: postgresql+psycopg2://test_user:test_pass@localhost:5432/test_db
      SECRET_KEY: testsecret

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Install dependencies for Postgres/psycopg2
        run: sudo apt-get update && sudo apt-get install -y libpq-dev

      - name: Wait for PostgreSQL
        run: |
          for i in {1..10}; do
            pg_isready -h localhost -p 5432 && break
            echo "Waiting for postgres..."
            sleep 2
          done

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Install dependencies
        run: poetry install

      - name: Run Black
        run: poetry run black . --check

      - name: Run Isort
        run: poetry run isort . --check

      - name: Run Ruff
        run: poetry run ruff check .

      - name: Run MyPy
        run: poetry run mypy app

      - name: Run Pytest with Coverage
        run: poetry run pytest --cov=app --cov-report=html

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: htmlcov


✅ Этот workflow автоматически:
  Поднимает PostgreSQL в контейнере
  Устанавливает зависимости
  Применяет миграции
  Запускает тесты

🧹 Очистка
Полностью удалить контейнеры, образы и тома:

docker-compose -f docker-compose.full.yml down -v --rmi all

