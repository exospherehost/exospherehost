ARG UV_VERSION=0.4.28
FROM ghcr.io/astral-sh/uv:${UV_VERSION}@sha256:<digest> AS uv

FROM python:3.12-slim-bookworm@sha256:<digest>

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /api-server

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY . .

EXPOSE 8000

CMD ["uv", "run", "run.py", "--mode", "production", "--workers", "4"]