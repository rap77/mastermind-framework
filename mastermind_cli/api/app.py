"""FastAPI application factory with CORS, audit middleware, and route registration.

This module creates and configures the FastAPI application for the MasterMind Framework.

Requirements: UI-01, UI-07
"""

import time
import hashlib
import uuid
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from mastermind_cli.api.routes import auth, tasks
from mastermind_cli.api.websocket import router as websocket_router
from mastermind_cli.state.database import DatabaseConnection


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

    # Configure CORS for all origins (adjustable via env var)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure via ENV_VAR in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register audit middleware (UI-07 requirement)
    @app.middleware("http")
    async def audit_middleware(request: Request, call_next):
        """Log all POST/PUT/DELETE requests to audit_log table."""
        start_time = time.time()

        # Extract user_id from JWT if present (set by auth dependency)
        user_id = getattr(request.state, "user_id", None)

        # Capture request body for mutations
        request_body = None
        request_hash = None
        if request.method in ["POST", "PUT", "DELETE"]:
            request_body = await request.body()

        response = await call_next(request)

        # Write audit log for mutations
        if request.method in ["POST", "PUT", "DELETE"] and user_id:
            request_hash = hashlib.sha256(request_body).hexdigest()[:16] if request_body else None

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
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "1.1.0"}

    # Register routes
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
    app.include_router(websocket_router, tags=["WebSocket"])

    # Mount static files for web UI
    # Note: Will be mounted in Plan 02 after creating HTML/CSS/JS
    # app.mount("/static", StaticFiles(directory="mastermind_cli/web/static"), name="static")

    # Startup event: create database schema
    @app.on_event("startup")
    async def startup_event():
        """Initialize database schemas on startup."""
        async with DatabaseConnection(db_path) as db:
            await db.create_task_schema()
            await db.create_auth_schema()

    return app


def get_app() -> FastAPI:
    """Get FastAPI application instance (for uvicorn).

    Usage:
        uvicorn mastermind_cli.api.app:get_app --factory
    """
    return create_app()


# Dependency for database access
async def get_db() -> DatabaseConnection:
    """Database dependency for FastAPI routes."""
    db = DatabaseConnection(":memory:")
    await db.connect()
    try:
        yield db
    finally:
        await db.close()
