# Dockerfile
FROM python:3.13-slim

# Устанавливаем зависимости системы для bcrypt и других пакетов
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Рабочая директория
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости через Poetry (без виртуального окружения)
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Копируем проект
COPY . .

# По умолчанию запускаем API (можно переопределить командой в docker-compose.override.yml)
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]

