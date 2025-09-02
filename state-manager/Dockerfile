FROM python:3.12-slim-bookworm

RUN pip install --no-cache-dir uv==0.4.28

WORKDIR /api-server

COPY pyproject.toml uv.lock ./

RUN uv sync --locked

COPY . .

EXPOSE 8000

CMD ["uv", "run", "run.py", "--mode", "production", "--workers", "4"]