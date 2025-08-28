FROM python:3.12-slim-bookworm

# Install curl for downloading uv
RUN apt-get update && apt-get install -y curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download uv binary based on target architecture
ARG TARGETARCH
RUN case "$TARGETARCH" in \
      amd64)  ARCH=x86_64 ;; \
      arm64)  ARCH=aarch64 ;; \
      *) echo "Unsupported architecture: $TARGETARCH" && exit 1 ;; \
    esac && \
    curl -L "https://github.com/astral-sh/uv/releases/latest/download/uv-${ARCH}-unknown-linux-musl.tar.gz" \
    | tar -xz && \
    mv uv-${ARCH}-unknown-linux-musl/uv /usr/local/bin/ && \
    mv uv-${ARCH}-unknown-linux-musl/uvx /usr/local/bin/ && \
    rm -rf uv-${ARCH}-unknown-linux-musl

WORKDIR /api-server

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --locked

# Copy app source code
COPY . .

EXPOSE 8000

# Start the app
CMD ["uv", "run", "run.py", "--mode", "production", "--workers", "4"]
