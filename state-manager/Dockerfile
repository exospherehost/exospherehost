FROM ghcr.io/astral-sh/uv:0.4.28 as uv

FROM python:3.12-slim-bookworm

COPY --from=uv /uv /usr/local/bin/uv
COPY --from=uv /uvx /usr/local/bin/uvx

WORKDIR /api-server

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY . .

EXPOSE 8000

CMD ["uv", "run", "run.py", "--mode", "production", "--workers", "4"]