"""FastAPI application factory with CORS, audit middleware, and route registration.

This module creates and configures the FastAPI application for the MasterMind Framework.

Requirements: UI-01, UI-07
"""

import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.api.routes import auth, tasks, brains
from mastermind_cli.api.routes.executions import router as executions_router
from mastermind_cli.api.websocket import router as websocket_router
from mastermind_cli.state.database import DatabaseConnection

_WEB_DIR = Path(__file__).parent.parent / "web"


def create_app(db_path: str = ":memory:") -> FastAPI:
    """Create and configure FastAPI application.

    Args:
        db_path: Path to SQLite database (default: in-memory)

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="MasterMind Framework",
        description="AI-powered brain orchestration platform",
        version="1.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS with explicit origins (Pitfall 7: wildcard + credentials is invalid)
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Explicit origins required when allow_credentials=True
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register audit middleware (UI-07 requirement)
    @app.middleware("http")
    async def audit_middleware(request: Request, call_next: Any) -> Any:
        """Log all POST/PUT/DELETE requests to audit_log table."""
        # Capture request body for mutations BEFORE call_next (body is a stream)
        request_body = None
        request_hash = None
        if request.method in ["POST", "PUT", "DELETE"]:
            request_body = await request.body()

        response = await call_next(request)

        # Extract user_id AFTER call_next (auth dependency sets request.state.user_id)
        user_id = getattr(request.state, "user_id", None)

        # Write audit log for mutations
        if request.method in ["POST", "PUT", "DELETE"] and user_id:
            request_hash = (
                hashlib.sha256(request_body).hexdigest()[:16] if request_body else None
            )

            async with DatabaseConnection(db_path) as db:
                await db.conn.execute(
                    """INSERT INTO audit_log
                       (id, user_id, endpoint, method, request_hash, response_status, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    [
                        str(uuid.uuid4()),
                        user_id,
                        str(request.url.path),
                        request.method,
                        request_hash,
                        response.status_code,
                        datetime.utcnow(),
                    ],
                )
                await db.conn.commit()

        return response

    # Health check endpoint
    @app.get("/")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "version": "1.1.0"}

    # Wire db_path into all routes via dependency override
    app.dependency_overrides[get_db_path] = lambda: db_path

    # Register routes
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
    app.include_router(brains.router, prefix="/api", tags=["Brains"])
    app.include_router(executions_router, prefix="/api/executions", tags=["Executions"])
    app.include_router(websocket_router, tags=["WebSocket"])

    # Serve dashboard HTML
    @app.get("/dashboard", include_in_schema=False)
    async def dashboard() -> FileResponse:
        return FileResponse(_WEB_DIR / "index.html")

    # Mount static files for web UI
    if (_WEB_DIR / "static").exists():
        app.mount(
            "/static", StaticFiles(directory=str(_WEB_DIR / "static")), name="static"
        )

    # Startup event: create database schema
    @app.on_event("startup")
    async def startup_event() -> None:
        """Initialize database schemas on startup."""
        async with DatabaseConnection(db_path) as db:
            await db.create_task_schema()
            await db.create_auth_schema()
            await db.create_execution_history_schema()

    return app


def get_app() -> FastAPI:
    """Get FastAPI application instance (for uvicorn).

    Usage:
        uvicorn mastermind_cli.api.app:get_app --factory

    Reads MM_DB_PATH from environment (default: /app/data/mastermind.db).
    """
    db_path = os.environ.get("MM_DB_PATH", "/app/data/mastermind.db")
    return create_app(db_path)


# Dependency for database access
async def get_db() -> AsyncGenerator[DatabaseConnection, None]:
    """Database dependency for FastAPI routes."""
    db = DatabaseConnection(":memory:")
    await db.connect()
    try:
        yield db
    finally:
        await db.close()
