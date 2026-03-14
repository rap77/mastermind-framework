# PRP-03-00: Pure Function Architecture (Simplification Cascade)

**Status:** Ready to Implement
**Priority:** Critical (v2.0 foundation)
**Estimated Time:** 6-8 hours
**Dependencies:** Existing v1.3.0 codebase

---

## Executive Summary

Implementar **Pure Function Architecture** para resolver 7 pitfalls identificados en v2.0 planning. **Un insight elimina múltiples problemas:** "Si cada brain es una FUNCIÓN PURA (input → output), NO necesitamos estado compartido."

This reduces complexity by **80%** (40+ files → 8 files, ~3000 LOC → ~600 LOC) while enabling multi-user safety, avoiding MCP bottlenecks, and simplifying auth.

---

## Context from Simplification Cascade

### The Problem

Current `Coordinator` class has global state (see lines 45-48):
```python
# mastermind_cli/orchestrator/coordinator.py
self.current_plan: dict[str, Any] | None = None
self.execution_results: dict[str, Any] = {}
self.iteration_count = 0
self.rejection_count = 0
```

**7 Pitfalls this creates:**
1. Multi-orchestrator race (can't have concurrent users)
2. MCP bottleneck (concurrent requests break MCP protocol)
3. Dependency blind spot (hidden state sharing)
4. Auth state schism (CLI vs Web UI auth)
5. False parallelism (mixing sync/async)
6. Type safety half-migration (Any types everywhere)
7. Backward compatibility breaking (v1.x brains break)

### The Solution

**Pure Function Architecture:**
- Brains are pure functions: `input → output` (no state access)
- Coordinator is stateless (per-request instances)
- MCP sequential by dependency level (no rate limit issues)
- API Key auth (simple, works for CLI + Web)
- Legacy brain wrapper (backward compatible)

---

## External Resources

### Pydantic v2 Documentation
- https://docs.pydantic.dev/latest/concepts/models/ - BaseModel for interfaces
- https://docs.pydantic.dev/latest/concepts/strict_mode/ - Strict type validation
- https://docs.pydantic.dev/latest/api/validate_call/ - Runtime validation decorator

### Python asyncio.TaskGroup
- https://docs.python.org/3.11/library/asyncio.html#asyncio.TaskGroup - Structured concurrency
- https://docs.python.org/3.11/library/asyncio-task.html#task-groups - Task groups for parallel execution

### FastAPI Dependency Injection
- https://fastapi.tiangolo.com/tutorial/dependencies/ - Depends() for per-request injection
- https://fastapi.tiangolo.com/advanced/dependencies/ - Advanced dependency patterns

### Type Safety Best Practices
- https://mypy.readthedocs.io/en/stable/strict_mode.html - mypy strict mode
- https://docs.pydantic.dev/latest/concepts/types/ - Pydantic type catalog

---

## Implementation Blueprint

### Architecture Overview

**Before (Complex):**
```
Orchestrator (Global State)
    ↓
Brains (Share implicit state via orchestrator.state)
    ↓
MCP Client (Concurrent requests)
    ↓
Database (Execution state)
```

**After (Simple):**
```
Coordinator (Stateless, per-request)
    ↓
Pure Functions (Input → Output, no state)
    ↓
MCP Client (Sequential by dependency level)
    ↓
SQLite (Logs only)
```

### Phase 1: Pure Function Interfaces (45 min)

Create Pydantic models for all brain inputs/outputs:

```python
# mastermind_cli/types/interfaces.py
from pydantic import BaseModel, Field
from typing import Literal

# ===== INPUTS =====

class Brief(BaseModel):
    """User brief input."""
    problem_statement: str = Field(..., min_length=10)
    context: str = ""
    constraints: list[str] = []

class BrainInput(BaseModel):
    """Generic brain input - all brains inherit from this."""
    brief: Brief
    additional_context: dict = {}

# ===== OUTPUTS =====

class ProductStrategy(BaseModel):
    """Brain #1 output."""
    positioning: str
    target_audience: str
    key_features: list[str]
    success_metrics: list[str]

class UXResearch(BaseModel):
    """Brain #2 output."""
    user_journeys: list[dict]
    pain_points: list[str]
    opportunities: list[str]

class FrontendDesign(BaseModel):
    """Brain #4 output - depends on strategy + UX."""
    component_hierarchy: dict
    state_management: str
    styling_approach: str

# ===== PURE FUNCTION SIGNATURE =====

def brain_product_strategy(
    input: BrainInput,
    mcp_client: MCPClient  # Injected, not global
) -> ProductStrategy:
    """
    Pure function: input → output, no state access.

    NO self.state access
    NO other_brain.output access
    Only returns ProductStrategy
    """
    knowledge = mcp_client.query_notebooklm(
        notebook_id="PRODUCT_NOTEBOOK_ID",
        query=input.brief.problem_statement
    )
    # Process knowledge into strategy...
    return ProductStrategy(
        positioning=...,
        target_audience=...,
        key_features=...,
        success_metrics=...
    )
```

### Phase 2: Stateless Coordinator (1 hour)

```python
# mastermind_cli/orchestrator/stateless_coordinator.py
from typing import Protocol
from dataclasses import dataclass

class MCPClient(Protocol):
    """MCP client protocol."""
    def query_notebooklm(self, notebook_id: str, query: str) -> str: ...

@dataclass
class CoordinatorConfig:
    """Coordinator configuration (immutable)."""
    mcp_client: MCPClient
    enable_logging: bool = True

class StatelessCoordinator:
    """
    Stateless coordinator - NO instance variables.

    Each request creates a new instance.
    Multi-user safe by design.
    """

    def __init__(self, config: CoordinatorConfig):
        """Store only immutable config."""
        self.config = config

    async def execute_flow(
        self,
        brief: Brief,
        brains: list[str]  # e.g., ["brain-1", "brain-2", "brain-4"]
    ) -> dict[str, BaseModel]:
        """
        Execute flow with wave-based parallelism.

        Returns dict of {brain_id: output_model}
        """
        from asyncio import TaskGroup

        # Resolve dependencies into waves
        waves = self._resolve_waves(brains)

        results = {}

        # Execute wave by wave (sequential waves, parallel within wave)
        async with TaskGroup() as tg:
            for wave in waves:
                wave_results = {}
                for brain_id in wave:
                    # Each brain is independent - pure function
                    task = tg.create_task(
                        self._execute_brain(brain_id, brief, results)
                    )
                    wave_results[brain_id] = task

                # Wait for all brains in this wave
                for brain_id, task in wave_results.items():
                    results[brain_id] = await task

        return results

    async def _execute_brain(
        self,
        brain_id: str,
        brief: Brief,
        previous_results: dict[str, BaseModel]
    ) -> BaseModel:
        """Execute single brain - pure function call."""
        from . import brain_functions  # Module of pure functions

        # Get brain function
        brain_func = getattr(brain_functions, brain_id)

        # Gather inputs from previous results
        brain_input = self._prepare_input(brain_id, brief, previous_results)

        # Call pure function
        output = brain_func(brain_input, mcp_client=self.config.mcp_client)

        return output

    def _resolve_waves(self, brains: list[str]) -> list[list[str]]:
        """Group brains into waves based on dependencies.

        Reuse existing DependencyResolver logic!
        """
        from .dependency_resolver import DependencyResolver
        resolver = DependencyResolver(registry=self.config.brain_registry)
        return resolver.resolve(brains)
```

### Phase 3: Simplified Auth (API Keys) (30 min)

```python
# mastermind_cli/auth/api_keys.py
from pydantic import BaseModel
from typing import Optional
import os

class APIKey(BaseModel):
    """API key model."""
    key: str
    owner: str
    created_at: str

def validate_api_key(api_key: str) -> bool:
    """
    Validate API key against database or environment.

    CLI: Uses MM_API_KEY environment variable
    Web: Validates against SQLite users table
    """
    # Environment variable (CLI)
    if api_key == os.getenv("MM_API_KEY"):
        return True

    # Database (Web UI)
    from .database import get_db
    db = get_db()
    return db.query_api_key(api_key)

# FastAPI integration
from fastapi import Header, HTTPException

async def get_current_api_key(
    x_api_key: str = Header(..., alias="X-API-Key")
) -> APIKey:
    """FastAPI dependency for API key validation."""
    if not validate_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return APIKey(key=x_api_key, owner="user", created_at="...")
```

### Phase 4: Legacy Brain Wrapper (45 min)

```python
# mastermind_cli/compatibility/legacy_wrapper.py
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class LegacyBrainAdapter(Generic[T]):
    """
    Wraps legacy brains (with state) to pure function interface.

    Allows v1.x brains to work in v2.0 without modification.
    """

    def __init__(
        self,
        legacy_brain_class: type,
        output_model: type[T]
    ):
        self.legacy_brain = legacy_brain_class()
        self.output_model = output_model

    def __call__(
        self,
        input: BrainInput,
        mcp_client: MCPClient
    ) -> T:
        """
        Call legacy brain with LOCAL context (not global).

        Creates isolated orchestrator for this execution only.
        """
        # Create LOCAL orchestrator (not shared)
        from ..orchestrator.coordinator import Coordinator
        local_orchestrator = Coordinator(
            formatter=None,
            use_mcp=True,
            enable_logging=False
        )

        # Call legacy brain with local context
        result = self.legacy_brain.execute(
            brief=input.brief.problem_statement,
            orchestrator=local_orchestrator  # LOCAL, not global
        )

        # Convert dict to Pydantic model
        return self.output_model(**result)

# Usage
legacy_wrapper = LegacyBrainAdapter(
    legacy_brain_class=OldProductStrategyBrain,
    output_model=ProductStrategy
)

# Now callable as pure function
strategy = legacy_wrapper(input, mcp_client)
```

---

## Tasks (in Order)

### Task 1: Create Interface Types (30 min)
- [ ] Create `mastermind_cli/types/interfaces.py`
- [ ] Define `Brief`, `BrainInput` base models
- [ ] Define `ProductStrategy`, `UXResearch`, `FrontendDesign` outputs
- [ ] Add strict mode validation (Field constraints)
- [ ] Write tests for model validation

### Task 2: Create Brain Functions Module (45 min)
- [ ] Create `mastermind_cli/orchestrator/brain_functions.py`
- [ ] Migrate brain #1 to pure function signature
- [ ] Migrate brain #2 to pure function signature
- [ ] Update imports to use new interfaces
- [ ] Write tests for pure function behavior (no side effects)

### Task 3: Implement Stateless Coordinator (1 hour)
- [ ] Create `mastermind_cli/orchestrator/stateless_coordinator.py`
- [ ] Implement `CoordinatorConfig` dataclass
- [ ] Implement `StatelessCoordinator.execute_flow()` with TaskGroup
- [ ] Implement `_resolve_waves()` reusing DependencyResolver
- [ ] Implement `_execute_brain()` pure function caller
- [ ] Write multi-user tests (parallel execution)

### Task 4: API Key Auth System (30 min)
- [ ] Create `mastermind_cli/auth/api_keys.py`
- [ ] Implement `validate_api_key()` for CLI (env var)
- [ ] Implement `validate_api_key()` for Web (SQLite)
- [ ] Create FastAPI dependency `get_current_api_key`
- [ ] Update CLI to use `MM_API_KEY` environment variable
- [ ] Write auth tests

### Task 5: Legacy Brain Wrapper (45 min)
- [ ] Create `mastermind_cli/compatibility/legacy_wrapper.py`
- [ ] Implement `LegacyBrainAdapter` generic class
- [ ] Test wrapper with existing brain #1
- [ ] Verify wrapper isolates state (no global pollution)
- [ ] Write backward compatibility tests

### Task 6: Update CLI Commands (30 min)
- [ ] Update `commands/orchestrate.py` to use `StatelessCoordinator`
- [ ] Add API key validation
- [ ] Update error messages for new architecture
- [ ] Test CLI with pure function brains
- [ ] Test CLI with legacy wrapped brains

### Task 7: Database Logger (30 min)
- [ ] Create `mastermind_cli/state/logger.py`
- [ ] Implement execution logging to SQLite
- [ ] Log brain inputs, outputs, timestamps
- [ ] Add query interface for logs
- [ ] Write logger tests

### Task 8: Integration Testing (1 hour)
- [ ] Create `tests/integration/test_pure_function_arch.py`
- [ ] Test multi-user scenario (5 concurrent requests)
- [ ] Test MCP sequential execution (no rate limit errors)
- [ ] Test legacy brain wrapper (v1.x compatibility)
- [ ] Test auth (CLI + API key)
- [ ] Performance benchmark (vs old coordinator)

### Task 9: Documentation (30 min)
- [ ] Update `docs/ARCHITECTURE.md` with new architecture
- [ ] Create `docs/PURE_FUNCTION_MIGRATION.md` guide
- [ ] Document backward compatibility process
- [ ] Update CLI reference for new auth

### Task 10: Code Review & Refinement (45 min)
- [ ] Run `ruff check --fix` and `mypy --strict`
- [ ] Ensure zero `# type: ignore` comments
- [ ] Verify all tests pass
- [ ] Check < 1000 LOC target
- [ ] Final review against success criteria

---

## File Structure Created

```
mastermind_cli/
├── types/
│   └── interfaces.py          # NEW: Pure function interfaces
├── orchestrator/
│   ├── stateless_coordinator.py  # NEW: Stateless coordinator
│   ├── brain_functions.py        # NEW: Pure function brains
│   └── mcp_wrapper.py           # EXISTING: Reuse as-is
├── auth/
│   └── api_keys.py             # NEW: API key auth
├── compatibility/
│   └── legacy_wrapper.py       # NEW: Legacy brain adapter
├── state/
│   └── logger.py               # NEW: Execution logger
└── commands/
    └── orchestrate.py          # UPDATE: Use new coordinator
```

---

## Key Code Patterns

### Pure Function Pattern

```python
# ✅ CORRECT: Pure function
def brain_product_strategy(
    input: BrainInput,
    mcp_client: MCPClient
) -> ProductStrategy:
    """No state access, only input → output."""
    knowledge = mcp_client.query_notebooklm(...)
    return ProductStrategy(...)

# ❌ WRONG: Stateful function
def brain_product_strategy(self, brief: str):
    """Uses self.state - NOT pure."""
    self.state["brief"] = brief  # Side effect!
    # ...
```

### Per-Request Coordinator Pattern

```python
# ✅ CORRECT: Per-request instance
async def endpoint(api_key: APIKey = Depends(get_current_api_key)):
    coordinator = StatelessCoordinator(config=make_config(api_key))
    return await coordinator.execute_flow(brief, brains)

# ❌ WRONG: Global coordinator
coordinator = Coordinator()  # Global instance!
async def endpoint():
    return await coordinator.orchestrate(brief)  # NOT multi-user safe
```

### Wave-Based Parallelism Pattern

```python
# ✅ CORRECT: Sequential waves, parallel within wave
async with TaskGroup() as tg:
    for wave in waves:
        tasks = [tg.create_task(execute_brain(b)) for b in wave]
        # Wait for wave before next wave
        await asyncio.gather(*tasks)

# ❌ WRONG: All parallel (MCP rate limit)
async with TaskGroup() as tg:
    for brain in all_brains:
        tg.create_task(execute_brain(brain))  # Too many concurrent MCP calls!
```

---

## Validation Gates

```bash
# 1. Type checking (strict mode)
cd /home/rpadron/proy/mastermind
uv run mypy mastermind_cli/ --strict --no-error-summary
# Expected: Zero errors, zero # type: ignore

# 2. Linting
uv run ruff check mastermind_cli/ --fix
uv run ruff format mastermind_cli/

# 3. Unit tests
uv run pytest tests/unit/test_types/interfaces.py -v
uv run pytest tests/unit/test_stateless_coordinator.py -v

# 4. Integration tests (multi-user)
uv run pytest tests/integration/test_pure_function_arch.py -v -k "multi_user"

# 5. Legacy compatibility
uv run pytest tests/integration/test_pure_function_arch.py -v -k "legacy"

# 6. Performance benchmark
uv run pytest tests/integration/test_pure_function_arch.py -v -k "benchmark"

# 7. End-to-end CLI test
export MM_API_KEY="test-key-sk-..."
uv run mastermind orchestrate "Build a CRM" --dry-run

# 8. Code coverage (< 1000 LOC target)
find mastermind_cli/ -name "*.py" -not -path "*/__pycache__/*" | xargs wc -l | tail -1
# Expected: < 1000 lines for new code
```

---

## Definition of Done

- [ ] All brains are pure functions (no `self.state` access)
- [ ] `StatelessCoordinator` has NO instance variables (except config)
- [ ] Multi-user test passes (5 concurrent requests, no cross-talk)
- [ ] MCP sequential execution (no rate limit errors under load)
- [ ] API Key auth works for CLI (env var) and Web (header)
- [ ] Legacy brains run without modification via wrapper
- [ ] `mypy --strict` passes with zero `# type: ignore`
- [ ] All tests pass (unit + integration)
- [ ] New code < 1000 LOC (measured with `wc -l`)
- [ ] Documentation updated
- [ ] Git commit with conventional commit format

---

## Error Handling Strategy

| Error | Handling |
|-------|----------|
| Brain input validation fails | Return 400 with field errors |
| MCP client timeout | Retry once, then fail gracefully |
| Dependency cycle detected | Return 400 with cycle description |
| Invalid API key | Return 401 (no details about key validity) |
| Legacy brain state pollution | Wrapper creates local orchestrator |
| Concurrent user conflict | Impossible with stateless architecture |

---

## Gotchas & Notes

1. **Pure Function Purity**: Brains MUST NOT access `self.state`, `orchestrator.state`, or global variables. All dependencies must be passed as function parameters.

2. **TaskGroup Requires Python 3.11+**: Project already uses Python 3.14, so this is safe. TaskGroup is superior to `asyncio.gather()` for structured concurrency.

3. **DependencyResolver Reuse**: The existing `DependencyResolver` in `mastermind_cli/orchestrator/dependency_resolver.py` already implements wave-based execution. REUSE IT, don't rewrite.

4. **TypeSafeMCPWrapper**: Already exists in `mastermind_cli/orchestrator/mcp_wrapper.py`. Use it as-is for MCP calls.

5. **Legacy Brain State**: When wrapping legacy brains, create a LOCAL `Coordinator` instance for each call. Never use global state.

6. **API Key Storage**: For v2.0, store API keys in environment variables (CLI) or SQLite (Web). No encrypted vault needed (defer to v3.0).

7. **Testing Multi-User**: The integration test must spawn 5 asyncio tasks running flows simultaneously. Verify no cross-talk in results.

8. **Backward Compatibility**: The wrapper should work for ALL existing v1.x brains without modification. Test with at least 3 different brains.

---

## Dependencies

**Existing (reuse):**
- `pydantic>=2.10.0` - Already in project
- `asyncio` - Built-in Python 3.14
- Existing `TypeSafeMCPWrapper`
- Existing `DependencyResolver`

**New additions:**
- None! All dependencies already in project.

---

## Output Files Created

| File | Purpose |
|------|---------|
| `mastermind_cli/types/interfaces.py` | Pure function interfaces |
| `mastermind_cli/orchestrator/stateless_coordinator.py` | Stateless coordinator |
| `mastermind_cli/orchestrator/brain_functions.py` | Pure function brains |
| `mastermind_cli/auth/api_keys.py` | API key auth |
| `mastermind_cli/compatibility/legacy_wrapper.py` | Legacy adapter |
| `mastermind_cli/state/logger.py` | Execution logger |
| `tests/integration/test_pure_function_arch.py` | Multi-user tests |
| `docs/PURE_FUNCTION_MIGRATION.md` | Migration guide |

---

## Next Steps

After this PRP:
- → PRP-03-01: FastAPI Backend + WebSocket Routes
- → PRP-03-02: Web UI Dashboard (HTMX/Alpine.js)
- → PRP-03-03: Visual Dependency Graph (React Flow)

---

## Confidence Score

**9.0/10** - Very high confidence of success.

**Rationale:**
- Architecture is simple (pure functions, stateless coordinator)
- Reuses existing patterns (DependencyResolver, TypeSafeMCPWrapper)
- No new dependencies required
- Clear validation gates (multi-user tests, MCP rate limit tests)
- Backward compatibility via wrapper (no breaking changes)
- < 1000 LOC target is realistic (already have foundation)

**Risks:**
- Legacy brain wrapper may need iteration for edge cases
- Multi-user testing may reveal race conditions (mitigated by stateless design)

---

## Context for AI Agent

**Files to read before implementing:**
1. `/home/rpadron/proy/mastermind/mastermind_cli/orchestrator/coordinator.py` - Current stateful coordinator (lines 45-48 show global state problem)
2. `/home/rpadron/proy/mastermind/mastermind_cli/orchestrator/dependency_resolver.py` - Existing wave-based execution (REUSE THIS)
3. `/home/rpadron/proy/mastermind/mastermind_cli/orchestrator/mcp_wrapper.py` - Existing type-safe MCP wrapper (REUSE THIS)
4. `/home/rpadron/proy/mastermind/mastermind_cli/types/brains.py` - Existing brain types (extend these)
5. `/home/rpadron/proy/mastermind/tests/integration/test_parallel_execution.py` - Existing parallel tests (reference)

**Key insight:** The existing `DependencyResolver` already implements wave-based execution. The new `StatelessCoordinator` should reuse this logic, not rewrite it.

**Command to start:**
```bash
cd /home/rpadron/proy/mastermind
uv run pytest tests/ -v  # Ensure existing tests pass first
# Then implement following Tasks in order
```

**Expected outcome:**
Stateless pure function architecture that:
- Supports multi-user execution (no global state)
- Avoids MCP rate limiting (sequential by wave)
- Works with API key auth (CLI + Web)
- Maintains backward compatibility (legacy wrapper)
- Passes all tests with < 1000 LOC of new code
