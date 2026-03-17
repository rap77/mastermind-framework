# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.14-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock README.md ./

# Install dependencies (frozen via uv.lock)
RUN uv sync --frozen --no-dev

# Stage 2: Runtime
FROM python:3.14-slim as runtime

# Install uv for runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY mastermind_cli/ ./mastermind_cli/
COPY scripts/ ./scripts/

# Create data directory for SQLite persistence
RUN mkdir -p /app/data

# Create non-root user
RUN useradd -m -u 1000 mastermind && \
    chown -R mastermind:mastermind /app
USER mastermind

# Database path (override via env or docker-compose volume)
ENV MM_DB_PATH=/app/data/mastermind.db

# Set PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose port (FastAPI dashboard)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD uv run mastermind-cli --version || exit 1

# Default command (FastAPI server via uvicorn)
CMD ["uvicorn", "mastermind_cli.api.app:get_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
