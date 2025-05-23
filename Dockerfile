FROM python:3.11-slim-bookworm

WORKDIR /app

COPY ./poetry.lock ./pyproject.toml /app/

RUN pip install --no-cache-dir poetry==1.4.0 && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY . /app/

EXPOSE 8000



CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]