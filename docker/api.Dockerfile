ARG PYTHON_VERSION=3.11.1
FROM python:${PYTHON_VERSION}-slim AS python-base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ARG POETRY_VERSION=2.1.2
ENV POETRY_VERSION=${POETRY_VERSION}
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_HOME="/opt/poetry"
ENV PYSETUP_PATH="/opt/pysetup"
ENV VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base AS builder

RUN apt-get update  \
    && apt-get install --no-install-recommends -y  \
    curl

# Use POETRY_VERSION & POETRY_HOME internally
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH

COPY pyproject.toml poetry.lock ./

RUN poetry install --with api

FROM python-base AS runtime

COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

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

WORKDIR /app

COPY ./src/api ./api

COPY ./fonts ./fonts

COPY ./alembic ./alembic

COPY ./alembic.ini .

CMD alembic upgrade head && python -m api

