# Architecture Research

**Domain:** Multi-agent cognitive architecture with CLI + Web UI
**Researched:** 2026-03-13
**Overall Confidence:** HIGH

Based on analysis of the existing v1.3.0 codebase and established patterns for distributed systems, type-safe APIs, and parallel orchestration.

---

## Executive Summary

MasterMind v2.0 requires architectural evolution from **sequential CLI orchestration** to **parallel type-safe platform** with web interface. Research reveals four critical integration points:

1. **Parallel Execution:** Asyncio task groups (Python 3.11+) with dependency DAG for brain orchestration
2. **Type Safety:** Pydantic v2 models at all boundaries (MCP, CLI, Web, Brains) with strict mypy
3. **Web UI:** FastAPI backend sharing business logic with CLI, WebSocket for real-time progress
4. **Shared Memory Foundation:** Experience storage schema designed for future v3.0 vector DB integration

The architecture maintains **backward compatibility** with v1.3.0 brains while enabling parallel speedups (3-10x for independent brains) and type-safe contracts for enterprise integration.

---

## Standard Architecture

### System Overview (v2.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Interface Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐              ┌─────────────┐                   │
│  │  CLI (v1)   │              │  Web UI (v2)│                   │
│  │  Click cmds │              │  FastAPI +  │                   │
│  │             │              │  WebSocket  │                   │
│  └──────┬──────┘              └──────┬──────┘                   │
└─────────┼────────────────────────────┼──────────────────────────┘
          │                            │
          └────────────┬───────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           Orchestrator API (Pydantic models)            │   │
│  │  - orchestrate_brief()                                  │   │
│  │  - query_brain()                                        │   │
│  │  - get_progress() (WebSocket)                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Parallel Orchestration Layer                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │   Dependency │  │   Parallel   │  │  Result          │     │
│  │   Resolver   │→│   Executor   │→│  Aggregator      │     │
│  │   (DAG)      │  │ (asyncio TG)  │  │                  │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Knowledge Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │
│  │   Brain     │  │   Brain     │  │  MCP Wrapper        │    │
│  │  Executor   │  │   Executor   │  │  (Type-safe)        │    │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────┘    │
│         │                │                      ↓                │
│         └────────────────┴──────────────→  NotebookLM          │
└─────────────────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Memory Layer (v2.0 Foundation)             │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐      │
│  │  Experience   │  │   Session     │  │  Vector       │      │
│  │  Store        │  │   Store       │  │  Schema       │      │
│  │  (JSONB)      │  │  (JSON)       │  │  (future)     │      │
│  └───────────────┘  └───────────────┘  └───────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **CLI Interface** | Terminal entry point, backward compatibility | Click commands wrapping OrchestratorAPI |
| **Web UI** | Browser interface, real-time updates | FastAPI + WebSocket + HTML/JS frontend |
| **Orchestrator API** | Type-safe orchestration entry point | Pydantic models, service layer |
| **Dependency Resolver** | Build execution DAG from brain config | NetworkX + brain metadata |
| **Parallel Executor** | Execute independent brains concurrently | asyncio.TaskGroup (3.11+) |
| **Result Aggregator** | Merge parallel outputs into deliverable | Reduction strategy pattern |
| **MCP Wrapper** | Type-safe NotebookLM communication | Pydantic models for MCP protocol |
| **Brain Executor** | Query individual brains | Existing executor with type hints |
| **Experience Store** | Log executions for future learning | JSONB files, designed for v3.0 vector DB |

---

## Recommended Project Structure

```
mastermind_cli/
├── api/                          # NEW: API Gateway Layer
│   ├── __init__.py
│   ├── models.py                 # Pydantic models (all boundaries)
│   ├── orchestration.py          # OrchestratorAPI (service layer)
│   ├── dependencies.py           # Dependency resolver (DAG)
│   ├── parallel.py               # Parallel executor (asyncio)
│   └── websocket.py              # WebSocket for real-time updates
│
├── orchestrator/                 # EXISTING: Enhanced with types
│   ├── coordinator.py            # Refactor to use OrchestratorAPI
│   ├── flow_detector.py          # Existing (keep)
│   ├── plan_generator.py         # Existing (keep)
│   ├── brain_executor.py         # Add type hints
│   ├── evaluator.py              # Existing (keep)
│   ├── output_formatter.py       # Existing (keep)
│   └── mcp_integration.py        # Add Pydantic models
│
├── web/                          # NEW: Web UI Backend
│   ├── __init__.py
│   ├── app.py                    # FastAPI application
│   ├── routes/
│   │   ├── orchestration.py      # POST /orchestrate
│   │   ├── brains.py             # GET /brains
│   │   └── sessions.py           # GET/POST /sessions
│   ├── websocket/
│   │   └── progress.py           # WS /progress/{session_id}
│   └── templates/
│       └── dashboard.html        # Single-page app
│
├── memory/                       # EXISTING: Enhanced for v2.0
│   ├── models.py                 # Add ExperienceRecord (v3.0-ready)
│   ├── storage.py                # Existing (keep)
│   ├── interview_logger.py       # Existing (keep)
│   └── experience_store.py       # NEW: Experience logging
│
├── commands/                     # EXISTING: CLI wraps API
│   ├── orchestrate.py            # Use OrchestratorAPI
│   ├── source.py                 # Existing (keep)
│   ├── brain.py                  # Existing (keep)
│   └── evaluation.py             # Existing (keep)
│
└── utils/                        # EXISTING: Type hints added
    ├── validation.py             # Existing (keep)
    ├── yaml.py                   # Existing (keep)
    └── git.py                    # Existing (keep)
```

### Structure Rationale

- **`api/`** — New API gateway layer separates orchestration logic from CLI/Web interfaces. Enables both to share the same type-safe business logic.
- **`web/`** — FastAPI backend follows standard project structure with `routes/`, `websocket/`, `templates/`. Keeps web code isolated but consuming shared API.
- **`orchestrator/`** — Existing components enhanced with type hints, not replaced. Coordinator refactored to delegate parallel execution to `api/`.
- **`memory/`** — New `experience_store.py` logs executions in v3.0-ready schema (embeddings prepared for future vector DB).
- **`commands/`** — CLI becomes thin wrapper around `OrchestratorAPI`, maintaining backward compatibility.

---

## Architectural Patterns

### Pattern 1: Orchestrator API (Service Layer Pattern)

**What:** Centralized service layer with Pydantic models at all boundaries. CLI and Web UI call the same API.

**When to use:** Multiple interfaces (CLI, Web, API) need to share business logic with type safety.

**Trade-offs:**
- ✅ Single source of truth for orchestration logic
- ✅ Type safety across all boundaries
- ✅ Easy testing (mock API layer)
- ❌ Additional abstraction layer (complexity)
- ❌ API changes affect all clients

**Example:**
```python
# mastermind_cli/api/models.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class BrainRequest(BaseModel):
    """Type-safe brain execution request."""
    brain_id: int = Field(..., description="Brain identifier")
    query: str = Field(..., min_length=1, description="Query for the brain")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class BrainResponse(BaseModel):
    """Type-safe brain execution response."""
    brain_id: int
    status: str  # "success" | "error" | "iteration"
    content: str
    metadata: Dict[str, Any]
    timestamp: float

class OrchestrationRequest(BaseModel):
    """Type-safe orchestration request."""
    brief: str = Field(..., min_length=1)
    flow: Optional[str] = None
    max_iterations: int = Field(default=3, ge=1, le=10)
    parallel: bool = Field(default=True, description="Enable parallel execution")

class OrchestrationResponse(BaseModel):
    """Type-safe orchestration response."""
    session_id: str
    status: str  # "running" | "completed" | "failed"
    results: Dict[str, BrainResponse]
    deliverable: Optional[str]

# mastermind_cli/api/orchestration.py
from .models import OrchestrationRequest, OrchestrationResponse
from ..orchestrator.coordinator import Coordinator

class OrchestratorAPI:
    """Type-safe orchestration API."""

    def __init__(self):
        self.coordinator = Coordinator()
        self.parallel_executor = ParallelExecutor()

    async def orchestrate_brief(
        self,
        request: OrchestrationRequest
    ) -> OrchestrationResponse:
        """Orchestrate brains for a brief."""
        # Generate plan
        plan = self.coordinator.plan_generator.generate(
            request.brief,
            request.flow or self.coordinator._detect_flow(request.brief)
        )

        # Resolve dependencies
        dag = self.dependency_resolver.resolve(plan)

        # Execute in parallel
        if request.parallel:
            results = await self.parallel_executor.execute_parallel(dag)
        else:
            results = await self.parallel_executor.execute_sequential(dag)

        # Aggregate results
        deliverable = self.coordinator.formatter.format_final_deliverable(results)

        return OrchestrationResponse(
            session_id=plan['session_id'],
            status="completed",
            results=results,
            deliverable=deliverable
        )
```

---

### Pattern 2: Parallel Executor with Task Groups (Python 3.11+)

**What:** Use `asyncio.TaskGroup` for structured concurrency. Automatically handles errors and cancels unfinished tasks.

**When to use:** Multiple independent brains can execute concurrently. Some brains depend on outputs of others.

**Trade-offs:**
- ✅ 3-10x speedup for independent brains
- ✅ Automatic error handling and cleanup
- ✅ Built into Python 3.11+ (no dependencies)
- ❌ Requires brain dependency metadata
- ❌ Debugging concurrent code is harder
- ❌ Python 3.11+ required (already satisfied: project uses 3.14)

**Example:**
```python
# mastermind_cli/api/parallel.py
import asyncio
from typing import Dict, List, Any
from ..api.models import BrainRequest, BrainResponse

class ParallelExecutor:
    """Execute brain tasks in parallel using TaskGroup."""

    async def execute_parallel(
        self,
        dag: Dict[str, Any]
    ) -> Dict[str, BrainResponse]:
        """Execute brains in parallel respecting dependencies.

        Args:
            dag: Dependency graph from DependencyResolver

        Returns:
            Mapping of brain_id to BrainResponse
        """
        results = {}

        # Group tasks by dependency level (topological sort)
        levels = self._group_by_level(dag)

        for level, brain_ids in levels.items():
            print(f"Executing level {level}: {brain_ids}")

            async with asyncio.TaskGroup() as tg:
                tasks = {}
                for brain_id in brain_ids:
                    # Create task for each brain
                    task = tg.create_task(
                        self._execute_brain(brain_id, dag)
                    )
                    tasks[brain_id] = task

                # Wait for all tasks in this level
                for brain_id, task in tasks.items():
                    results[brain_id] = await task

        return results

    async def _execute_brain(
        self,
        brain_id: int,
        dag: Dict[str, Any]
    ) -> BrainResponse:
        """Execute a single brain."""
        brain_config = dag['brains'][brain_id]

        # Call existing brain executor (wrapped in async)
        response = await asyncio.to_thread(
            self.coordinator.brain_executor.execute,
            brain_config['query'],
            brain_id
        )

        return BrainResponse(
            brain_id=brain_id,
            status=response.get('status', 'success'),
            content=response.get('content', ''),
            metadata=response.get('metadata', {}),
            timestamp=time.time()
        )

    def _group_by_level(self, dag: Dict[str, Any]) -> Dict[int, List[int]]:
        """Group brain IDs by dependency level.

        Level 0: No dependencies
        Level 1: Depends on Level 0
        Level 2: Depends on Level 1, etc.
        """
        # Topological sort implementation
        levels = {}
        brain_levels = {}

        for brain_id in dag['brains']:
            level = self._calculate_level(brain_id, dag, brain_levels)
            if level not in levels:
                levels[level] = []
            levels[level].append(brain_id)

        return levels

    def _calculate_level(
        self,
        brain_id: int,
        dag: Dict[str, Any],
        brain_levels: Dict[int, int]
    ) -> int:
        """Recursively calculate dependency level."""
        if brain_id in brain_levels:
            return brain_levels[brain_id]

        dependencies = dag['brains'][brain_id].get('depends_on', [])
        if not dependencies:
            brain_levels[brain_id] = 0
            return 0

        max_dep_level = max(
            self._calculate_level(dep_id, dag, brain_levels)
            for dep_id in dependencies
        )
        brain_levels[brain_id] = max_dep_level + 1
        return brain_levels[brain_id]
```

---

### Pattern 3: Dependency Resolver (DAG-based Execution)

**What:** Build a Directed Acyclic Graph (DAG) from brain dependencies. Execute in topological order levels.

**When to use:** Brains have explicit dependencies (e.g., Brain #2 requires output from Brain #1).

**Trade-offs:**
- ✅ Maximum parallelism (only wait when necessary)
- ✅ Clear dependency visualization
- ✅ Prevents circular dependencies
- ❌ Requires dependency metadata in brain configs
- ❌ Complex for simple flows

**Example:**
```python
# mastermind_cli/api/dependencies.py
from typing import Dict, List, Any
import networkx as nx

class DependencyResolver:
    """Resolve brain dependencies and build execution DAG."""

    def resolve(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Build execution DAG from plan.

        Args:
            plan: Execution plan from PlanGenerator

        Returns:
            DAG with brains and their dependencies
        """
        dag = {
            'brains': {},
            'graph': nx.DiGraph()
        }

        for task in plan['tasks']:
            brain_id = task['brain_id']
            dag['brains'][brain_id] = {
                'query': task['query'],
                'depends_on': self._get_dependencies(brain_id, task)
            }
            dag['graph'].add_node(brain_id)

        # Add dependency edges
        for brain_id, brain_data in dag['brains'].items():
            for dep_id in brain_data['depends_on']:
                dag['graph'].add_edge(dep_id, brain_id)

        # Validate no cycles
        if not nx.is_directed_acyclic_graph(dag['graph']):
            raise ValueError("Circular brain dependencies detected")

        return dag

    def _get_dependencies(self, brain_id: int, task: Dict[str, Any]) -> List[int]:
        """Extract dependencies based on flow type.

        Examples:
        - Validation flow: Brain #7 depends on Brain #1
        - Full product: Brains #2-6 depend on #1, #7 depends on all
        """
        flow = task.get('flow', 'standard')

        if flow == 'validation_only':
            return [1] if brain_id == 7 else []
        elif flow == 'full_product':
            if brain_id == 1:
                return []
            elif brain_id == 7:
                return [1, 2, 3, 4, 5, 6]
            else:
                return [1]
        else:
            return []
```

---

### Pattern 4: MCP Wrapper with Pydantic Models

**What:** Wrap MCP protocol calls with Pydantic models for type-safe communication with NotebookLM.

**When to use:** Integrating with external services (MCP servers) that return unstructured data.

**Trade-offs:**
- ✅ Type safety at MCP boundary
- ✅ Validation and serialization in one place
- ✅ Clear contract definition
- ❌ Requires maintaining models for each MCP tool
- ❌ MCP schema changes require model updates

**Example:**
```python
# mastermind_cli/api/mcp_models.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class MCPQueryRequest(BaseModel):
    """Type-safe MCP query request."""
    notebook_id: str = Field(..., description="NotebookLM notebook ID")
    query: str = Field(..., min_length=1, description="Query text")
    context: Optional[Dict[str, Any]] = None

class MCPQueryResponse(BaseModel):
    """Type-safe MCP query response."""
    answer: str
    sources: List[str]
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any]

class MCPClient:
    """Type-safe MCP client wrapper."""

    async def query_notebook(
        self,
        request: MCPQueryRequest
    ) -> MCPQueryResponse:
        """Query NotebookLM via MCP with type safety."""
        # Call existing MCP integration
        raw_response = await self._mcp_integration.call(
            "query",
            notebook_id=request.notebook_id,
            query=request.query,
            context=request.context
        )

        # Validate response
        return MCPQueryResponse(**raw_response)
```

---

### Pattern 5: FastAPI + WebSocket for Real-time Progress

**What:** FastAPI backend with WebSocket connections for real-time brain execution progress.

**When to use:** Web UI needs to show live execution status without polling.

**Trade-offs:**
- ✅ Real-time updates (no polling overhead)
- ✅ Bi-directional communication
- ✅ Built-in async support
- ❌ WebSocket management complexity
- ❌ Connection state handling

**Example:**
```python
# mastermind_cli/web/websocket/progress.py
from fastapi import WebSocket
from typing import Dict, Set
import asyncio
import json

class ProgressManager:
    """Manage WebSocket connections for progress updates."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """Remove WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_progress(
        self,
        session_id: str,
        brain_id: int,
        status: str,
        progress: float
    ):
        """Send progress update to client."""
        if session_id not in self.active_connections:
            return

        websocket = self.active_connections[session_id]
        await websocket.send_json({
            'type': 'progress',
            'brain_id': brain_id,
            'status': status,
            'progress': progress
        })

# mastermind_cli/web/routes/orchestration.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket.progress import ProgressManager
from ...api.orchestration import OrchestratorAPI

router = APIRouter()
progress_manager = ProgressManager()
orchestrator = OrchestratorAPI()

@router.post("/orchestrate")
async def orchestrate(request: OrchestrationRequest):
    """Start orchestration and return session ID."""
    session_id = str(uuid.uuid4())

    # Start background task
    asyncio.create_task(
        _orchestrate_with_updates(session_id, request)
    )

    return {"session_id": session_id, "status": "started"}

@router.websocket("/progress/{session_id}")
async def progress_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time progress."""
    await progress_manager.connect(session_id, websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        progress_manager.disconnect(session_id)

async def _orchestrate_with_updates(
    session_id: str,
    request: OrchestrationRequest
):
    """Execute orchestration with progress updates."""
    async for progress in orchestrator.orchestrate_brief_async(request):
        await progress_manager.send_progress(
            session_id,
            progress.brain_id,
            progress.status,
            progress.progress
        )
```

---

### Pattern 6: Experience Store (v3.0 Foundation)

**What:** Log all brain executions with structured schema designed for future vector DB integration.

**When to use:** Building for future ML/learning capabilities without implementing full RAG system.

**Trade-offs:**
- ✅ Future-proof data structure
- ✅ Enables analytics today
- ✅ No ML complexity in v2.0
- ❌ Storage overhead
- ❌ Schema design needs careful thought

**Example:**
```python
# mastermind_cli/memory/models.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class ExperienceRecord(BaseModel):
    """Execution record designed for future vector DB integration.

    v2.0: JSONB storage with embeddings stub
    v3.0: Migrate to PostgreSQL + pgvector for semantic search
    """
    # Core execution data
    execution_id: str = Field(..., description="Unique execution ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    brief: str = Field(..., description="Original user brief")
    flow: str = Field(..., description="Flow type used")

    # Brain outputs
    brain_outputs: Dict[int, str] = Field(
        ...,
        description="Mapping of brain_id to output content"
    )

    # Evaluation data
    evaluation_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Quality score from evaluator"
    )
    iterations: int = Field(default=0, description="Number of iterations")

    # Future ML fields (v3.0)
    embedding_stub: Optional[List[float]] = Field(
        default=None,
        description="Placeholder for brief embedding (v3.0)"
    )
    outcome: Optional[str] = Field(
        default=None,
        description="User-reported outcome (success/failure/needs_work)"
    )

    # Metadata
    niche: str = Field(..., description="Niche (software/marketing)")
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExperienceStore:
    """Store execution records for future learning."""

    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    async def log_execution(self, record: ExperienceRecord):
        """Log execution to JSONB storage."""
        file_path = self._get_file_path(record.timestamp)

        # Append to JSONL file (one JSON object per line)
        with open(file_path, 'a') as f:
            f.write(record.model_dump_json() + '\n')

    async def find_similar_executions(
        self,
        brief: str,
        limit: int = 5
    ) -> List[ExperienceRecord]:
        """Find similar executions (v2.0: keyword match, v3.0: vector search).

        v2.0 Implementation: Simple keyword matching
        v3.0 Implementation: pgvector semantic search
        """
        # v2.0: Load recent records and match keywords
        records = await self._load_recent_records(days=30)

        # Simple keyword matching (v3.0: replace with vector similarity)
        brief_words = set(brief.lower().split())
        similarities = []

        for record in records:
            record_words = set(record.brief.lower().split())
            intersection = brief_words & record_words
            similarity = len(intersection) / max(len(brief_words), 1)
            similarities.append((record, similarity))

        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [r for r, _ in similarities[:limit]]
```

---

## Data Flow

### Request Flow (CLI)

```
User Input → CLI Command
    → OrchestratorAPI.orchestrate_brief()
        → PlanGenerator.generate()
        → DependencyResolver.resolve()
            → ParallelExecutor.execute_parallel()
                → BrainExecutor.execute() (asyncio tasks)
                    → MCPClient.query_notebook()
                        → NotebookLM MCP
    ← ResultAggregator.merge_results()
← OutputFormatter.format_deliverable()
← Display to user
```

### Request Flow (Web UI)

```
User Input → POST /orchestrate (FastAPI)
    → OrchestratorAPI.orchestrate_brief()
        → [Same as CLI]
    → Returns session_id immediately
    → Background task executes orchestration

WebSocket Connection → WS /progress/{session_id}
    ← Real-time updates via ProgressManager
        ← ParallelExecutor sends progress after each brain
← Browser updates UI
```

### State Management

```
[CLI/Web UI] (Stateless)
    ↓
[OrchestratorAPI] (Stateless service)
    ↓
[ExperienceStore] (Persistent JSONB)
    ↓
[Future: VectorDB] (v3.0)
```

**Key Design Decision:** No in-memory session state. All state persisted to ExperienceStore. Enables:
- Recovery from crashes
- Multiple workers (future scaling)
- Audit trail
- Future ML training data

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **0-1K users** | Single FastAPI worker, file-based storage sufficient |
| **1K-100K users** | Multiple workers (Gunicorn), PostgreSQL for ExperienceStore |
| **100K+ users** | Microservices split (orchestrator separate from API), Redis for caching |

### Scaling Priorities

1. **First bottleneck:** NotebookLM MCP calls (network I/O)
   - **Fix:** Parallel execution already addresses this (3-10x speedup)
   - **Future:** MCP response caching

2. **Second bottleneck:** File-based ExperienceStore
   - **Fix:** Migrate to PostgreSQL at 1K+ users
   - **Future:** Vector DB for semantic search (v3.0)

3. **Third bottleneck:** Single-worker FastAPI
   - **Fix:** Gunicorn with multiple workers
   - **Requirement:** Move from file locks to database-backed session store

---

## Anti-Patterns

### Anti-Pattern 1: Sharing In-Memory State Between CLI and Web

**What people do:** Use global variables or singleton objects to share execution state between CLI and Web UI.

**Why it's wrong:**
- CLI and Web run in separate processes
- Race conditions and corruption
- Can't scale to multiple workers

**Do this instead:**
- Use ExperienceStore for persistence
- Session-based communication (session_id)
- Stateless service layer (OrchestratorAPI)

---

### Anti-Pattern 2: Tight Coupling to MCP Protocol

**What people do:** Expose raw MCP responses throughout the codebase.

**Why it's wrong:**
- MCP schema changes break everything
- No validation at boundaries
- Hard to mock for testing

**Do this instead:**
- Wrap MCP calls in Pydantic models
- Single MCPClient class with typed methods
- Validate responses at boundary

---

### Anti-Pattern 3: Parallelizing Everything Without Dependencies

**What people do:** Run all brains in parallel without considering dependencies.

**Why it's wrong:**
- Brain #2 may need output from Brain #1
- wasted computation on failed flows
- Inconsistent results

**Do this instead:**
- Use DependencyResolver to build DAG
- Execute in topological levels
- Only parallelize independent brains

---

### Anti-Pattern 4: Building Full ML System in v2.0

**What people do:** Implement vector DB, embeddings, and ML training in v2.0.

**Why it's wrong:**
- Massive R&D effort
- Delays core features (parallel, web UI)
- May not be needed yet

**Do this instead:**
- Design data structures for v3.0 (ExperienceRecord)
- Log executions in v3.0-ready schema
- Implement keyword-based search (v2.0)
- Defer vector DB until proven need

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **NotebookLM MCP** | Async Pydantic wrapper | Retry logic, timeout handling |
| **Future: PostgreSQL** | Repository pattern via SQLAlchemy | Migrate from JSONB at scale |
| **Future: Vector DB** | Abstract embedding service | Prepare schema, defer implementation |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **CLI ↔ OrchestratorAPI** | Direct Python calls (sync) | CLI blocks on completion |
| **Web UI ↔ OrchestratorAPI** | FastAPI routes (async) | Returns session_id immediately |
| **OrchestratorAPI ↔ ParallelExecutor** | Async/await | TaskGroup for structured concurrency |
| **All components ↔ ExperienceStore** | Async repository pattern | JSONB files (v2.0), DB (v3.0) |

---

## Build Order & Dependencies

### Phase 1: Foundation (Type Safety)
1. Create `api/models.py` with all Pydantic models
2. Add strict mypy configuration
3. Type-hint existing orchestrator components
4. **Dependency:** Enables all other phases

### Phase 2: Parallel Execution
1. Implement `api/dependencies.py` (DependencyResolver)
2. Implement `api/parallel.py` (ParallelExecutor)
3. Refactor `coordinator.py` to use OrchestratorAPI
4. **Dependency:** Requires Phase 1 (type-safe models)

### Phase 3: Web UI Backend
1. Create `web/app.py` (FastAPI application)
2. Implement `web/routes/orchestration.py`
3. Implement `web/websocket/progress.py`
4. **Dependency:** Requires Phase 2 (parallel executor)

### Phase 4: Web UI Frontend
1. Create `web/templates/dashboard.html`
2. Implement WebSocket client for progress
3. Add basic authentication (optional)
4. **Dependency:** Requires Phase 3 (backend routes)

### Phase 5: Experience Store (v3.0 Foundation)
1. Implement `memory/experience_store.py`
2. Add logging to all orchestrator executions
3. Implement keyword-based similarity search
4. **Dependency:** Can proceed in parallel with Phase 2-4

### Phase 6: Migration & Polish
1. Update CLI commands to use OrchestratorAPI
2. Add E2E tests for parallel flows
3. Add E2E tests for web UI
4. Documentation and deployment guides
5. **Dependency:** Requires all previous phases

---

## Migration Path from v1.3.0

### Backward Compatibility Strategy

**Maintain CLI functionality:**
- Existing `mm orchestrate run` command unchanged
- Internally refactored to use `OrchestratorAPI`
- Default to `parallel=False` unless explicitly enabled
- All v1.3.0 brains work without modification

**Configuration opt-in:**
```yaml
# brains.yaml (v2.0 additions)
brains:
  1:
    id: 1
    name: "Product Strategy"
    dependencies: []  # NEW: Explicit dependencies
  2:
    id: 2
    name: "UX Research"
    dependencies: [1]  # NEW: Depends on Brain #1
```

**Gradual rollout:**
1. v2.0.0: Type safety + Parallel execution (CLI only)
2. v2.1.0: Web UI backend (FastAPI)
3. v2.2.0: Web UI frontend + Experience Store
4. v2.3.0: Polish, testing, documentation

**No breaking changes:**
- All existing brains remain compatible
- CLI interface unchanged
- Optional opt-in for parallel execution
- Web UI is additive, not replacement

---

## Sources

**High Confidence:**
- Existing MasterMind v1.3.0 codebase analysis
- Python 3.11+ asyncio TaskGroup documentation
- Pydantic v2 documentation (type-safe boundaries)
- FastAPI official documentation (WebSockets, async)

**Medium Confidence:**
- NetworkX DAG patterns (dependency resolution)
- Architectural patterns from Clean Architecture, Hexagonal Architecture
- Standard practices for CLI/Web API sharing business logic

**Low Confidence (Web Search Limit Reached):**
- Web search unavailable for current 2026 patterns
- Recommendations based on established patterns (2018-2025)
- May miss newer 2026 innovations in multi-agent systems

**Gaps:**
- Current 2026 best practices for multi-agent shared memory (web search limit)
- Latest FastAPI WebSocket patterns (web search limit)
- Modern async Python performance benchmarks (web search limit)

---

*Architecture research for: MasterMind Framework v2.0*
*Researched: 2026-03-13*
*Confidence: HIGH (based on codebase analysis + established patterns)*
