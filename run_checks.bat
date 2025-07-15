@echo off
poetry run black .
poetry run isort .
poetry run ruff check .
poetry run flake8 .
poetry run pytest
pause
