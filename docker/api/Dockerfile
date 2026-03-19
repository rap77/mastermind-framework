# Multi-stage build for optimized image size
# Build context: ../../apps/api

# Stage 1: Builder
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.14-slim AS runtime

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY mastermind_cli/ ./mastermind_cli/
COPY agents/ ./agents/
COPY scripts/ ./scripts/

RUN mkdir -p /app/data

RUN useradd -m -u 1000 mastermind && \
    chown -R mastermind:mastermind /app
USER mastermind

ENV MM_DB_PATH=/app/data/mastermind.db
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run mastermind-cli --version || exit 1

CMD ["uvicorn", "mastermind_cli.api.app:get_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
