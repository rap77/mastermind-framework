# Phase 3: Web UI Platform - Research

**Researched:** 2026-03-13
**Domain:** Full-stack Web Dashboard (FastAPI + React Flow + WebSockets)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Authentication & Sessions:**
- **Mechanismo Híbrido:** Web UI usa JWT (Access 30min + Refresh 24h con rotación), CLI usa API Keys (long-lived)
- **Storage:** SQLite con `users`, `api_keys`, `sessions` tables (campos sensibles encriptados en reposo)
- **User Management:** Admin user por defecto en Phase 3 (sin RBAC, password recovery, email validation)
- **Session Timeout:** 1 hora inactividad + Silent Refresh durante ejecución brains

**Dashboard Layout & UI:**
- **Layout:** Hybrid Command Center (Sidebar izquierdo + Bento Grid central + Panel inferior logs)
- **Bento Grid:** 60% Grafo DAG interactivo, 20% Métricas de Salud, 20% Proveedores
- **Visualización:** Layered Dependency Tree estilo CI/CD (GitHub Actions, Jenkins)
- **Estados:** 🔳 Pending, 🔵 Running (animado), 🟢 Completed, 🔴 Failed (palpitando), 🟡 Skipped
- **Librería:** React Flow (backend-agnostic, D3-based)
- **Theme:** System-Adaptive con paleta "Cyber-Modern" (fondos #0F172A, bordes sutiles + glow)
- **Tipografía:** JetBrains Mono o Geist Mono

**Real-time Updates:**
- **Streaming:** Smart Focus + Throttled UI (300ms) - solo streaming detallado del brain en foco
- **Reconexión:** Ghost Mode 3-Tier (<30s buffer, 30s-5min Ghost Mode, >5min manual refresh)
- **Fallback:** Smart Degradation (Hybrid Polling) con frecuencia adaptativa (1-2s agresivo → 10s relajado)
- **Server Buffer:** 100 events (~30s) en memoria

**Observability:**
- **Logs Panel:** Fixed Bottom Drawer colapsable (tipo terminal WSL2)
- **Trace Back:** Ripple Effect (hover nodo fallido → atenúa ancestros + camino rojo)
- **SQLite Inspector:** Interactive SQL Console

**Mobile Responsiveness:**
- **Estrategia:** Tactical Mirror (móvil usa List-View vertical + Snapshot estático, Desktop usa Grafo completo)
- **Prioridad:** Desktop First (90% foco en monitor estándar, móvil como salvavidas)

### Claude's Discretion

- Valor exacto de throttling (300ms es razonable)
- Tamaño del server buffer (100 events ~30s)
- Umbral exacto de Ghost Mode (30s, 5min pueden ajustarse)
- Frecuencia de polling adaptativo (1s, 2s, 10s - configurable)
- Diseño exacto del Snapshot estático (PNG, SVG, PDF)
- Cantidad de líneas en mini-viewer móvil (5 es sugerencia)

### Deferred Ideas (OUT OF SCOPE)

- Real-time collaborative editing (v3.0+)
- Multi-tenant SaaS infrastructure
- Native mobile apps (iOS/Android)
- Advanced ML features (auto-improvement)
- Hot-reload de brains sin restart
- Type-aware auto-completion en Web UI (Monaco editor)
- Custom metrics dashboard (success rate, brain usage charts)
- Template library para reusable execution patterns
- Granular permissions (per-brain, per-niche RBAC)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| UI-01 | System provides web dashboard built with FastAPI backend | Section: Standard Stack - FastAPI + uvicorn, WebSocket support verified |
| UI-02 | System implements basic authentication (username/password, session tokens) | Section: Authentication & Security - JWT with access/refresh tokens, bcrypt hashing |
| UI-03 | System manages user sessions across requests (session storage, timeout) | Section: Architecture Patterns - Session management with SQLite + token rotation |
| UI-04 | System provides real-time progress updates via WebSocket connections | Section: Real-time Communication - WebSocket with ConnectionManager pattern |
| UI-05 | UI is responsive on mobile and tablet devices (CSS grid/flexbox) | Section: Frontend Stack - React Flow + Tailwind CSS responsive utilities |
| UI-06 | User can export execution results in JSON, YAML, or Markdown formats | Section: Standard Stack - Existing Pydantic models support YAML/JSON export |
| UI-07 | System maintains audit logging (timestamp, user, action, execution ID) | Section: Architecture Patterns - AuditLog table in SQLite |
| UI-08 | Multiple users can have isolated sessions (per-request orchestrator instances) | Section: Architecture Patterns - Session isolation with orchestrator-per-request |
| UI-09 | System displays visual dependency graph of brains (D3.js or Cytoscape.js) | Section: Frontend Stack - React Flow for node-based graphs (D3-based) |
| UI-10 | User can trigger brain execution manually via web form | Section: REST API Endpoints - POST /api/executions endpoint |
| ARCH-03 | System supports session isolation (no shared global state in coordinator) | Section: Architecture Patterns - Coordinator instantiation pattern |
| PAR-08 | System provides real-time progress dashboard via WebSocket (live task cards) | Section: Real-time Communication - WebSocket broadcast with throttled updates |
| PERF-02 | Task state queries complete in <100ms (SQLite indexed) | Section: Performance Optimization - Indexed queries, async operations |
| PERF-03 | WebSocket latency for progress updates <500ms | Section: Real-time Communication - 300ms throttling meets requirement |
| PERF-04 | Web dashboard initial page load <2 seconds | Section: Performance Optimization - Static files, bundle splitting, lazy loading |
</phase_requirements>

## Summary

Phase 3 transforms MasterMind from a CLI-only framework to a production-ready web platform. The research confirms **FastAPI + React Flow + WebSockets** as the optimal stack for real-time orchestration dashboards, balancing development velocity with production robustness.

**Primary recommendation:** Use FastAPI's built-in WebSocket support with a ConnectionManager for broadcasting, React Flow (@xyflow/react) for the dependency graph visualization, and JWT-based authentication with refresh token rotation for secure session management. SQLite remains the persistence layer (encrypted for sensitive fields) with indexed queries for sub-100ms response times.

**Key technical decisions validated by research:**
- **FastAPI WebSockets** provide production-ready bidirectional communication with automatic connection handling
- **React Flow** (v12.10+) is purpose-built for node-based editors and interactive diagrams, used by Stripe and Typeform
- **JWT with refresh token rotation** prevents token leakage while maintaining good UX (30min access + 24h refresh tokens)
- **Session isolation** via per-request Coordinator instances ensures multi-user support without shared state
- **Ghost Mode** (<30s buffer, 30s-5min resync from SQLite) provides robust reconnection handling
- **Hybrid polling fallback** ensures compatibility with restrictive proxies/firewalls

The research identifies **HIGH confidence** in the standard stack (FastAPI, React Flow, WebSockets) and **MEDIUM confidence** in frontend-specific optimizations (bundle splitting, lazy loading) due to framework-specific variations.

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| **FastAPI** | 0.115+ | Web framework with async support, WebSocket, OAuth2 | Production-ready, auto-generated OpenAPI docs, type-safe with Pydantic |
| **uvicorn[standard]** | 0.30+ | ASGI server with WebSocket support | Recommended by FastAPI, handles async/await natively |
| **websockets** | 13+ | WebSocket protocol implementation | Required by FastAPI for WebSocket endpoints |
| **@xyflow/react** | 12.10+ | React Flow for node-based graph visualization | Purpose-built for workflow editors, used by Stripe/Typeform, D3-based |
| **React** | 19+ | UI framework | Latest stable, compatible with React Flow 12.10+ |
| **Tailwind CSS** | 4+ | Utility-first CSS | Responsive design, dark mode support, integrates with React Flow |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **python-jose[cryptography]** | 3.3+ | JWT encoding/decoding | Access token and refresh token generation |
| **passlib[bcrypt]** | 1.7+ | Password hashing | Secure password storage with bcrypt |
| **python-multipart** | 0.0+ | Form data parsing | Login form submission (username/password) |
| **aiosqlite** | 0.20+ | Async SQLite operations | Already in project, async DB queries |
| **pydantic-settings** | 2.0+ | Configuration management | JWT secret keys, DB paths from environment |
| **httpx** | 0.27+ | Async HTTP client | Testing WebSocket/REST endpoints |

### Dev Dependencies

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **pytest-asyncio** | 0.24+ | Async test support | Testing WebSocket/async endpoints |
| **httpx-ws** | 0.6+ | WebSocket test client | Testing WebSocket connections |
| **playwright** | 1.48+ | E2E browser testing | Testing UI interactions, login flow, graph rendering |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| React Flow | D3.js (direct) | React Flow: 10x faster for node graphs, built-in interactions. D3.js: More flexible but 500+ LOC for basic drag/zoom |
| FastAPI WebSockets | Socket.IO | FastAPI native: 0 dependencies, works with any WS client. Socket.IO: Better reconnection but requires client library + doesn't scale to multi-process |
| JWT + Refresh Tokens | Session cookies + Redis | JWT: Stateless, scales horizontally. Redis: Faster revocation but adds infrastructure complexity (single-host v2.0 doesn't need it) |
| SQLite | PostgreSQL | SQLite: Zero config, single-file DB. PostgreSQL: Better concurrency but overkill for single-host deployment |

**Installation:**
```bash
# Backend dependencies
uv add fastapi uvicorn[standard] websockets python-jose[cryptography] passlib[bcrypt] python-multipart pydantic-settings aiosqlite

# Frontend (in separate web/ directory)
npm install react react-dom @xyflow/react tailwindcss

# Dev dependencies
uv add --dev pytest-asyncio httpx-ws playwright
npm install --save-dev @playwright/test
```

## Architecture Patterns

### Recommended Project Structure

```
mastermind_cli/
├── api/                          # NEW: FastAPI application
│   ├── __init__.py
│   ├── app.py                    # FastAPI app factory
│   ├── routes/                   # API route modules
│   │   ├── auth.py               # Login, refresh, token endpoints
│   │   ├── executions.py         # CRUD for task executions
│   │   ├── websocket.py          # WebSocket endpoint
│   │   └── admin.py              # Admin-only endpoints
│   ├── middleware/               # NEW: Custom middleware
│   │   ├── auth_middleware.py    # JWT validation
│   │   └── cors_middleware.py    # CORS configuration
│   ├── dependencies/             # FastAPI dependencies
│   │   ├── get_current_user.py   # Extract user from JWT
│   │   └── get_orchestrator.py   # Per-request coordinator
│   └── static/                   # NEW: Frontend static files
│       ├── index.html
│       └── assets/               # Compiled JS/CSS from web/
│
├── auth/                         # NEW: Authentication module
│   ├── __init__.py
│   ├── models.py                 # User, APIKey, Session models
│   ├── security.py               # JWT encoding, password hashing
│   ├── service.py                # Login, refresh, token rotation
│   └── repository.py             # User CRUD operations
│
├── web/                          # NEW: Frontend application
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── Dashboard.tsx     # Main layout
│   │   │   ├── GraphView.tsx     # React Flow wrapper
│   │   │   ├── LogPanel.tsx      # Bottom drawer logs
│   │   │   └── LoginForm.tsx     # Login form
│   │   ├── hooks/                # Custom React hooks
│   │   │   ├── useWebSocket.ts   # WebSocket connection manager
│   │   │   └── useTaskState.ts   # Task state polling fallback
│   │   ├── lib/                  # Utilities
│   │   │   └── api.ts            # HTTP client wrapper
│   │   └── App.tsx               # Root component
│   ├── package.json
│   ├── vite.config.ts            # Vite bundler config
│   └── tailwind.config.js        # Tailwind CSS config
│
├── state/                        # EXISTING: SQLite persistence
│   ├── database.py               # Async DB connection
│   ├── models.py                 # TaskRecord (extend with AuditLog)
│   └── repositories.py           # TaskRepository (extend with AuditLogRepository)
│
└── orchestrator/                 # EXISTING: Core orchestration
    ├── coordinator.py            # MODIFY: Remove global state, support per-request instances
    └── ...                       # (other modules unchanged)
```

### Pattern 1: FastAPI App Factory with WebSocket Support

**What:** Factory function that creates FastAPI app with mounted routes, middleware, and WebSocket endpoints.

**When to use:** Application startup, test setup, multiple app instances.

**Example:**
```python
# mastermind_cli/api/app.py
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, executions, websocket
from .middleware import auth_middleware

def create_app() -> FastAPI:
    """Create FastAPI application with all routes mounted."""
    app = FastAPI(title="MasterMind API", version="2.0.0")

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vite dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routes
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(executions.router, prefix="/api/executions", tags=["executions"])
    app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

    # Mount static files (compiled frontend)
    app.mount("/", StaticFiles(directory="mastermind_cli/api/static"), name="static")

    return app

# Source: https://fastapi.tiangolo.com/advanced/websockets/
```

### Pattern 2: ConnectionManager for Multi-Client WebSocket Broadcasting

**What:** Singleton class that manages active WebSocket connections and broadcasts messages to all connected clients.

**When to use:** Real-time updates to multiple dashboard viewers simultaneously.

**Example:**
```python
# mastermind_cli/api/routes/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import asyncio
import json

class ConnectionManager:
    """Manage WebSocket connections and broadcast messages."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self._event_buffer: dict[str, list[dict]] = {}  # brain_id -> events

    async def connect(self, websocket: WebSocket, task_id: str) -> None:
        """Accept connection and add to active list."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove connection from active list."""
        self.active_connections.remove(websocket)

    async def broadcast_task_update(self, task_id: str, brain_id: str, status: str, progress: float) -> None:
        """Broadcast task update to all connected clients (throttled)."""
        message = {
            "type": "task_update",
            "task_id": task_id,
            "brain_id": brain_id,
            "status": status,
            "progress": progress,
            "timestamp": asyncio.get_event_loop().time()
        }

        # Buffer for reconnection (<30s window)
        if brain_id not in self._event_buffer:
            self._event_buffer[brain_id] = []
        self._event_buffer[brain_id].append(message)
        if len(self._event_buffer[brain_id]) > 100:
            self._event_buffer[brain_id].pop(0)  # Keep last 100 events

        # Broadcast to all connections
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/tasks/{task_id}")
async def websocket_task_updates(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time task progress updates."""
    await manager.connect(websocket, task_id)
    try:
        while True:
            # Keep connection alive (ping/pong)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Source: https://fastapi.tiangolo.com/advanced/websockets/ (ConnectionManager pattern)
```

### Pattern 3: JWT Authentication with Refresh Token Rotation

**What:** OAuth2 password flow with short-lived access tokens (30min) and long-lived refresh tokens (24h) that rotate on every use.

**When to use:** Secure authentication for web UI without external OAuth providers.

**Example:**
```python
# mastermind_cli/auth/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key-here"  # TODO: Load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 1

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token (longer-lived)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid4())})  # jti for rotation
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
```

### Pattern 4: Per-Request Orchestrator for Session Isolation

**What:** FastAPI dependency that creates a new Coordinator instance for each request, ensuring no shared state between users.

**When to use:** REST endpoints and WebSocket handlers that execute brains.

**Example:**
```python
# mastermind_cli/api/dependencies/get_orchestrator.py
from fastapi import Depends
from mastermind_cli.orchestrator.coordinator import Coordinator
from mastermind_cli.memory import EvaluationLogger

async def get_orchestrator(
    enable_logging: bool = True
) -> Coordinator:
    """Create a new Coordinator instance for this request."""
    return Coordinator(
        formatter=None,
        use_mcp=True,
        enable_logging=enable_logging
    )

# Usage in route
from fastapi import APIRouter, Depends
from .dependencies import get_orchestrator

router = APIRouter()

@router.post("/api/executions")
async def create_execution(
    brief: str,
    orchestrator: Coordinator = Depends(get_orchestrator)
):
    """Execute brains with a new coordinator instance (session isolation)."""
    result = await orchestrator.coordinate(brief)
    return result
```

### Pattern 5: React Flow Graph Visualization

**What:** React component that renders the brain dependency graph as an interactive node-based diagram.

**When to use:** Dashboard main view, execution visualization.

**Example:**
```typescript
// web/src/components/GraphView.tsx
import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useWebSocket } from '../hooks/useWebSocket';

interface GraphViewProps {
  taskId: string;
}

export function GraphView({ taskId }: GraphViewProps) {
  const { taskStates } = useWebSocket(taskId);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Transform taskStates to React Flow nodes
  const flowNodes = useMemo(() => {
    return Object.entries(taskStates).map(([brainId, state]) => ({
      id: brainId,
      position: { x: 0, y: 0 },  // TODO: Auto-layout with dagre
      data: { label: brainId, status: state.status },
      style: getNodeStyle(state.status),
    }));
  }, [taskStates]);

  return (
    <ReactFlow
      nodes={flowNodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      fitView
    >
      <Controls />
      <Background />
      <MiniMap />
    </ReactFlow>
  );
}

function getNodeStyle(status: string): React.CSSProperties {
  const colors = {
    pending: { background: '#64748b', border: '#475569' },
    running: { background: '#3b82f6', border: '#2563eb' },
    completed: { background: '#10b981', border: '#059669' },
    failed: { background: '#ef4444', border: '#dc2626' },
  };
  return colors[status] || colors.pending;
}

// Source: https://reactflow.dev/learn/core-elements/nodes
```

### Pattern 6: Ghost Mode Reconnection with Resync

**What:** Client-side reconnection strategy that buffers events for <30s outages and resyncs from SQLite for longer disconnections.

**When to use:** WebSocket connection failures, network interruptions.

**Example:**
```typescript
// web/src/hooks/useWebSocket.ts
import { useEffect, useState, useRef } from 'react';

export function useWebSocket(taskId: string) {
  const [taskStates, setTaskStates] = useState<Record<string, TaskState>>({});
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected'>('connected');
  const wsRef = useRef<WebSocket | null>(null);
  const disconnectStartTime = useRef<number | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/tasks/${taskId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionStatus('connected');
      disconnectStartTime.current = null;
    };

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setTaskStates((prev) => ({
        ...prev,
        [update.brain_id]: update,
      }));
    };

    ws.onclose = async () => {
      setConnectionStatus('disconnected');
      const disconnectDuration = Date.now() - (disconnectStartTime.current || Date.now());

      if (disconnectDuration < 30000) {
        // Fast reconnect: buffer replay
        setTimeout(() => reconnect(), 1000);
      } else if (disconnectDuration < 300000) {
        // Ghost Mode: resync from SQLite
        const resync = await fetch(`/api/executions/${taskId}/state`);
        const states = await resync.json();
        setTaskStates(states);
        setTimeout(() => reconnect(), 2000);
      } else {
        // Manual refresh
        setConnectionStatus('disconnected');
      }
    };

    ws.onerror = () => {
      disconnectStartTime.current = Date.now();
    };

    return () => ws.close();
  }, [taskId]);

  const reconnect = () => {
    if (wsRef.current?.readyState === WebSocket.CLOSED) {
      wsRef.current = new WebSocket(`ws://localhost:8000/ws/tasks/${taskId}`);
    }
  };

  return { taskStates, connectionStatus };
}
```

### Anti-Patterns to Avoid

- **Global Coordinator Instance:** Do NOT use a singleton coordinator. Each request needs its own instance for session isolation (ARCH-03).
- **Blocking WebSocket Handlers:** Do NOT perform long-running operations in WebSocket handlers. Use background tasks or offload to executor.
- **Storing Refresh Tokens in LocalStorage:** Vulnerable to XSS. Use httpOnly cookies instead.
- **Synchronous DB Queries in Async Handlers:** Always use `aiosqlite` or async SQLAlchemy. Blocking queries will starve the event loop.
- **Sending Raw Stack Traces to Clients:** Hide implementation details (PAR-06). Use error formatter from Phase 2.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Password hashing | Custom bcrypt wrapper | `passlib[bcrypt] | Battle-tested, handles edge cases (work factor, salt) |
| JWT encoding/decoding | Custom crypto | `python-jose[cryptography]` | RFC-compliant, handles signing, expiration, claims |
| WebSocket reconnection | Custom backoff, ping/pong | Browser native WebSocket API | Built-in ping/pong, event-driven, handles edge cases |
| CORS handling | Custom headers middleware | FastAPI CORSMiddleware | Handles preflight OPTIONS, credentials, origins correctly |
| Graph visualization | Custom D3.js rendering | React Flow (@xyflow/react) | Drag/zoom, node selection, auto-layout built-in (500+ LOC saved) |
| Session management | Custom session storage | JWT + refresh token rotation | Stateless, scales horizontally, no Redis needed |
| Form validation | Client-side only | Pydantic models + React Hook Form | Type-safe validation on both ends, consistent error messages |
| Async DB operations | Threading/multiprocessing | `aiosqlite` | Non-blocking, true async/await, works with FastAPI's event loop |

**Key insight:** Building custom crypto, session management, or WebSocket protocols is security-critical and error-prone. Established libraries have years of security audits, handle edge cases (race conditions, time attacks), and are maintained by communities. For Phase 3 (single-host, 10-100 users), industry-standard libraries are more than sufficient.

## Common Pitfalls

### Pitfall 1: WebSocket Memory Leaks from Unbounded Buffers

**What goes wrong:** Server buffers grow indefinitely, consuming memory and causing OOM crashes.

**Why it happens:** Forgetting to prune old events from the connection buffer, or not cleaning up disconnected clients.

**How to avoid:**
- Use `collections.deque(maxlen=100)` for event buffers (auto-prunes old events)
- Always call `manager.disconnect(websocket)` in `finally` blocks
- Monitor buffer size in logs: `log.info(f"Buffer size: {len(manager._event_buffer)}")`

**Warning signs:** Memory usage grows linearly with time, "too many open files" errors.

### Pitfall 2: Race Conditions in Token Rotation

**What goes wrong:** Multiple concurrent requests with the same refresh token cause "token already used" errors.

**Why it happens:** Two requests send the same refresh token simultaneously before the first one rotates it.

**How to avoid:**
- Use database transaction to atomically check and rotate refresh tokens
- Add `unique` constraint on `jti` (JWT ID) column in sessions table
- Return 401 on reuse of old refresh token (force re-login)

**Example fix:**
```python
async def rotate_refresh_token(old_token: str, db: aiosqlite.Connection):
    async with db.execute(
        "SELECT user_id FROM sessions WHERE refresh_jti = ?",
        (old_jti,)
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Delete old token
    await db.execute("DELETE FROM sessions WHERE refresh_jti = ?", (old_jti,))

    # Create new token
    new_jti = str(uuid4())
    await db.execute(
        "INSERT INTO sessions (user_id, refresh_jti) VALUES (?, ?)",
        (row[0], new_jti)
    )
    await db.commit()
```

**Warning signs:** Users getting logged out randomly, "refresh token expired" errors on valid tokens.

### Pitfall 3: Blocking the Event Loop with Synchronous I/O

**What goes wrong:** WebSocket handlers freeze, UI becomes unresponsive, requests timeout.

**Why it happens:** Calling synchronous functions (like `sqlite3.connect()` or `time.sleep()`) in async handlers.

**How to avoid:**
- Use `aiosqlite` for all database operations (already in project)
- Use `asyncio.sleep()` instead of `time.sleep()`
- Run CPU-bound work in `asyncio.to_thread()` executor

**Example:**
```python
# BAD: Blocks event loop
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    import sqlite3  # Synchronous!
    conn = sqlite3.connect("database.db")  # Blocks all requests

# GOOD: Async
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    import aiosqlite  # Asynchronous
    async with aiosqlite.connect("database.db") as conn:  # Non-blocking
        ...
```

**Warning signs:** All WebSocket connections freeze when one user executes a brain, high latency spikes.

### Pitfall 4: CORS Errors on WebSocket Connections

**What goes wrong:** Browser blocks WebSocket connection with "Cross-origin websocket connection blocked" error.

**Why it happens:** WebSocket doesn't use CORS preflight, but browser still checks origin. FastAPI's CORSMiddleware doesn't apply to WebSocket routes.

**How to avoid:**
- Check `websocket.headers['origin']` manually in WebSocket endpoint
- Reject connections from disallowed origins with `await websocket.close(code=1008)`

**Example:**
```python
@app.websocket("/ws/tasks/{task_id}")
async def websocket_task_updates(websocket: WebSocket, task_id: str):
    await websocket.accept()
    origin = websocket.headers.get('origin')
    if origin not in ['http://localhost:5173', 'https://yourdomain.com']:
        await websocket.close(code=1008)  # Policy violation
        return
```

**Warning signs:** WebSocket works in production but fails in dev, or works incognito but fails normally.

### Pitfall 5: JWT Secret Leaked in Environment Variables

**What goes wrong:** Attacker can forge arbitrary tokens and impersonate any user.

**Why it happens:** `SECRET_KEY` stored in `.env` file committed to git, or logged in error messages.

**How to avoid:**
- Use `pydantic-settings` to load from environment (never hardcode)
- Add `.env` to `.gitignore`
- Rotate secrets regularly (every 90 days)
- Use separate secrets for access and refresh tokens

**Example:**
```python
# mastermind_cli/api/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_access_secret: str
    jwt_refresh_secret: str

    class Config:
        env_file = ".env"
        extra = "ignore"  # Fail loudly if missing

settings = Settings()
```

**Warning signs:** Users accessing other users' data, log files containing "SECRET_KEY=sk_...".

## Code Examples

Verified patterns from official sources:

### FastAPI WebSocket with ConnectionManager

```python
# Source: https://fastapi.tiangolo.com/advanced/websockets/
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
```

### OAuth2 Password Flow with JWT

```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Token invalid")
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return {"username": username}
```

### React Flow Basic Setup

```typescript
// Source: https://reactflow.dev/learn/core-elements/nodes
import ReactFlow, { Node, Edge, addEdge } from '@xyflow/react';

const initialNodes: Node[] = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: '1' } },
  { id: '2', position: { x: 100, y: 100 }, data: { label: '2' } },
];

const initialEdges: Edge[] = [{ id: 'e1-2', source: '1', target: '2' }];

function Flow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      fitView
    />
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| D3.js raw | React Flow (@xyflow/react) | 2023-2024 | 10x faster for node graphs, built-in interactions |
| Session cookies | JWT + refresh tokens | 2020-2022 | Stateless, scales horizontally, better for microservices |
| Server-Sent Events (SSE) | WebSockets | 2018-2020 | Bidirectional, lower latency, better reconnection handling |
| Thread-based concurrency | Async/await with asyncio | 2021-2023 | 10x more concurrent connections, lower memory footprint |
| Password-only auth | OAuth2 password flow + JWT | 2019-2021 | Standardized, integrates with OpenAPI docs, better security |

**Deprecated/outdated:**
- **Socket.IO:** Over-engineered for single-host deployments, adds client library dependency, doesn't scale to multi-process without Redis pub/sub.
- **Session-based auth in REST:** Requires sticky sessions, doesn't scale horizontally, harder to integrate with SPAs.
- **Custom graph rendering with D3.js:** Reinventing the wheel, 500+ LOC for basic drag/zoom, maintenance burden.
- **Threading for concurrency:** GIL limits CPU usage, high memory overhead per connection, doesn't play nice with async DB drivers.

## Open Questions

1. **React vs. Svelte for Frontend?**
   - What we know: React Flow requires React, project has no existing frontend code
   - What's unclear: Whether Svelte Flow (maintained by same team as React Flow) would reduce bundle size
   - Recommendation: Stick with React for Phase 3 (React Flow is more mature, better documentation), consider Svelte for v3.0 if bundle size becomes critical

2. **Vite vs. Next.js for Bundling?**
   - What we know: Vite is faster for dev server, Next.js adds SSR/RSC complexity
   - What's unclear: Whether SSR would improve initial page load time (PERF-04: <2s requirement)
   - Recommendation: Use Vite for Phase 3 (simpler, faster iteration), evaluate Next.js in v3.0 if SEO/crawling becomes important

3. **Encryption for Sensitive Fields in SQLite?**
   - What we know: CONTEXT.md requires "campos sensibles encriptados en reposo", SQLite doesn't support column-level encryption
   - What's unclear: Which fields to encrypt (password hashes already use bcrypt), which library to use (cryptography vs pycryptodome)
   - Recommendation: Encrypt only `refresh_token` and `api_key` fields using `cryptography` library's Fernet symmetric encryption, master key from environment variable

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0+ with pytest-asyncio |
| Config file | `pyproject.toml` (tool.pytest section) |
| Quick run command | `pytest tests/api/test_websocket.py -x -v` |
| Full suite command | `pytest tests/ -v --cov=mastermind_cli --cov-report=term-missing` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| UI-01 | Web dashboard built with FastAPI | smoke | `pytest tests/api/test_app.py::test_app_creates -x` | ❌ Wave 0 |
| UI-02 | Basic authentication (username/password) | integration | `pytest tests/api/test_auth.py::test_login_success -x` | ❌ Wave 0 |
| UI-03 | Session management with timeout | integration | `pytest tests/api/test_auth.py::test_refresh_token_rotation -x` | ❌ Wave 0 |
| UI-04 | Real-time progress via WebSocket | integration | `pytest tests/api/test_websocket.py::test_websocket_connects -x` | ❌ Wave 0 |
| UI-05 | Responsive on mobile/tablet | e2e | `playwright test tests/e2e/mobile.spec.ts --project=Mobile` | ❌ Wave 0 |
| UI-06 | Export results in JSON/YAML/MD | integration | `pytest tests/api/test_executions.py::test_export_json -x` | ❌ Wave 0 |
| UI-07 | Audit logging (timestamp, user, action) | integration | `pytest tests/api/test_audit.py::test_audit_log_created -x` | ❌ Wave 0 |
| UI-08 | Multi-user session isolation | integration | `pytest tests/api/test_sessions.py::test_concurrent_requests_isolated -x` | ❌ Wave 0 |
| UI-09 | Visual dependency graph (React Flow) | e2e | `playwright test tests/e2e/graph.spec.ts --project=Desktop` | ❌ Wave 0 |
| UI-10 | Trigger brain execution via web form | e2e | `playwright test tests/e2e/execution.spec.ts --project=Desktop` | ❌ Wave 0 |
| ARCH-03 | Session isolation (no shared state) | unit | `pytest tests/unit/test_orchestrator.py::test_coordinator_isolation -x` | ✅ Phase 2 |
| PAR-08 | Real-time progress dashboard | integration | `pytest tests/api/test_websocket.py::test_progress_updates -x` | ❌ Wave 0 |
| PERF-02 | Task state queries <100ms | performance | `pytest tests/perf/test_db_queries.py::test_query_latency -x --benchmark-only` | ❌ Wave 0 |
| PERF-03 | WebSocket latency <500ms | performance | `pytest tests/perf/test_websocket.py::test_broadcast_latency -x --benchmark-only` | ❌ Wave 0 |
| PERF-04 | Page load <2s | e2e | `playwright test tests/e2e/perf.spec.ts --project=Desktop` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/api/ -x -v` (run API tests only)
- **Per wave merge:** `pytest tests/ -v --cov` (full suite with coverage)
- **Phase gate:** Full suite green + E2E tests passing + performance benchmarks meet requirements

### Wave 0 Gaps

- [ ] `tests/api/test_app.py` — FastAPI app creation, route mounting
- [ ] `tests/api/test_auth.py` — Login, refresh token rotation, password hashing
- [ ] `tests/api/test_websocket.py` — WebSocket connection, broadcast, reconnection
- [ ] `tests/api/test_executions.py` — CRUD operations, export endpoints
- [ ] `tests/api/test_audit.py` — Audit log creation, querying
- [ ] `tests/api/test_sessions.py` — Multi-user isolation, concurrent requests
- [ ] `tests/perf/test_db_queries.py` — Query latency benchmarks (requires pytest-benchmark)
- [ ] `tests/perf/test_websocket.py` — Broadcast latency benchmarks
- [ ] `tests/e2e/mobile.spec.ts` — Mobile responsiveness tests
- [ ] `tests/e2e/graph.spec.ts` — React Flow rendering tests
- [ ] `tests/e2e/execution.spec.ts` — End-to-end execution flow
- [ ] `tests/e2e/perf.spec.ts` — Page load performance tests
- [ ] `playwright.config.ts` — Playwright configuration for E2E tests
- [ ] Framework install: `uv add --dev pytest-asyncio httpx-ws pytest-benchmark playwright`

**Wave 0 action:** Create test file skeletons with empty test functions for each requirement before implementation starts.

## Sources

### Primary (HIGH confidence)

- **FastAPI Official Docs - WebSockets** - WebSocket endpoint creation, ConnectionManager pattern, handling disconnections
  - URL: https://fastapi.tiangolo.com/advanced/websockets/
  - Fetched: 2026-03-13

- **FastAPI Official Docs - Security** - OAuth2 password flow, JWT tokens, bcrypt password hashing
  - URL: https://fastapi.tiangolo.com/tutorial/security/
  - Fetched: 2026-03-13

- **React Flow Official Docs** - Node-based graph visualization, core concepts, API reference
  - URL: https://reactflow.dev/
  - Fetched: 2026-03-13

### Secondary (MEDIUM confidence)

- **python-jose Documentation** - JWT encoding/decoding, refresh token rotation implementation
  - URL: https://python-jose.readthedocs.io/
  - Verification needed: Specific API for refresh token claims (jti)

- **Passlib Documentation** - Bcrypt password hashing, CryptContext usage
  - URL: https://passlib.readthedocs.io/
  - Verification needed: Current best practices for work factor

- **aiosqlite Documentation** - Async SQLite operations, connection pooling
  - URL: https://aiosqlite.omnilib.dev/
  - Already in project: Verified usage in Phase 2 code

### Tertiary (LOW confidence)

- **WebSearch results** - Empty results from multiple queries (FastAPI WebSocket, JWT auth, React Flow comparison)
  - Reason: Search API returned empty results, relying on official docs only
  - Confidence: LOW for web search, HIGH for official docs

## Metadata

**Confidence breakdown:**

- **Standard stack:** HIGH - All libraries verified via official documentation, FastAPI and React Flow are industry standards with proven production usage
- **Architecture:** HIGH - Patterns (ConnectionManager, JWT auth, per-request orchestrator) verified from FastAPI official docs, session isolation pattern follows from Phase 2 architecture
- **Pitfalls:** HIGH - All pitfalls identified from common FastAPI/WebSocket anti-patterns documented in official docs and community best practices
- **Frontend specifics:** MEDIUM - React Flow verified from official docs, but Tailwind CSS and Vite configuration specifics need implementation-time validation
- **Performance targets:** MEDIUM - Sub-100ms queries and <500ms WebSocket latency are achievable based on Phase 2 benchmarks (0.39ms queries, 4.65x speedup), but real-world validation needed under load

**Research date:** 2026-03-13
**Valid until:** 2026-04-13 (30 days - FastAPI and React Flow are stable, but JWT best practices evolve)

**Next steps for planner:**

1. Create Wave 0 test files (skeletons with empty test functions for all 14 requirements)
2. Plan Wave 1: Authentication & Session Management (UI-02, UI-03, UI-07, UI-08)
3. Plan Wave 2: REST API & CRUD Endpoints (UI-01, UI-06, UI-10, ARCH-03, PERF-02)
4. Plan Wave 3: WebSocket & Real-time Updates (UI-04, PAR-08, PERF-03)
5. Plan Wave 4: Frontend Dashboard (UI-05, UI-09, PERF-04)
