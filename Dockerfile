FROM python:3.12.8
LABEL authors="Александр"
WORKDIR /app

COPY pyproject.toml ./

RUN poetry install

COPY . .

CMD["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]