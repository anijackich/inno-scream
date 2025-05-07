ARG PYTHON_VERSION=3.11.1
FROM python:${PYTHON_VERSION}-slim as python-base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV POETRY_VERSION=2.1.2
ENV POETRY_HOME="/opt/poetry"
ENV PYSETUP_PATH="/opt/pysetup"
ENV VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder

RUN apt-get update  \
    && apt-get install --no-install-recommends -y  \
    curl

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH

COPY pyproject.toml poetry.lock ./

RUN poetry install --with api --no-root

FROM python-base

ARG UID=10001
ARG GID=10001
RUN addgroup --gid "${GID}" appgroup && \
  adduser \
  --disabled-password \
  --gecos "" \
  --home "/nonexistent" \
  --shell "/sbin/nologin" \
  --no-create-home \
  --uid "${UID}" \
  --gid "${GID}" \
  appuser

USER appuser

COPY --from=builder $VENV_PATH $VENV_PATH

WORKDIR /app

COPY ./src/api ./api
COPY ./alembic.ini .

CMD alembic upgrade head && poetry run python -m api

