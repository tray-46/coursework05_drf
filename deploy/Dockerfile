FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV POETRY_VERSION=2.2.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        gcc \
        libpq-dev \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ../../pyproject.toml ./poetry.lock ./
RUN poetry install --no-interaction --no-ansi --no-root --only main

COPY ../.. /app

EXPOSE 8000

ENTRYPOINT ["deploy/entrypoint.sh"]
