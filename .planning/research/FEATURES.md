# Feature Research: MasterMind Framework v2.0

**Domain:** Cognitive Architecture Platform (Parallel Execution + Type Safety + Web UI)
**Researched:** 2026-03-13
**Confidence:** MEDIUM (Web search unavailable, based on codebase analysis + ecosystem knowledge)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Task Status Indication** | Users need to know what's happening | LOW | Progress bars, status messages, completion percentage |
| **Error Messages** | When things fail, users need explanations | LOW | Clear error descriptions, not just stack traces |
| **Task Cancellation** | Users should control execution | MEDIUM | Graceful shutdown of running tasks |
| **Result Export** | Users want to save outputs | LOW | JSON, YAML, Markdown export (already exists in v1.3) |
| **Configuration Persistence** | Re-run without reconfiguring | MEDIUM | Save/load execution configurations |
| **Type Validation** | Catch data errors before execution | MEDIUM | Pydantic already validates, needs enforcement |
| **Basic Authentication** | Multi-user requires security | MEDIUM | Simple username/password, RBAC basics |
| **Session Management** | Track user state across requests | MEDIUM | Session storage, timeout handling |
| **Responsive UI** | Works on mobile/tablet | LOW | CSS grid/flexbox, responsive design |
| **Audit Logging** | Who did what, when | LOW | Timestamp, user, action (already have eval logs) |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Visual Dependency Graph** | See brain relationships intuitively | HIGH | Interactive DAG visualization (D3.js/Cytoscape.js) |
| **Parallel Execution Dashboard** | Real-time view of multiple brains running | HIGH | WebSocket updates, live task cards |
| **Type-Auto-Completion** | IDE-like experience in browser | HIGH | Monaco/Ace editor with type hints |
| **Brain-to-Brain Comm Visualization** | See how brains collaborate | MEDIUM | Message flow animation |
| **Replay/Debug Mode** | Step through execution history | HIGH | Time-travel debugging for orchestration |
| **Smart Caching** | Skip redundant brain queries | MEDIUM | Cache by brief hash + brain config |
| **Live Interview Collaboration** | Multiple users in discovery session | HIGH | Shared cursor, real-time chat |
| **Execution Comparison** | Compare two runs side-by-side | MEDIUM | Diff view of brain outputs |
| **Custom Metrics Dashboard** | Track agency KPIs | MEDIUM | Charts: success rate, avg iterations, brain usage |
| **Template Library** | Reusable execution patterns | LOW | Pre-built flows for common scenarios |
| **Hot-Reload Brains** | Update brains without restart | MEDIUM | Watch filesystem, reload on change |
| **Granular Permissions** | Per-brain, per-niche access control | HIGH | Complex RBAC system |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Real-Time Collaborative Editing** | "Like Google Docs for brains" | Extreme complexity (CRDTs), operational transform overkill | Session isolation with explicit sharing |
| **Auto-Scaling** | "Handle 1000 users automatically" | Kubernetes complexity, cost overkill for v2.0 | Manual deployment guide, performance docs |
| **ML-Based Optimization** | "System learns to be faster" | R&D heavy, unpredictable behavior | Explicit configuration, profiling tools |
| **Blockchain/Audit Trail** | "Immutable proof of execution" | Overengineering, performance hit | File-based audit logs (already exists) |
| **Mobile Native Apps** | "Use on iPhone" | Fragmented codebase, app store overhead | Responsive web UI (PWA future) |
| **Voice Interface** | "Talk to brains" | Speech-to-text complexity, low ROI | Text-first, voice via browser API later |
| **Full RAG Vector DB** | "Search across all brains" | Premature optimization (v3.0 feature) | NotebookLM search is sufficient for now |
| **Multi-Tenant SaaS** | "Host for customers" | Auth complexity, data isolation, compliance nightmares | Single-tenant deployment, customer hosts own instance |

## Feature Dependencies

```
[Parallel Task Execution]
    ├──requires──> [Dependency Graph Resolution]
    │                └──requires──> [Task State Management]
    └──enhances──> [Real-Time Progress Dashboard]

[Type-Safe Interfaces]
    ├──requires──> [Pydantic Models for All Data]
    │                └──requires──> [Mypy Strict Mode Configuration]
    └──enables──> [Auto-Completion in Web UI]

[Web Dashboard]
    ├──requires──> [WebSocket Server]
    │                └──requires──> [Session Management]
    ├──requires──> [Authentication System]
    └──enhances──> [Visual Dependency Graph]

[Multi-User Sessions]
    ├──requires──> [User Authentication]
    ├──requires──> [Session Isolation]
    └──conflicts──> [Shared Global State] (must be refactored)

[Real-Time Progress]
    ├──requires──> [Parallel Task Execution]
    └──requires──> [WebSocket Updates]

[Visual Dependency Graph]
    ├──requires──> [Dependency Graph Resolution]
    └──requires──> [D3.js/Cytoscape.js Frontend]
```

### Dependency Notes

- **[Parallel Task Execution] requires [Task State Management]:** Can't track parallel tasks without centralized state store (Redis/SQLite)
- **[Type-Safe Interfaces] enables [Auto-Completion]:** With strict typing, IDE can provide suggestions in Monaco editor
- **[Multi-User Sessions] conflicts with [Shared Global State]:** Current coordinator uses instance variables, must be refactored to session-scoped
- **[Real-Time Progress] requires [Parallel Task Execution]:** Sequential execution has trivial progress (0% → 100% with nothing in between)
- **[Visual Dependency Graph] requires [Dependency Graph Resolution]:** Can't visualize what you don't understand

## MVP Definition

### Launch With (v2.0)

Minimum viable product — what's needed to validate the concept.

**Parallel Execution Core:**
- [ ] **Dependency Graph Resolution** — Detect brain dependencies from flow definitions
- [ ] **Task State Management** — SQLite-based task store with status (pending/running/completed/failed)
- [ ] **Parallel Executor** — asyncio-based parallel brain execution with dependency waiting

**Type Safety Foundation:**
- [ ] **Strict Pydantic Models** — All coordinator/brain data as typed models (75% done, see models.py)
- [ ] **Mypy Strict Mode** — Enable strict type checking, fix all errors
- [ ] **Type-Safe MCP Wrapper** — Typed MCP client integration

**Web Dashboard (Basic):**
- [ ] **FastAPI Backend** — REST API for orchestration endpoints
- [ ] **Basic Auth** — Simple username/password (single-tenant)
- [ ] **Task Status Page** — List active/completed tasks with status
- [ ] **Manual Brain Trigger** — Web form to execute single brain
- [ ] **Static Asset Serving** — Serve HTML/CSS/JS

### Add After Validation (v2.1)

Features to add once core is working.

- [ ] **Real-Time Progress** — WebSocket updates for live task status
- [ ] **Visual Dependency Graph** — D3.js interactive DAG visualization
- [ ] **Multi-User Support** — Session isolation, per-user task lists
- [ ] **Execution History** — Browse past runs, view outputs
- [ ] **Configuration UI** — Create/edit execution flows via web interface
- [ ] **Advanced RBAC** — Per-niche, per-brain permissions

### Future Consideration (v3.0+)

Features to defer until product-market fit is established.

- [ ] **Full RAG System** — Vector DB with semantic search across all brains
- [ ] **ML-Based Optimization** — Learn optimal execution paths
- [ ] **Auto-Scaling** — Horizontal scaling with Kubernetes
- [ ] **Real-Time Collaboration** — Multiple users editing same session
- [ ] **Mobile Apps** — Native iOS/Android applications

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| **Task State Management** | HIGH (enables parallel) | MEDIUM (SQLite + schema) | P1 |
| **Dependency Graph Resolution** | HIGH (enables parallel) | HIGH (flow analysis) | P1 |
| **Parallel Executor** | HIGH (faster execution) | HIGH (asyncio refactoring) | P1 |
| **Strict Pydantic Models** | HIGH (catch bugs early) | MEDIUM (already started) | P1 |
| **Mypy Strict Mode** | MEDIUM (developer UX) | MEDIUM (fix type errors) | P1 |
| **FastAPI Backend** | HIGH (enables web UI) | LOW (simple REST) | P1 |
| **Basic Auth** | HIGH (security) | LOW (simple password) | P1 |
| **Task Status Page** | HIGH (visibility) | LOW (HTML + polling) | P1 |
| **Manual Brain Trigger** | MEDIUM (convenience) | LOW (form + API call) | P2 |
| **Real-Time Progress** | HIGH (UX) | MEDIUM (WebSockets) | P2 |
| **Visual Dependency Graph** | MEDIUM (clarity) | HIGH (D3.js + backend) | P2 |
| **Multi-User Sessions** | MEDIUM (agencies need it) | HIGH (session isolation) | P2 |
| **Execution History** | MEDIUM (debugging) | MEDIUM (pagination + filters) | P2 |
| **Configuration UI** | MEDIUM (no-code) | HIGH (complex forms) | P3 |
| **Advanced RBAC** | LOW (single-tenant OK) | HIGH (complex auth) | P3 |
| **Replay/Debug Mode** | MEDIUM (debugging) | HIGH (time-travel) | P3 |
| **Auto-Completion in Editor** | MEDIUM (DX) | HIGH (Monaco + types) | P3 |
| **Smart Caching** | LOW (nice to have) | MEDIUM (cache invalidation) | P3 |

**Priority key:**
- **P1:** Must have for v2.0 launch
- **P2:** Should have, add when possible (v2.1)
- **P3:** Nice to have, future consideration (v3.0+)

## Competitor Feature Analysis

| Feature | LangChain | LangGraph | Airflow | Prefect | Our Approach |
|---------|-----------|-----------|---------|---------|--------------|
| **Parallel Execution** | ✅ Yes (async) | ✅ Yes (DAG) | ✅ Yes (DAG) | ✅ Yes (DAG) | ✅ Planned (asyncio) |
| **Type Safety** | ❌ Partial | ❌ Partial | ❌ None | ❌ Partial | ✅ Pydantic + mypy strict |
| **Web Dashboard** | ✅ LangSmith | ✅ LangStudio | ✅ Yes | ✅ Prefect Cloud | ✅ Planned (FastAPI) |
| **Real-Time Progress** | ✅ Yes | ✅ Yes | ⚠️ Polling | ✅ Yes | ✅ Planned (WebSocket) |
| **Visual DAG** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Maybe (D3.js) |
| **Multi-User** | ✅ Yes (SaaS) | ✅ Yes (SaaS) | ✅ Yes (RBAC) | ✅ Yes (SaaS) | ⚠️ Basic (single-tenant) |
| **Self-Hosted** | ❌ No | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes (only option) |
| **AI-Native** | ✅ Yes | ✅ Yes | ❌ No | ❌ No | ✅ Yes (brains-first) |
| **Domain-Specific** | ❌ Generic | ❌ Generic | ❌ Generic | ❌ Generic | ✅ Yes (expert niches) |

**Key Differentiators:**
1. **Type Safety** — Only strict-typed framework in this space
2. **Self-Hosted Only** — No vendor lock-in, full data control
3. **Domain-Specific Brains** — Not generic LLM orchestration
4. **Expert Knowledge Distillation** — Built-in expert sources (230+)

## Domain-Specific Features

### 1. Parallel Task Execution Systems

**Table Stakes:**
- Task queue with pending/running/completed states
- Dependency resolution (A depends on B → B runs first)
- Error handling (task failure → stop dependents or continue?)
- Execution logs (what ran, when, how long)

**Differentiators:**
- Smart dependency detection from flow definitions
- Dynamic parallelism (auto-detect independent tasks)
- Predictive execution time estimation
- Execution replay with same random seeds

**Anti-Features:**
- Complex retry policies (exponential backoff is overkill)
- Distributed execution (single-machine is fine for v2.0)
- Priority queues (all tasks are equal priority)

### 2. Type-Safe Python Frameworks

**Table Stakes:**
- Pydantic models for all data structures
- mypy type checking (not strict, but enabled)
- Type hints on all public APIs
- Runtime validation at boundaries

**Differentiators:**
- **Strict mypy mode** (no `Any`, no untyped calls)
- **Type-safe MCP** (validated notebook queries)
- **Generated TypeScript types** (for web UI)
- **Auto-completion in CLI** (type-driven suggestions)

**Anti-Features:**
- Runtime type checker (Typeguard is too slow)
- Full TypeScript backend (stay in Python)
- Generic type system (keep it simple)

### 3. Web Dashboards for AI Systems

**Table Stakes:**
- Task list with status (pending/running/completed/failed)
- Individual task detail page (logs, output, errors)
- Manual trigger form (execute brain with inputs)
- Basic authentication (login screen)
- Responsive design (works on tablet)

**Differentiators:**
- **Live brain collaboration** (multiple users viewing same run)
- **Visual dependency graph** (DAG animation)
- **Type-aware forms** (validation errors in real-time)
- **Execution comparison** (diff two runs)
- **Brain usage analytics** (which brains used most)

**Anti-Features:**
- Real-time code editing (too complex)
- Collaborative cursors (overkill)
- Dark mode toggle (nice to have, defer)
- Mobile app (PWA is enough)

## Technical Complexity Notes

### High Complexity Features (Require R&D)

1. **Dependency Graph Resolution**
   - Challenge: Detect implicit dependencies from brain outputs
   - Risk: Circular dependencies, deadlock
   - Approach: Explicit dependency declarations in flow configs

2. **Visual Dependency Graph**
   - Challenge: Layout algorithms for large DAGs (23+ brains)
   - Risk: Performance with 100+ nodes
   - Approach: Use Cytoscape.js with force-directed layout, lazy rendering

3. **Multi-User Session Isolation**
   - Challenge: Current coordinator is singleton (instance variables)
   - Risk: Race conditions, mixed state
   - Approach: Refactor to session-scoped coordinators, request context

### Medium Complexity (Standard Patterns)

1. **Parallel Executor**
   - Pattern: asyncio.gather with dependency semaphore
   - Risk: NotebookLM MCP is not async (needs thread pool)
   - Approach: Run in executor thread, await futures

2. **WebSocket Real-Time Updates**
   - Pattern: Socket.IO or native WebSockets
   - Risk: Connection state management
   - Approach: Reconnection logic, heartbeat

3. **Authentication System**
   - Pattern: FastAPI Security with HTTPBasic
   - Risk: Password storage (use bcrypt)
   - Approach: Simple file-based users (no DB needed)

### Low Complexity (Well-Understood)

1. **Task State Management**
   - Pattern: SQLite with tasks table
   - Risk: None (standard CRUD)
   - Approach: SQLAlchemy ORM or raw SQL

2. **FastAPI Backend**
   - Pattern: REST endpoints with Pydantic models
   - Risk: None (mature framework)
   - Approach: One endpoint per operation

3. **Static Asset Serving**
   - Pattern: Whitenoise or FastAPI StaticFiles
   - Risk: None (standard)
   - Approach: Build frontend to dist/, serve from FastAPI

## Implementation Risk Assessment

| Feature | Risk Level | Risk Type | Mitigation |
|---------|------------|-----------|------------|
| **Dependency Graph Resolution** | HIGH | Technical (circular deps) | Explicit declarations, cycle detection |
| **Parallel Executor** | MEDIUM | Technical (async MCP) | Thread pool executor, timeout handling |
| **Visual Dependency Graph** | MEDIUM | UX (large DAGs) | Progressive rendering, filters |
| **Mypy Strict Mode** | LOW | Process (fix errors) | Incremental adoption, CI blocking |
| **WebSocket Updates** | LOW | Technical (disconnects) | Reconnection logic, polling fallback |
| **Multi-User Sessions** | HIGH | Architectural (state) | Session-scoped coordinators |
| **Authentication** | LOW | Security (passwords) | bcrypt, https enforcement |
| **Real-Time Collaboration** | HIGH | Technical (race conditions) | Operational transforms or CRDTs (defer to v2.1) |

## Sources

**Codebase Analysis:**
- `/home/rpadron/proy/mastermind/mastermind_cli/memory/models.py` — Existing Pydantic patterns
- `/home/rpadron/proy/mastermind/mastermind_cli/orchestrator/coordinator.py` — Current orchestration patterns
- `/home/rpadron/proy/mastermind/pyproject.toml` — Current dependencies (Pydantic 2.0+, click, rich)

**Ecosystem Knowledge (LOW confidence without WebSearch):**
- Python asyncio for parallel execution
- FastAPI for web dashboard
- WebSocket for real-time updates
- D3.js/Cytoscape.js for DAG visualization
- Celery/Airflow patterns for task scheduling (competitor analysis)

**Missing Verification (WebSearch was rate-limited):**
- Current best practices for Python parallel task execution (2026)
- Type-safe Python framework adoption trends (2026)
- Web dashboard real-time progress patterns (2026)
- Multi-user session management in Python (2026)

**Confidence Level: MEDIUM**
- Codebase analysis is HIGH confidence
- Ecosystem knowledge is MEDIUM confidence (based on training data, not verified with current sources)
- Competitor analysis is LOW confidence (without WebSearch verification)

---

*Feature research for: MasterMind Framework v2.0*
*Researched: 2026-03-13*
*Confidence: MEDIUM (WebSearch unavailable, codebase analysis + ecosystem knowledge)*
