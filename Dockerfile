FROM python:3.10-alpine as build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /opt/build

# Install poetry
RUN apk add --no-cache poetry

# Install package dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry env use /usr/local/bin/python3 && \
    poetry install --no-root --no-dev

# Install package
COPY src ./src
RUN poetry install --no-dev

FROM python:3.10-alpine

WORKDIR /opt/action

RUN apk add --no-cache git

# Copy the package
COPY --from=build /opt/build/.venv ./.venv
# Normally we'd copy this into workdir, but GitHub hardcodes it
COPY --from=build /opt/build/src ./.venv/lib/python3.10/site-packages/

# "Activate" the venv
ENV PATH="/opt/action/.venv/bin:${PATH}"

# Entrypoint
CMD ["python3", "-m", "dalamud_plugin_pr2"]
