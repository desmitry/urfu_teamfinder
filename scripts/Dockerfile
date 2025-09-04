FROM python:3.12.3-slim

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=on \
    PIP_ROOT_USER_ACTION=ignore

ENV \
    POETRY_NO_INTERACTION=1 \
    POETRY_NO_ANSI=1

RUN mkdir /backend

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN pip install --upgrade pip && pip install poetry
RUN poetry install --no-root

COPY __init__.py ./
COPY src/__init__.py src/
COPY src/core src/core/
COPY scripts scripts/
COPY configs configs/

ENTRYPOINT ["/bin/bash"]