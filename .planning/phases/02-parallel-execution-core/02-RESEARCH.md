# Phase 2: Parallel Execution Core - Research

**Researched:** 2026-03-13
**Domain:** Asyncio parallel execution, DAG dependency resolution, SQLite task state persistence
**Confidence:** MEDIUM

## Summary

Phase 2 transforms the sequential orchestration engine into a dependency-aware parallel execution system. The core challenge is executing multiple brains concurrently when they have no dependencies, while respecting the DAG (Directed Acyclic Graph) structure defined in flow configurations. This requires implementing topological sort for dependency resolution, asyncio.TaskGroup for structured concurrency, SQLite for persistent task state, and graceful cancellation semantics.

**Primary recommendation:** Use Python 3.14's native asyncio.TaskGroup (no third-party libraries) with Kahn's algorithm for topological sort, SQLite with aiosqlite for async database operations, and cooperative cancellation with 5-second grace period.

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Dependency Resolution (Grafo DAG)**
- Validación **estática** en tiempo de carga del YAML — flows.yaml con ciclos ni siquiera se instancian
- Algoritmo de **Kahn** o **DFS** integrado directamente en `model_validator` de Pydantic v2
- **Fast-fail early**: si hay un ciclo, se lanza `ValidationError` inmediato antes de gastar tokens de IA
- Output del validador: lista ordenada de brains para ejecución en orden topológico
- **Zero dependencies**: no usar networkx o librerías de ciencia de datos

**Cancellation Semantics**
- **5 segundos de grace period** — brains in-flight tienen tiempo para guardar checkpoint en SQLite
- `asyncio.Event` o `CancellationToken` para propagar señal de cancelación
- Usuario pulsa Ctrl+C → Coordinator envía señal a todos los brains activos
- **Timeout**: después de 5 segundos, hard kill (fuerza bruta)
- Razón técnica: evitar transacciones corruptas en SQLite — COMMIT y cierre seguro de conexión

**State Persistence**
- **Solo en transitions**: `running→completed`, `running→failed`, `running→cancelled`
- Una sola transacción atómica por brain
- `model_dump_json()` de Pydantic v2 → convertir resultado a string JSON
- Guardar en columna `result` de tabla SQLite `tasks`
- **No updates periódicos** — evitar `database is locked` con 23 brains escribiendo concurrentemente

**Error Handling (Propagación)**
- **3 reintentos** con exponential backoff (1s, 2s, 4s) + jitter
- Si reintentos fallan → **Circuit Breaker** se abre
- **Blast radius controlado**: solo se cancelan dependientes directos del brain fallido
- Brains en ramas paralelas (independientes) siguen ejecutándose normalmente

**Resource Scheduling & Rate Limiting**
- **Capa 1: Preventiva (Per-API Semaphores)**: `asyncio.Semaphore` por proveedor de API
- Configuración en `providers.yaml`
- **Capa 2: Seguridad (Exponential Backoff with Jitter)**: si brain recibe `429 Too Many Requests` → espera exponencial + jitter aleatorio (±20%)

### Claude's Discretion

- Valor exacto de `max_concurrent_calls` por proveedor (default: NotebookLM=2, Claude=10)
- Algoritmo de backoff (exponential vs linear)
- Cantidad de jitter (±20% es razonable, pero puede ajustarse)
- Política de Circuit Breaker (qué tan rápido se abre/cierra)

### Deferred Ideas (OUT OF SCOPE)

- Distributed task queues (Celery/RQ) — single-host asyncio only
- Multi-machine orchestration — deferred to v3.0+
- Auto-scaling infrastructure — single-tenant deployment
- Real-time collaborative editing — separate phase

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PAR-01 | System resolves brain dependencies from flow configurations and builds DAG | Kahn's algorithm in Pydantic `@model_validator` |
| PAR-02 | System executes independent brains in parallel using asyncio.TaskGroup | Python 3.14 native TaskGroup (no third-party lib) |
| PAR-03 | System maintains centralized task state in SQLite database | aiosqlite for async, checkpoint-based persistence |
| PAR-04 | User can cancel running tasks with graceful shutdown | asyncio.Event with 5s grace period |
| PAR-05 | System provides task status indication (progress, current brain, ETA) | SQLite queries + progress tracking model |
| PAR-06 | System displays clear error messages when brains fail | Normalizer Pattern from Phase 1 + contextual errors |
| PAR-07 | System persists execution configurations for re-run | Pydantic `model_dump_json()` → SQLite |
| PAR-08 | System provides real-time progress dashboard via WebSocket | Deferred to Phase 3 (Web UI) |
| PAR-09 | System prevents false parallelism (no threading for I/O-bound work) | asyncio only, no threading |
| PERF-01 | Parallel execution achieves 3-10x speedup for independent brains vs sequential | Dependency-aware scheduling + semaphore throttling |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| asyncio | Built-in Python 3.14 | Structured concurrency with TaskGroup | Native support, no dependencies, stable API |
| aiosqlite | 0.20.0+ | Async SQLite operations | Standard for async SQLite, mature library |
| Pydantic | 2.12.5+ (existing) | Runtime validation + config models | Already in Phase 1, proven type safety |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest-asyncio | 0.24.0+ | Async test fixtures | Testing TaskGroup execution |
| faker | 30.0+ | Generate test data | Mock brain outputs in tests |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| asyncio.TaskGroup | trio | Trio has cleaner cancellation but less ecosystem support |
| aiosqlite | peewee-async | Peewee has ORM but adds complexity; raw SQL is sufficient |
| Kahn's algorithm | networkx | Networkx is overkill; 23 brains don't need scientific computing |
| aiosqlite | SQLite synchronous blocks | Would block event loop, defeating parallelism |

**Installation:**
```bash
uv add aiosqlite pytest-asyncio faker
```

## Architecture Patterns

### Recommended Project Structure

```
mastermind_cli/
├── orchestrator/
│   ├── coordinator.py          # Existing: add _execute_parallel()
│   ├── mcp_wrapper.py          # Existing: type-safe wrapper
│   ├── dependency_resolver.py  # NEW: Kahn's algorithm for DAG
│   ├── task_executor.py        # NEW: TaskGroup wrapper with semaphores
│   └── cancellation.py         # NEW: Grace period handler
├── state/
│   ├── __init__.py
│   ├── database.py             # NEW: aiosqlite connection manager
│   ├── models.py               # NEW: Task state Pydantic models
│   └── repositories.py         # NEW: CRUD operations for tasks
├── types/
│   ├── coordinator.py          # Existing: add FlowConfig, TaskState
│   └── parallel.py             # NEW: Parallel execution types
├── config/
│   ├── brains.yaml             # Existing
│   ├── flows.yaml              # Existing
│   └── providers.yaml          # NEW: API rate limits (semaphores)
└── commands/
    └── orchestrate.py          # Existing: add --parallel flag

tests/
├── unit/
│   ├── test_dependency_resolver.py   # Kahn's algorithm tests
│   ├── test_task_executor.py         # TaskGroup tests
│   ├── test_task_state_models.py     # Pydantic model tests
│   └── test_cancellation.py          # Grace period tests
├── integration/
│   ├── test_parallel_execution.py    # End-to-end parallel flow
│   └── test_database_operations.py   # SQLite CRUD tests
└── fixtures/
    ├── flows_dag.yaml          # Test flow configurations
    └──brains_mock.yaml         # Mock brain configurations
```

### Pattern 1: Topological Sort with Kahn's Algorithm

**What:** Dependency resolution using Kahn's algorithm to detect cycles and produce execution order.

**When to use:** Loading flow configurations from YAML, before executing brains.

**Example:**
```python
from pydantic import BaseModel, field_validator, Field
from typing import Dict, List

class FlowConfig(BaseModel):
    """Flow configuration with DAG validation."""
    flow_id: str = Field(..., description="Unique flow identifier")
    nodes: Dict[str, List[str]] = Field(..., description="brain_id -> list of dependencies")
    description: str = Field("", description="Flow description")

    @field_validator('nodes')
    @classmethod
    def validate_dag(cls, nodes: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Kahn's algorithm to detect cycles and validate DAG structure.

        Fast-fail early: if cycle detected, raise ValidationError before execution.
        This prevents wasting tokens on invalid configurations.
        """
        # Calculate in-degrees
        in_degree = {node: 0 for node in nodes}
        for node, deps in nodes.items():
            for dep in deps:
                if dep not in in_degree:
                    raise ValueError(f"Dependency '{dep}' not found in nodes")
                in_degree[node] += 1

        # Initialize queue with nodes having zero in-degree
        from collections import deque
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        topological_order = []

        while queue:
            current = queue.popleft()
            topological_order.append(current)

            # Reduce in-degree for dependent nodes
            for node, deps in nodes.items():
                if current in deps:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)

        # Check for cycle
        if len(topological_order) != len(nodes):
            cycle_nodes = [node for node in nodes if node not in topological_order]
            raise ValueError(f"Cycle detected in flow dependencies involving: {cycle_nodes}")

        return nodes

    def get_execution_order(self) -> List[str]:
        """Return topological order for brain execution."""
        # Re-run Kahn's to get order (could cache this)
        in_degree = {node: 0 for node in self.nodes}
        for node, deps in self.nodes.items():
            for dep in deps:
                in_degree[node] += 1

        from collections import deque
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for node, deps in self.nodes.items():
                if current in deps:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)

        return order
```

### Pattern 2: Structured Concurrency with asyncio.TaskGroup

**What:** Python 3.14's native TaskGroup for managing multiple concurrent tasks with automatic exception propagation.

**When to use:** Executing independent brains in parallel, handling cancellation, collecting results.

**Example:**
```python
import asyncio
from typing import Dict, Any, List

class ParallelExecutor:
    """Execute brains in parallel using asyncio.TaskGroup."""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.cancel_event = asyncio.Event()

    async def execute_brain(
        self,
        brain_id: str,
        query: str,
        mcp_client: Any
    ) -> Dict[str, Any]:
        """Execute a single brain with semaphore limiting.

        Args:
            brain_id: Brain identifier
            query: Query to execute
            mcp_client: MCP client for NotebookLM calls

        Returns:
            Brain output as dictionary

        Raises:
            asyncio.CancelledError: If task is cancelled
        """
        async with self.semaphore:
            # Check for cancellation before starting
            if self.cancel_event.is_set():
                raise asyncio.CancelledError("Task cancelled before execution")

            try:
                # Execute brain (reuse existing MCP wrapper)
                result = await mcp_client.query_brain(brain_id, query)
                return {
                    "brain_id": brain_id,
                    "status": "completed",
                    "result": result
                }
            except asyncio.CancelledError:
                # Graceful cancellation: save checkpoint
                await self._save_checkpoint(brain_id, "cancelled")
                raise
            except Exception as e:
                return {
                    "brain_id": brain_id,
                    "status": "failed",
                    "error": str(e)
                }

    async def execute_parallel(
        self,
        brains: List[Dict[str, Any]],
        mcp_client: Any
    ) -> Dict[str, Any]:
        """Execute multiple brains in parallel using TaskGroup.

        Args:
            brains: List of {brain_id, query} dicts
            mcp_client: MCP client instance

        Returns:
            Dictionary with results from all brains
        """
        results = {}

        try:
            async with asyncio.TaskGroup() as tg:
                tasks = []
                for brain_spec in brains:
                    task = tg.create_task(
                        self.execute_brain(
                            brain_spec["brain_id"],
                            brain_spec["query"],
                            mcp_client
                        )
                    )
                    tasks.append(task)

                # Collect results as they complete
                for task in tasks:
                    result = await task
                    results[result["brain_id"]] = result

        except* Exception as eg:  # ExceptionGroup
            # Handle multiple failures
            for exc in eg.exceptions:
                print(f"Task failed: {exc}")

        return results

    def cancel(self, grace_period: float = 5.0):
        """Cancel all running tasks with grace period.

        Args:
            grace_period: Seconds to wait for in-flight tasks to complete
        """
        self.cancel_event.set()

        # Wait for grace period (implement in execute_parallel)
        # After grace period, hard kill any remaining tasks

    async def _save_checkpoint(self, brain_id: str, status: str):
        """Save checkpoint state to database.

        Args:
            brain_id: Brain being executed
            status: Status to save (cancelled, failed, etc.)
        """
        # TODO: Implement in Phase 2 Plan 03
        pass
```

### Pattern 3: Async SQLite with aiosqlite

**What:** Non-blocking SQLite database operations using aiosqlite library.

**When to use:** Persisting task state, querying progress, saving execution results.

**Example:**
```python
import aiosqlite
from typing import Optional
from datetime import datetime, timezone

class TaskStateStore:
    """Async SQLite store for task state persistence."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Establish database connection and create schema."""
        self._connection = await aiosqlite.connect(self.db_path)
        await self._create_schema()

    async def _create_schema(self):
        """Create tasks table if not exists."""
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                brain_id TEXT NOT NULL,
                status TEXT NOT NULL,
                progress TEXT,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)

        # Create indexes for fast queries
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_brain_id ON tasks(brain_id)"
        )
        await self._connection.commit()

    async def create_task(
        self,
        task_id: str,
        brain_id: str,
        initial_status: str = "pending"
    ):
        """Create a new task record."""
        now = datetime.now(timezone.utc).isoformat()
        await self._connection.execute(
            """
            INSERT INTO tasks (id, brain_id, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (task_id, brain_id, initial_status, now, now)
        )
        await self._connection.commit()

    async def update_task(
        self,
        task_id: str,
        status: str,
        result: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Update task status atomically (checkpoint-based).

        Only updates on state transitions: pending->running, running->completed, etc.
        Uses a single transaction to avoid corruption.
        """
        now = datetime.now(timezone.utc).isoformat()

        if result:
            await self._connection.execute(
                """
                UPDATE tasks
                SET status = ?, result = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, result, now, task_id)
            )
        elif error:
            await self._connection.execute(
                """
                UPDATE tasks
                SET status = ?, error = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, error, now, task_id)
            )
        else:
            await self._connection.execute(
                """
                UPDATE tasks
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, now, task_id)
            )

        await self._connection.commit()

    async def get_task(self, task_id: str) -> Optional[dict]:
        """Retrieve task by ID."""
        cursor = await self._connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = await cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "brain_id": row[1],
                "status": row[2],
                "progress": row[3],
                "result": row[4],
                "error": row[5],
                "created_at": row[6],
                "updated_at": row[7]
            }
        return None

    async def get_tasks_by_status(self, status: str) -> list[dict]:
        """Retrieve all tasks with given status."""
        cursor = await self._connection.execute(
            "SELECT * FROM tasks WHERE status = ?",
            (status,)
        )
        rows = await cursor.fetchall()

        return [
            {
                "id": row[0],
                "brain_id": row[1],
                "status": row[2],
                "progress": row[3],
                "result": row[4],
                "error": row[5],
                "created_at": row[6],
                "updated_at": row[7]
            }
            for row in rows
        ]

    async def close(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()
```

### Anti-Patterns to Avoid

- **Threading for I/O-bound work:** Use asyncio, not threading. Threading introduces GIL contention and complexity without benefit for I/O-bound MCP calls.
- **Periodic database updates:** Only update on state transitions. Frequent updates cause "database is locked" errors with SQLite.
- **Synchronous database calls:** Never use `sqlite3` directly in async code. Use `aiosqlite` to avoid blocking the event loop.
- **Global state for cancellation:** Use `asyncio.Event` passed to tasks, not module-level globals. This enables multi-user session isolation in Phase 3.
- **Hard kills immediately:** Always allow grace period (5s) for in-flight tasks to save checkpoints. Hard kills corrupt SQLite transactions.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Async task management | Custom Task wrapper | asyncio.TaskGroup | Native in Python 3.14, handles exception groups automatically |
| Cycle detection | Custom DFS algorithm | Kahn's algorithm (standard) | Simpler, produces topological order as byproduct |
| Async SQLite | Thread pool executor | aiosqlite library | Purpose-built for async SQLite, mature and stable |
| Rate limiting | Custom throttling | asyncio.Semaphore | Built-in, prevents thundering herd elegantly |
| Retry logic | Custom backoff loop | tenacity library (optional) | Handles exponential backoff + jitter correctly |

**Key insight:** Custom parallel execution primitives are notoriously buggy. Python 3.14's TaskGroup is battle-tested through PEP 654 (Exception Groups). Building custom task scheduling risks deadlocks, race conditions, and exception swallowing.

## Common Pitfalls

### Pitfall 1: Blocking Event Loop with Synchronous Calls

**What goes wrong:** Using synchronous `sqlite3` or blocking I/O in async functions causes all concurrent tasks to stall.

**Why it happens:** SQLite's default Python module is synchronous. Calling it in an async function blocks the entire event loop.

**How to avoid:** Always use `aiosqlite` for database operations. Wrap any blocking I/O in `asyncio.to_thread()`.

**Warning signs:** Parallel execution is slower than sequential. Database operations cause noticeable pauses.

### Pitfall 2: Database Lock Contention

**What goes wrong:** Multiple tasks try to write to SQLite simultaneously, causing "database is locked" errors.

**Why it happens:** SQLite has limited write concurrency. With 23 brains writing checkpoints, contention is inevitable.

**How to avoid:** Use WAL (Write-Ahead Logging) mode, minimize write frequency (checkpoint-only), and batch writes when possible.

**Warning signs:** Intermittent `aiosqlite.OperationalError: database is locked` errors.

### Pitfall 3: Circular Dependencies in Flow Configs

**What goes wrong:** Flow configuration has circular dependencies (A→B→A), causing infinite loops or crashes.

**Why it happens:** Manual YAML editing without validation allows cycles.

**How to avoid:** Implement Kahn's algorithm in Pydantic `@model_validator` to reject cycles at load time.

**Warning signs:** Execution hangs indefinitely, brains never complete.

### Pitfall 4: Cancelling Without Grace Period

**What goes wrong:** Ctrl+C kills tasks immediately, leaving SQLite transactions open and database corrupted.

**Why it happens:** Using `task.cancel()` without allowing cleanup.

**How to avoid:** Implement cooperative cancellation with `asyncio.Event` and 5-second grace period for checkpointing.

**Warning signs:** Database file needs recovery after cancellation, partial results lost.

### Pitfall 5: False Parallelism with Threading

**What goes wrong:** Using threading "to make things faster" but actually slowing down due to GIL contention.

**Why it happens:** Misunderstanding that I/O-bound work (MCP calls) doesn't benefit from threading.

**How to avoid:** Use asyncio only. No threads. Thread switches are more expensive than async task yields.

**Warning signs:** CPU usage at 100% despite I/O-bound workload, minimal speedup.

## Code Examples

### Topological Sort with Cycle Detection

```python
# Source: Standard Kahn's algorithm
from pydantic import BaseModel, field_validator
from typing import Dict, List
from collections import deque

class FlowConfig(BaseModel):
    nodes: Dict[str, List[str]]  # brain_id -> dependencies

    @field_validator('nodes')
    @classmethod
    def validate_dag(cls, nodes: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Kahn's algorithm: detect cycles and validate DAG."""
        in_degree = {node: 0 for node in nodes}
        for node, deps in nodes.items():
            for dep in deps:
                if dep not in in_degree:
                    raise ValueError(f"Unknown dependency: {dep}")
                in_degree[node] += 1

        queue = deque([n for n, d in in_degree.items() if d == 0])
        processed = 0

        while queue:
            current = queue.popleft()
            processed += 1

            for node, deps in nodes.items():
                if current in deps:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)

        if processed != len(nodes):
            raise ValueError(f"Cycle detected in graph")

        return nodes

    def get_execution_order(self) -> List[str]:
        """Return topological order for execution."""
        in_degree = {node: 0 for node in self.nodes}
        for node, deps in self.nodes.items():
            for dep in deps:
                in_degree[node] += 1

        queue = deque([n for n, d in in_degree.items() if d == 0])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for node, deps in nodes.items():
                if current in deps:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)

        return order
```

### Parallel Execution with TaskGroup

```python
# Source: Python 3.14 asyncio documentation
import asyncio

async def execute_brains_parallel(
    brain_specs: List[Dict[str, str]],
    mcp_client: Any,
    semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    """Execute independent brains concurrently using TaskGroup."""

    async def run_with_limit(brain_id: str, query: str):
        async with semaphore:
            # Rate limiting per API
            return await mcp_client.query_brain(brain_id, query)

    results = {}

    try:
        async with asyncio.TaskGroup() as tg:
            tasks = {}
            for spec in brain_specs:
                task = tg.create_task(
                    run_with_limit(spec["brain_id"], spec["query"])
                )
                tasks[spec["brain_id"]] = task

            # Collect results as tasks complete
            for brain_id, task in tasks.items():
                results[brain_id] = await task

    except* Exception as eg:
        # Handle exception group (multiple failures)
        print(f"{len(eg.exceptions)} tasks failed")

    return results
```

### Graceful Cancellation with Checkpointing

```python
# Source: Cooperative cancellation pattern
import asyncio

class CancellableExecutor:
    def __init__(self, grace_period: float = 5.0):
        self.cancel_event = asyncio.Event()
        self.grace_period = grace_period

    async def execute_with_checkpoint(
        self,
        brain_id: str,
        query: str,
        db: TaskStateStore
    ):
        """Execute brain with cooperative cancellation."""
        task_id = f"task-{brain_id}"

        try:
            # Check for cancellation before starting
            if self.cancel_event.is_set():
                raise asyncio.CancelledError()

            # Mark as running
            await db.update_task(task_id, "running")

            # Execute brain (mock)
            result = await self._query_brain(brain_id, query)

            # Save result atomically
            await db.update_task(
                task_id,
                "completed",
                result=result
            )

        except asyncio.CancelledError:
            # Grace period: save checkpoint
            await db.update_task(task_id, "cancelled")
            raise

        except Exception as e:
            await db.update_task(
                task_id,
                "failed",
                error=str(e)
            )

    def cancel(self):
        """Signal cancellation to all running tasks."""
        self.cancel_event.set()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| threading.Thread | asyncio.TaskGroup | Python 3.11+ (PEP 654) | Structured concurrency, no race conditions |
| sqlite3 (sync) | aiosqlite | 2020+ | Non-blocking database operations |
| networkx for DAG | Kahn's algorithm (hand-rolled) | - | Zero dependencies for simple graphs |
| Custom retry loops | tenacity library | 2018+ | Production-grade exponential backoff + jitter |
| Global cancellation token | asyncio.Event per-executor | Python 3.4+ | Enables multi-user session isolation |

**Deprecated/outdated:**
- **asyncio.ensure_future()**: Use `asyncio.TaskGroup` instead for structured concurrency
- **threading for I/O**: Asyncio is superior for I/O-bound work (MCP calls)
- **synchronous SQLite**: Blocks event loop, use `aiosqlite` for async code

## Open Questions

1. **SQLite WAL mode configuration**
   - What we know: WAL mode improves write concurrency
   - What's unclear: Whether to enable WAL mode by default or make it configurable
   - Recommendation: Enable WAL mode in `connect()` method: `await conn.execute("PRAGMA journal_mode=WAL")`

2. **Semaphore defaults per provider**
   - What we know: NotebookLM is more restrictive than Claude API
   - What's unclear: Exact limits (default: NotebookLM=2, Claude=10)
   - Recommendation: Start with conservative defaults, make configurable in `providers.yaml`

3. **Task expiration policy**
   - What we know: Tasks can be stale if system crashes
   - What's unclear: How long to keep completed/failed tasks
   - Recommendation: Implement cleanup job in Phase 4, keep tasks for 30 days

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2+ (existing) + pytest-asyncio 0.24.0+ |
| Config file | `pyproject.toml` (existing) |
| Quick run command | `pytest tests/unit/test_dependency_resolver.py -x -v` |
| Full suite command | `pytest tests/ -v --cov=mastermind_cli` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PAR-01 | Topological sort detects cycles | unit | `pytest tests/unit/test_dependency_resolver.py::test_cycle_detection -x` | ❌ Wave 0 |
| PAR-01 | Topological sort produces valid order | unit | `pytest tests/unit/test_dependency_resolver.py::test_execution_order -x` | ❌ Wave 0 |
| PAR-02 | Independent brains execute in parallel | integration | `pytest tests/integration/test_parallel_execution.py::test_concurrent_execution -x` | ❌ Wave 0 |
| PAR-03 | Task state persists to SQLite | integration | `pytest tests/integration/test_database_operations.py::test_create_and_retrieve_task -x` | ❌ Wave 0 |
| PAR-04 | Cancellation with grace period | unit | `pytest tests/unit/test_cancellation.py::test_grace_period_checkpoint -x` | ❌ Wave 0 |
| PAR-05 | Task status queries return correct state | unit | `pytest tests/unit/test_task_state_models.py::test_status_transitions -x` | ❌ Wave 0 |
| PAR-06 | Clear error messages on brain failure | unit | `pytest tests/unit/test_task_executor.py::test_error_message_formatting -x` | ❌ Wave 0 |
| PAR-07 | Execution config saves/loads | integration | `pytest tests/integration/test_parallel_execution.py::test_config_persistence -x` | ❌ Wave 0 |
| PAR-09 | No threading used (asyncio only) | unit | `pytest tests/unit/test_task_executor.py::test_no_threading_used -x` | ❌ Wave 0 |
| PERF-01 | Parallel execution faster than sequential | integration | `pytest tests/integration/test_parallel_execution.py::test_speedup_factor -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/unit/ -x -q` (run unit tests for current module)
- **Per wave merge:** `pytest tests/ -v --cov=mastermind_cli --cov-report=term-missing` (full suite with coverage)
- **Phase gate:** Full suite green + coverage >80% on new code before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/unit/test_dependency_resolver.py` — Kahn's algorithm unit tests (PAR-01)
- [ ] `tests/unit/test_task_executor.py` — TaskGroup execution tests (PAR-02, PAR-09)
- [ ] `tests/unit/test_task_state_models.py` — Pydantic model validation (PAR-05, PAR-06)
- [ ] `tests/unit/test_cancellation.py` — Grace period and checkpoint tests (PAR-04)
- [ ] `tests/integration/test_parallel_execution.py` — End-to-end parallel flow (PAR-02, PERF-01)
- [ ] `tests/integration/test_database_operations.py` — SQLite CRUD tests (PAR-03, PAR-07)
- [ ] `pytest-asyncio` installation: `uv add --dev pytest-asyncio` — required for async test fixtures
- [ ] `tests/conftest.py` — shared fixtures for aiosqlite in-memory database, mock MCP client

## Sources

### Primary (HIGH confidence)

- **Python 3.14 asyncio documentation** — asyncio.TaskGroup, structured concurrency, exception groups
- **aiosqlite official docs** — Async SQLite operations, connection management
- **Pydantic v2 documentation** — `@model_validator` decorator, Field constraints, ConfigDict

### Secondary (MEDIUM confidence)

- **Kahn's algorithm (Wikipedia/standard references)** — Topological sorting algorithm
- **PEP 654 (Exception Groups)** — Exception handling in structured concurrency
- **pytest-asyncio documentation** — Async test fixtures and test execution

### Tertiary (LOW confidence)

- **Rate limiting patterns** — General asyncio semaphore usage (verify with official docs)
- **SQLite WAL mode** — Performance optimization (verify with SQLite docs)

## Metadata

**Confidence breakdown:**
- Standard stack: MEDIUM - aiosqlite and pytest-asyncio are standard, but asyncio.TaskGroup is relatively new (Python 3.11+)
- Architecture: MEDIUM - Kahn's algorithm is well-known, but integrating with Pydantic validators needs verification
- Pitfalls: HIGH - SQLite locking and async event loop blocking are well-documented issues

**Research date:** 2026-03-13
**Valid until:** 2026-04-13 (30 days - stable stack, but async APIs evolve)
