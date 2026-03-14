# Simplification Cascade - v2.0 Architecture

**Date:** 2026-03-13
**Type:** Architecture Decision
**Status:** Approved for Implementation

---

## The Insight

**"If every brain is a PURE FUNCTION (input → output), we DON'T need shared state."**

This ONE insight eliminates MULTIPLE pitfalls at once.

---

## What Gets Eliminated

### ❌ Eliminated by #5 (Multi-Orchestrator Race):
- ~~Session management~~ (each request creates its context)
- ~~Request context propagation~~ (no state to propagate)
- ~~Database-backed execution state~~ (logs only, no state)
- ~~Concurrency control~~ (each request is independent)

### ❌ Eliminated by #2 (Dependency Blind Spot):
- ~~State isolation layer~~ (no shared state anymore)
- ~~Complex dependency graph~~ (dependencies = declared inputs)
- ~~Topological sort~~ (DAG is simple: inputs → outputs)

### ❌ Eliminated by #6 (MCP Bottleneck):
- ~~Complex connection pooling~~ (limit by levels, not semaphores)
- ~~Request correlation~~ (each request is independent)
- ~~Response queue matching~~ (no responses to match)

### ❌ Eliminated by #4 (Auth Schism):
- ~~Full OAuth flow~~ (API Keys are sufficient)
- ~~JWT refresh rotation~~ (long-lived tokens)
- ~~Encrypted vault~~ (environment variables)

### ❌ Eliminated by #1 (False Parallelism):
- ~~Profiling infrastructure~~ (I/O-bound is obvious: MCP calls)
- ~~Async profiler~~ (asyncio is correct for I/O)

### ❌ Eliminated by #7 (Backward Compatibility):
- ~~Complex migration scripts~~ (lightweight wrapper)
- ~~Dual execution paths~~ (old brains with wrapper)

---

## Architecture: Before vs After

### Before (Complex):
```
Orchestrator (Global State)
    ↓
Brains (Share implicit state)
    ↓
MCP Client (Concurrent requests)
    ↓
Database (Execution state)
```

### After (Simple):
```
Coordinator (Stateless)
    ↓
Pure Functions (Input → Output)
    ↓
MCP Client (Sequential by level)
    ↓
SQLite (Logs only)
```

---

## Complexity Reduction

| Component | Before | After | Reduction |
|-----------|--------|-------|-----------|
| New files | 40+ | 8 | **80%** |
| Lines of code | ~3000 | ~600 | **80%** |
| Concepts | 15+ | 3 | **80%** |
| Dependencies | 12+ | 4 | **67%** |

---

## Implementation Plan

### Phase 1: Define Interfaces (Non-breaking)

Create Pydantic input/output models for each brain:

```python
# interfaces/core.py
from pydantic import BaseModel

class Brief(BaseModel):
    problem_statement: str
    context: str

class ProductStrategy(BaseModel):
    positioning: str
    target_audience: str

def brain_product_strategy(
    brief: Brief,
    mcp_client: MCPClient  # Injected, not global
) -> ProductStrategy:
    """Pure function: input → output, no state"""
    knowledge = mcp_client.query_notebooklm(...)
    return ProductStrategy(...)
```

### Phase 2: Stateless Coordinator

```python
# coordinator.py
class Coordinator:
    def execute_flow(self, brief: Brief) -> dict:
        """Stateless: each request is independent"""

        # Level 1: parallel (no dependencies)
        results = await asyncio.gather(
            brain_product_strategy(brief, self.mcp_client),
            brain_ux_research(brief, self.mcp_client),
        )

        # Level 2: sequential (depends on level 1)
        strategy, ux = results
        return brain_frontend_design(
            strategy=strategy,
            ux_research=ux,
            mcp_client=self.mcp_client
        )
```

### Phase 3: Simplified Auth (API Keys)

```python
# CLI: Environment variable
MM_API_KEY="sk-..."

# Web UI: POST /api/auth/login
# User enters API key (saved in localStorage)

# Middleware
async def verify_api_key(request: Request) -> bool:
    api_key = request.headers.get("X-API-Key")
    return validate_api_key(api_key)
```

### Phase 4: Backward Compatibility Wrapper

```python
# compatibility/wrapper.py
class LegacyBrainAdapter:
    """Converts old brains (with state) to pure functions"""

    def __call__(self, brief: Brief) -> BaseModel:
        # Create LOCAL context (not global)
        local_orchestrator = Orchestrator()

        # Call old brain
        result = self.legacy_brain.execute(
            brief=brief,
            orchestrator=local_orchestrator  # Local, not global
        )

        # Convert to Pydantic
        return self.output_model(**result)
```

---

## PRPs to Generate

1. **PRP-03-01:** Pure Function Interfaces (Pydantic models)
2. **PRP-03-02:** Stateless Coordinator Implementation
3. **PRP-03-03:** Simplified Auth (API Keys)
4. **PRP-03-04:** Legacy Brain Wrapper
5. **PRP-03-05:** MCP Client Sequential-by-Level
6. **PRP-03-06:** SQLite Logger (execution logs only)

---

## Success Criteria

- [ ] All brains are pure functions (no global state access)
- [ ] Coordinator is stateless (multi-user safe)
- [ ] MCP requests are sequential by dependency level (no rate limit issues)
- [ ] Auth works with API keys (CLI + Web UI)
- [ ] Legacy brains run without modification via wrapper
- [ ] < 1000 lines of new code (vs ~3000 with complex approach)

---

## The Cascade Test

**Explaining architecture to a new dev:**

**Before:** "You need to understand session management, request context, state isolation, dependency graphs, topological sort, concurrency control, connection pooling..."

**After:** "Brains are functions. Input → Output. Coordinator connects them. Done."

---

*Approved: 2026-03-13*
*Ready for PRP generation via /mm:generate-prp*
