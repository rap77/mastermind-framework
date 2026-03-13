# Stack Research: MasterMind Framework v2.0

**Domain:** Cognitive Architecture Platform (Python)
**Researched:** 2026-03-13
**Confidence:** HIGH (based on official docs and established patterns)

---

## Executive Summary

MasterMind v2.0 requires three major capabilities: **parallel task execution**, **strict type safety**, and **web dashboard**. This stack prioritizes simplicity, maintainability, and compatibility with existing v1.3.0 code while adding production-ready infrastructure.

**Core recommendations:**
- **Parallel execution:** `asyncio` for I/O-bound tasks + `anyio` for portable async, avoid premature multiprocessing
- **Type safety:** `mypy strict` + `pydantic>=2.10` with type validation, not runtime type hints
- **Web dashboard:** `FastAPI` + `WebSocket` for real-time updates, NOT Streamlit/Dash (wrong use case)
- **Task queue:** Defer to v2.1+ - current sequential execution is sufficient for initial parallelization

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | 3.14+ | Core runtime | Latest stable with improved type hints, pattern matching, perf |
| **FastAPI** | 0.115+ | Web dashboard backend | Modern async framework, automatic OpenAPI, WebSocket native support |
| **WebSocket** | Native via FastAPI | Real-time dashboard updates | Built-in to FastAPI, no extra deps, bidirectional comms |
| **asyncio** | Standard library (3.14+) | Parallel task execution | I/O-bound tasks (MCP calls, API requests), zero overhead |
| **anyio** | 3.7+ | Portable async/await | Abstraction over asyncio/trio, future-proofs for async backends |
| **pydantic** | 2.10+ | Data validation + type safety | Runtime validation, JSON serialization, mypy plugin, V2 stable |

**Confidence:** HIGH - All are production-proven with official support

---

### Parallel Task Execution

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **asyncio** | Built-in (3.14+) | I/O-bound parallel tasks | MCP calls, HTTP requests, DB queries, file I/O |
| **anyio** | 3.7+ | Async backend abstraction | When you might switch backends (trio, curio) later |
| **concurrent.futures** | Built-in | CPU-bound parallel tasks | Heavy computation, data processing (rare for v2.0) |

**NOT recommended for v2.0:**
- ❌ **Celery** - Overkill for single-host orchestration, adds Redis/RabbitMQ dependency
- ❌ **multiprocessing** - Unnecessary complexity, Python GIL not an issue for I/O-bound tasks
- ❌ **RQ (Redis Queue)** - Adds Redis dependency, asyncio is sufficient for MVP

**Rationale:**
- MasterMind tasks are **I/O-bound** (waiting for NotebookLM MCP, Claude API, file reads)
- `asyncio` provides true concurrency for I/O without threading/multiprocessing overhead
- Brain orchestration is **single-host** (no distributed workers in v2.0)
- Task queues add operational complexity that's not needed yet

**Confidence:** HIGH - Established pattern for I/O-bound services

---

### Type Safety

| Tool | Version | Purpose | Configuration |
|------|---------|---------|---------------|
| **mypy** | 1.14+ | Static type checking | `--strict` mode, incremental caching |
| **pydantic** | 2.10+ | Runtime validation + types | `strict` mode, mypy plugin enabled |
| **types-*** | Varied | Type stubs for third-party | `types-PyYAML`, `types-redis`, etc. |

**mypy strict mode setup:**
```toml
[tool.mypy]
python_version = "3.14"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true

plugins = ["pydantic.mypy"]
```

**Pydantic v2 type safety:**
```python
from pydantic import BaseModel, ConfigDict

class BrainOutput(BaseModel):
    model_config = ConfigDict(strict=True)  # Strict validation

    brain_id: int
    status: Literal["success", "error", "pending"]
    content: str
    metadata: Dict[str, Any] = {}
    timestamp: datetime
```

**Key improvements over v1.3.0:**
- ✅ All function signatures must have type hints
- ✅ No `Any` types without explicit `# type: ignore` with justification
- ✅ Pydantic models catch invalid data at runtime
- ✅ mypy catches type bugs before runtime
- ✅ Better IDE autocomplete and refactoring

**Confidence:** HIGH - Industry standard for type-safe Python in 2025

---

### Web Dashboard Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **FastAPI** | 0.115+ | REST API + WebSocket | Native async, auto docs, type validation |
| **Uvicorn** | 0.34+ | ASGI server | Production async server, hot reload |
| **WebSocket** | Built-in to FastAPI | Real-time updates | No extra deps, native to FastAPI |
| **HTTPX** | 0.28+ | Async HTTP client | Used by dashboard to talk to orchestrator |

**Frontend (minimal):**
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **HTMX** | 2.0+ | Dynamic UI without SPA complexity | Server-driven, minimal JS |
| **Alpine.js** | 3.14+ | Light interactivity | Tiny, progressive enhancement |
| **Tailwind CSS** | 4.0+ | Styling | Utility-first, modern, fast dev |

**NOT recommended:**
- ❌ **Streamlit** - Wrong paradigm (data science dashboards, not orchestration UI)
- ❌ **Dash** - Too heavy, Plotly dependency, not suited for real-time orchestration
- ❌ **React/Vue SPA** - Overkill for v2.0, adds build complexity, HTMX is sufficient

**Architecture:**
```
FastAPI (port 8000)
├── REST endpoints: /brains, /sessions, /tasks
├── WebSocket: /ws/session/{id} (real-time updates)
└── Static files: / (serve HTMX frontend)

HTMX frontend (single HTML file + Tailwind)
├── Real-time progress via WebSocket
├── Async form submissions to FastAPI
└── No build step, no bundler
```

**Confidence:** HIGH - FastAPI is de facto standard for Python async APIs in 2025

---

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **structlog** | 25.0+ | Structured logging | When you need JSON logs, observability |
| **rich** | 13.9+ | Terminal output (existing) | Keep for CLI, add web dashboard alongside |
| **pytest-asyncio** | 0.25+ | Async test support | When testing async/await code |
| **httpx** | 0.28+ | Async HTTP client | For dashboard ↔ orchestrator communication |
| **websockets** | 14.0+ | WebSocket client (if needed) | For testing WebSocket endpoints |

**Existing dependencies to keep:**
- ✅ `click>=8.1.0` - CLI framework (coexists with web UI)
- ✅ `rich>=13.0.0` - Terminal formatting
- ✅ `pyyaml>=6.0` - Config parsing
- ✅ `gitpython>=3.1.0` - Git operations
- ✅ `semver>=3.0.0` - Versioning
- ✅ `pytest>=9.0.2` - Testing

---

## Installation

```bash
# Core v2.0 additions
uv add \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.34.0" \
    "anyio>=3.7.0" \
    "structlog>=25.0.0" \
    "httpx>=0.28.0" \
    "websockets>=14.0.0" \
    "pytest-asyncio>=0.25.0"

# Upgrade Pydantic to latest v2
uv add "pydantic>=2.10.0"

# Type stubs for mypy
uv add -D \
    "mypy>=1.14.0" \
    "types-PyYAML" \
    "types-redis"  # If you add Redis later

# Frontend (via CDN, no npm needed)
# - HTMX: https://unpkg.com/htmx.org@2.0.3
# - Alpine.js: https://cdn.jsdelivr.net/npm/alpinejs@3.14.0
# - Tailwind: CDN or standalone CLI
```

**pyproject.toml updates:**
```toml
[project]
dependencies = [
    # Existing v1.3.0 deps...
    "click>=8.1.0",
    "rich>=13.0.0",
    "pyyaml>=6.0",
    "gitpython>=3.1.0",
    "semver>=3.0.0",

    # v2.0 additions
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "anyio>=3.7.0",
    "pydantic>=2.10.0",
    "structlog>=25.0.0",
    "httpx>=0.28.0",
    "websockets>=14.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-cov>=7.0.0",
    "pytest-asyncio>=0.25.0",
    "mypy>=1.14.0",
    "types-PyYAML",
]

[tool.mypy]
python_version = "3.14"
strict = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = "mastermind_cli.*"
disallow_untyped_defs = true
```

---

## Alternatives Considered

### Parallel Execution

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **asyncio + anyio** | Celery + Redis | When you need distributed workers across multiple hosts (v3.0+) |
| **asyncio + anyio** | multiprocessing | When tasks are CPU-bound (ML model training, heavy computation) |
| **asyncio + anyio** | RQ + Redis | When you need persistent job queue with retry logic (v2.1+) |

**Why asyncio is right for v2.0:**
- Brains spend 90% of time waiting on I/O (MCP calls, API responses)
- No need for Redis/RabbitMQ complexity yet
- Can add Celery later without breaking changes
- `anyio` makes backend swappable if needed

---

### Type Safety

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **mypy strict + Pydantic** | Type-only (no runtime checks) | When performance is critical and you trust input |
| **mypy strict + Pydantic** | Runtime only (no mypy) | When you don't care about IDE support or early error detection |
| **mypy strict + Pydantic** | Pydantic v1 | Never - v2 is superior in all aspects |

**Why strict mode + Pydantic:**
- Catch bugs at dev time (mypy) AND runtime (Pydantic)
- Pydantic v2 is 5-50x faster than v1
- `strict` mode prevents silent type coercion bugs
- Future ML feature needs data validation anyway

---

### Web Dashboard

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **FastAPI + HTMX** | Streamlit | When building data science notebooks, not orchestration UI |
| **FastAPI + HTMX** | Dash | When building Plotly-heavy analytics dashboards |
| **FastAPI + HTMX** | React SPA | When you need complex client-side state (v3.0+) |
| **FastAPI + HTMX** | Django Admin | When you need CRUD CMS, not custom orchestration |

**Why FastAPI + HTMX:**
- FastAPI: Native async, type-safe, automatic OpenAPI docs
- HTMX: No build step, server-driven, works with REST
- Cohesive with existing Python stack
- Can migrate to React later without backend changes

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **Celery** | Adds Redis/RabbitMQ, overkill for single-host | asyncio + anyio (now), Celery (v3.0 if distributed) |
| **multiprocessing** | GIL not an issue for I/O-bound tasks, complex IPC | asyncio for I/O, concurrent.futures for CPU |
| **Streamlit** | Wrong paradigm (notebook-style, not orchestration UI) | FastAPI + HTMX for custom dashboards |
| **Dash** | Plotly dependency too heavy, not suited for real-time | FastAPI + HTMX + Chart.js if needed |
| **React SPA** | Build complexity, overkill for MVP | HTMX for v2.0, React (optional v3.0) |
| **Pydantic v1** | Deprecated, slower, worse type inference | Pydantic v2.10+ |
| **Flask** | Not async-first, less type-safe than FastAPI | FastAPI (built on Starlette, async-native) |
| **Tornado** | Legacy, less maintained, not type-safe | FastAPI + WebSocket |

---

## Stack Patterns by Variant

### If parallel I/O tasks (MCP calls, HTTP requests):
- Use `asyncio.gather()` for concurrent execution
- Example: Run 5 brains in parallel, wait for all
```python
async def execute_brains_parallel(brain_tasks: List[Task]) -> List[Result]:
    return await asyncio.gather(*[execute_brain(t) for t in brain_tasks])
```

### If CPU-bound tasks (data processing, ML):
- Use `concurrent.futures.ProcessPoolExecutor`
- Example: Parallel data transformation
```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor() as executor:
    results = executor.map(cpu_bound_function, data)
```

### If dependency-aware orchestration (Brain #2 waits for #1):
- Use `asyncio.Task` with explicit `await` on dependencies
- Example: Brain #2 waits for Brain #1 output
```python
brain1_task = asyncio.create_task(execute_brain(1, task))
await brain1_task  # Ensure Brain #1 completes
brain2_result = await execute_brain(2, brain1_task.result())  # Use output
```

---

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| **pydantic 2.10+** | Python 3.14+ | V2 requires 3.10+, 3.14 recommended |
| **fastapi 0.115+** | pydantic 2.0+ | FastAPI requires Pydantic V2 |
| **mypy 1.14+** | Python 3.14+ | Full support for 3.14 features |
| **anyio 3.7+** | Python 3.9+ | asyncio backend default, trio optional |
| **uvicorn 0.34+** | Python 3.9+ | ASGI server, works with FastAPI |
| **pytest-asyncio** | pytest 9.0+ | Use `@pytest.mark.asyncio` |

**Backward compatibility with v1.3.0:**
- ✅ All existing brains remain compatible (CLI still works)
- ✅ NotebookLM MCP integration unchanged
- ✅ Brain YAML configs unchanged
- ✅ Can run CLI and web dashboard simultaneously

---

## Architecture Impact

### Before (v1.3.0 - Sequential)
```
Coordinator → Brain #1 (sequential) → Brain #2 → ... → Brain #7
```

### After (v2.0 - Parallel + Type-Safe + Web)
```
FastAPI (port 8000)
├── REST API: POST /orchestrate
├── WebSocket: /ws/session/{id}
└── Coordinator (async)
    ├── Parallel: asyncio.gather(Brain #1, #3, #5)
    ├── Sequential: Brain #2 awaits Brain #1
    └── Type-safe: Pydantic models validate all data
```

---

## Migration Path from v1.3.0

### Phase 1: Type Safety (PAR-01, TS-01, TS-02, TS-03)
1. Add `mypy --strict` to CI/CD
2. Add type hints to all public functions
3. Convert data classes to Pydantic models
4. Fix type errors incrementally

### Phase 2: Parallel Execution (PAR-01, PAR-02)
1. Refactor `Coordinator.execute()` to `async def`
2. Use `asyncio.gather()` for independent brains
3. Add dependency graph in `PlanGenerator`
4. Topological sort for execution order

### Phase 3: Web Dashboard (UI-01, UI-02, UI-03)
1. Create FastAPI app (`api/app.py`)
2. Add WebSocket endpoint for real-time updates
3. Build HTMX frontend (`frontend/dashboard.html`)
4. Connect orchestrator to WebSocket events

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| Parallel execution (asyncio) | HIGH | Industry standard for I/O-bound services since 3.7 |
| Type safety (mypy + Pydantic) | HIGH | Pydantic v2 stable, mypy mature, official support |
| Web dashboard (FastAPI + HTMX) | HIGH | FastAPI is #1 Python async framework, HTMX proven |
| Defer Celery/RQ | HIGH | Consensus: premature optimization for single-host |
| Avoid Streamlit/Dash | HIGH | Wrong paradigm (notebook vs orchestration) |
| HTMX over React | MEDIUM | UX tradeoff, but valid for v2.0 simplicity |

**Overall:** HIGH confidence - All choices are established, production-proven technologies with official support and large communities.

---

## Sources

- **Python asyncio docs** - Official documentation for async/await, concurrency
- **FastAPI docs** - Official FastAPI documentation, WebSocket support
- **Pydantic v2 docs** - Official Pydantic V2 migration guide, performance notes
- **anyio docs** - Portable async library, backend abstraction
- **mypy docs** - Static type checking, strict mode configuration
- **HTMX docs** - Server-driven dynamic UI without SPA complexity
- **Real Python** - "Async IO in Python: A Complete Walkthrough" (MEDIUM confidence - tutorial)
- **Two Scoops of Django 3.x** - Type safety patterns (MEDIUM confidence - book reference)

---

*Stack research for: MasterMind Framework v2.0*
*Researched: 2026-03-13*
*Confidence: HIGH*
