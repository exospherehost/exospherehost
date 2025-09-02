ARG UV_VERSION=0.4.28
ARG UV_DIGEST=sha256:REPLACE_WITH_MANIFEST_DIGEST
FROM ghcr.io/astral-sh/uv:${UV_VERSION}@${UV_DIGEST} AS uv
ARG PYTHON_DIGEST=sha256:REPLACE_WITH_MANIFEST_DIGEST
FROM python:3.12-slim-bookworm@${PYTHON_DIGEST}

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /api-server

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY . .

EXPOSE 8000

CMD ["uv", "run", "run.py", "--mode", "production", "--workers", "4"]