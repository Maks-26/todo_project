# 1. Базовый образ Python
FROM python:3.13-slim

# 2. Устанавливаем зависимости для Poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# 3. Рабочая директория внутри контейнера
WORKDIR /app

# 4. Копируем только файлы конфигурации Poetry
COPY pyproject.toml poetry.lock* ./

# 5. Устанавливаем зависимости через Poetry (без виртуального окружения)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# 6. Копируем весь проект
COPY . .

# 7. Команда запуска
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
