# Dockerfile

# Используем Python 3.13
FROM python:3.13-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry через pip (это гарантированно работает на Python 3.13)
RUN pip install --no-cache-dir poetry

# Рабочая директория
WORKDIR /app

# Копируем только файлы зависимостей
COPY pyproject.toml poetry.lock* ./

# Настройки Poetry — не создавать виртуальное окружение
RUN poetry config virtualenvs.create false

# Устанавливаем проектные зависимости
RUN poetry install --no-root --no-interaction --no-ansi

# Копируем остальной проект
COPY . .

# Значение по умолчанию — запуск API
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
