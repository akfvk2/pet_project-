FROM python:3.12.8
LABEL authors="Александр"
WORKDIR /app

COPY pyproject.toml ./
RUN pip