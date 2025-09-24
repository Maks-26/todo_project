# alembic/env.py

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from app.db import Base

# --- наши импорты ---
from settings import get_settings

# Alembic config
config = context.config

# Используем .ini только для логов
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# загружаем настройки проекта
settings = get_settings()

# Передаем Alembic правильный URL из settings
print("⚡ Alembic using DB URL:", settings.DATABASE_URL)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Метаданные всех моделей (User, Task и т.д.)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
