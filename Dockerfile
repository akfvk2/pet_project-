FROM python:3.12.8-slim
LABEL authors="Александр"
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app


RUN pip install --no-cache-dir poetry


COPY pyproject.toml poetry.lock* ./


RUN poetry install --no-root --no-ansi && rm -rf $POETRY_CACHE_DIR

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]