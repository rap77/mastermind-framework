"""FastAPI application factory with CORS and route registration.

This module creates and configures the FastAPI application for the MasterMind Framework.

Requirements: UI-01, UI-07
"""

import os
import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from mastermind_cli.api.dependencies import get_db_path, get_project_state_db_url
from mastermind_cli.api.routes import analytics, auth, tasks, brains
from mastermind_cli.observability.trace_context import set_trace_id
from mastermind_cli.api.routes.executions import router as executions_router
from mastermind_cli.api.routes.experiences import router as experiences_router
from mastermind_cli.api.routes.keys import (
    router as keys_router,
    _limiter as keys_limiter,
)
from mastermind_cli.api.websocket import router as websocket_router
from mastermind_cli.api.companies import router as companies_router
from mastermind_cli.api.routes.project_overview import router as project_overview_router
from mastermind_cli.api.routes.project_participants import (
    router as project_participants_router,
)
from mastermind_cli.project_state.database.session import initialize_database
from mastermind_cli.state.database import DatabaseConnection

# gRPC server (Phase 18: gap-closure)
try:
    from routers.internal import start_grpc_server

    _GRPC_ENABLED = True
except ImportError:
    _GRPC_ENABLED = False

# Audit trail router (MM-Flow audit infrastructure)
audit_router: Optional[Any] = None

try:
    from routers import audit as audit_router_module

    audit_router = audit_router_module.router
except ImportError:
    # Fallback if audit router not available
    pass

# Channel routers for multi-channel gateway
instagram_router: Optional[Any] = None
whatsapp_router: Optional[Any] = None

try:
    from routers import instagram, whatsapp

    instagram_router = instagram.router
    whatsapp_router = whatsapp.router
except ImportError:
    # Fallback if routers not available
    pass

_WEB_DIR = Path(__file__).parent.parent / "web"
logger = logging.getLogger(__name__)

# Global gRPC server instance (for graceful shutdown)
_grpc_server = None


def _grpc_server_disabled() -> bool:
    """Return whether gRPC startup is disabled by environment."""
    return os.environ.get("MM_DISABLE_GRPC_SERVER", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _resolve_project_state_db_url(db_path: str) -> str:
    """Resolve the project state database URL for the current app instance."""
    project_state_db_url = os.environ.get("MM_PROJECT_STATE_DB_URL")
    if project_state_db_url:
        return project_state_db_url

    postgres_url = os.environ.get("POSTGRES_URL")
    if postgres_url:
        return postgres_url

    if db_path == ":memory:":
        return "sqlite:///:memory:"
    return f"sqlite:///{db_path}.project_state"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage FastAPI app lifecycle: startup and shutdown of services.

    Startup:
    - Initializes database schemas
    - Starts gRPC server for webhook processing (Phase 18: gap-closure)

    Shutdown:
    - Gracefully stops gRPC server
    """
    global _grpc_server

    # STARTUP
    async with DatabaseConnection(":memory:") as db:
        await db.create_task_schema()
        await db.create_auth_schema()
        await db.create_execution_history_schema()
        await db.create_api_keys_v2_schema()
        await db.create_experience_schema()
        await db.create_audit_trail_schema()

    # Start gRPC server (Phase 18: AI Worker gRPC integration)
    if _GRPC_ENABLED and not _grpc_server_disabled():
        try:
            _grpc_server = await start_grpc_server()
        except Exception as e:
            logger.warning("Failed to start gRPC server: %s", e)
            # Don't fail app startup if gRPC is optional
            pass

    yield

    # SHUTDOWN
    if _grpc_server:
        try:
            await _grpc_server.stop(grace=0.1)
        except Exception as e:
            logger.warning("Error closing gRPC server: %s", e)


def create_app(
    db_path: str = ":memory:",
    governance: object | None = None,
) -> FastAPI:
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
        lifespan=lifespan,
    )
    app.state.governance = governance
    app.state.db_path = db_path
    initialize_database(_resolve_project_state_db_url(db_path))

    # Register rate limiter (Brain #7 gap B — prevent bcrypt DoS via x-api-key spam)
    app.state.limiter = keys_limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # Configure CORS with explicit origins (Pitfall 7: wildcard + credentials is invalid)
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3001,http://localhost:3000"
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Explicit origins required when allow_credentials=True
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # B1.13 / B1.14: Trace propagation middleware
    # Reads X-Trace-ID from HTTP request header and binds it to the async
    # ContextVar so all structlog calls within the request carry trace_id.
    # If the header is absent or empty, a fresh UUID v4 is generated.
    @app.middleware("http")
    async def trace_id_middleware(request: Request, call_next: Any) -> Any:
        """Extract X-Trace-ID header and set it in the trace ContextVar.

        Priority:
          1. X-Trace-ID request header, if present and non-empty
          2. Fresh UUID v4

        After this middleware runs every structlog call in the request handler
        emits {"trace_id": "<value>"} automatically via the add_trace_id processor.
        """
        raw = request.headers.get("X-Trace-ID", "").strip()
        trace_id = raw if raw else str(uuid.uuid4())
        set_trace_id(trace_id)
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response

    # Health check endpoints
    @app.get("/")
    async def root_health_check() -> dict[str, str]:
        """Root health check endpoint."""
        return {"status": "healthy", "version": "1.1.0"}

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """B3.2: Health check endpoint — returns status and db backend.

        Returns:
            JSON with status=ok and db=sqlite.
        """
        return {"status": "ok", "db": "sqlite"}

    # Wire db_path into all routes via dependency overrides
    async def _provide_db_path() -> str:
        """Provide the application-scoped database path."""
        return db_path

    async def _provide_project_state_db_url() -> str:
        """Provide the application-scoped project state database URL."""
        return _resolve_project_state_db_url(db_path)

    app.dependency_overrides[get_db_path] = _provide_db_path
    app.dependency_overrides[get_project_state_db_url] = _provide_project_state_db_url

    # Register routes
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
    app.include_router(brains.router, prefix="/api", tags=["Brains"])
    app.include_router(executions_router, prefix="/api/executions", tags=["Executions"])
    app.include_router(
        experiences_router, prefix="/api/experiences", tags=["Experiences"]
    )
    app.include_router(keys_router, prefix="/api/keys", tags=["API Keys"])
    app.include_router(analytics.router)  # Analytics endpoints
    app.include_router(websocket_router, tags=["WebSocket"])
    app.include_router(companies_router)  # Companies with tenant isolation
    app.include_router(
        project_overview_router,
        prefix="/api/projects",
        tags=["Project State"],
    )
    app.include_router(
        project_participants_router,
        prefix="/api/projects",
        tags=["Project Participants"],
    )

    # Audit trail router (MM-Flow infrastructure — Phase 16+)
    if audit_router:
        app.include_router(audit_router, tags=["Audit"])

    # Channel routers for multi-channel gateway (Phase 18)
    if instagram_router:
        app.include_router(instagram_router, tags=["Instagram"])
    if whatsapp_router:
        app.include_router(whatsapp_router, tags=["WhatsApp"])

    # Serve dashboard HTML
    @app.get("/dashboard", include_in_schema=False)
    async def dashboard() -> FileResponse:
        """Serve the web dashboard entrypoint."""
        return FileResponse(_WEB_DIR / "index.html")

    # Mount static files for web UI
    if (_WEB_DIR / "static").exists():
        app.mount(
            "/static", StaticFiles(directory=str(_WEB_DIR / "static")), name="static"
        )

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
    db_path = os.environ.get("MM_DB_PATH", "/app/data/mastermind.db")
    db = DatabaseConnection(db_path)
    await db.connect()
    try:
        yield db
    finally:
        await db.close()
