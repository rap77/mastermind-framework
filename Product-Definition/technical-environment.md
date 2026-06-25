# Technical Environment — Multi-Harness Architecture

## 1. Project Technical Summary

| Attribute | Value |
|---|---|
| Runtime environment | Hybrid — Docker containers (production) + WSL Ubuntu-24 (development) |
| Cloud provider | AWS (diseñado agnóstico al proveedor con Gateway pattern) |
| Deployment model | Containers — docker-compose (dev + prod); aspiración ECS/EKS futuro |
| Team size | 1 developer full-stack (rpadron) |
| Experience | Python fuerte, TypeScript/React, Rust, Claude Code, MCP, NotebookLM |

---

## 2. Programming Languages

### 2.1 Required Languages

| Language | Version | Purpose | Rationale |
|---|---|---|---|
| Python | 3.14+ | Backend services, CLI, brain orchestration, AI harness, governance, eval | Type hints nativos, async/await, ecosistema principal |
| Rust | Latest stable | Control plane, real-time hub, adapter registry, future hot-path gates | Performance; 65% del backend (DR-007) |
| TypeScript | 5.x | Frontend dashboard (Next.js 16) | Type safety, React ecosystem |
| SQL | PostgreSQL 17 | Data persistence + pgvector + event sourcing | Modelo híbrido relacional + JSONB + vector (doc 27) |

### 2.2 Permitted Languages

| Language | Conditions for Use |
|---|---|
| Bash | Scripts de instalación, CI/CD hooks, pre-commit. Debe tener `set -euo pipefail` |
| YAML/TOML | Configuración. No lógica de negocio |

### 2.3 Prohibited Languages

| Language | Reason |
|---|---|
| (ninguno explícitamente prohibido) | Solo se prohíben package managers alternativos |

### 2.4 Package Manager Policy (OBLIGATORIO)

| Runtime | Must Use | Prohibited |
|---|---|---|
| Python | `uv` siempre | pip, poetry, conda |
| Node.js | `pnpm` siempre | npm, yarn |
| Rust | `cargo` | — |

---

## 3. Frameworks and Libraries

### 3.1 Required Frameworks

| Framework | Domain | Rationale |
|---|---|---|
| FastAPI | Python backend / API | Ya existente, async nativo, Pydantic integration |
| Pydantic v2 | Data validation / models | Type-safe, migration ya completada |
| SQLAlchemy | ORM / DB access | PostgreSQL + migrations + pgvector |
| Click + Rich | CLI | Ya implementado en mastermind-cli |
| Next.js 16 | Frontend dashboard | React 19 + App Router (del fork Paperclip) |
| Tailwind 4 + shadcn/ui | UI components | Design system consistente |
| pytest | Testing | Framework principal de testing |
| Playwright | E2E testing | Browser automation |

### 3.2 Preferred Frameworks (not required)

| Framework | Conditions for Use |
|---|---|
| Pydantic Settings | Configuration management con env vars |
| structlog | Structured logging (preferido sobre print/logging básico) |
| httpx | HTTP client async (preferido sobre requests) |
| alembic | Database migrations |

### 3.3 Prohibited Libraries

| Prohibited | Reason | Use Instead |
|---|---|---|
| pip | Policy enforcement | uv |
| npm / yarn | Policy enforcement | pnpm |
| poetry / conda | Policy enforcement | uv |
| SQLite (for new features) | Legacy being removed; no scaling | PostgreSQL |
| axios | Bundle size | native fetch |
| requests (for new code) | Sync-only, no async | httpx |

---

## 4. Cloud Services

### 4.1 Allow-List

| Service | Purpose | Constraints |
|---|---|---|
| PostgreSQL 17 + pgvector | Primary data store, vector retrieval | Hosted via Docker; future: RDS/Aurora |
| Redis | Session cache, pub/sub, rate limiting | Via Docker |
| Docker / Docker Compose | Container orchestration | Dev + Prod |
| NotebookLM (via MCP) | Knowledge retrieval bridge | Read-only; no writes from harness |
| Context7 (MCP) | Documentation MCP server | Read-only |
| AWS S3 (future) | Artifact storage, backups | Not yet configured |
| AWS CloudWatch (future) | Monitoring, alerting | Not yet configured |

### 4.2 Deny-List

| Service | Reason |
|---|---|
| Firebase | No relevance; adds vendor complexity |
| MongoDB | PostgreSQL covers all use cases with hybrid model |
| DynamoDB | AWS lock-in for data layer; prefer Postgres portability |

---

## 5. Architecture and Patterns

### 5.1 API Style

- **REST** (FastAPI) — Primary API surface for dashboard and external consumers
- **WebSocket** — Real-time events to dashboard (doc 35)
- **gRPC** — Rust ↔ Python internal communication (control plane)
- **Event-driven** — Internal pub/sub for scheduler events and audit trail

### 5.2 Data Patterns

| Pattern | Usage |
|---|---|
| Relational (normalized) | Projects, tasks, runs, decisions, users |
| JSONB (flexible) | Checkpoints, payloads, metadata, config |
| pgvector | Semantic retrieval for Memory Layer |
| Event sourcing | Scheduler events, audit trail, token consumption |
| Append-only logs | Audit, evaluation history, governance decisions |

### 5.3 Architecture Patterns for Multi-Harness

| Pattern | Application |
|---|---|
| **Interceptor/Middleware** | SAL governance layer antes del Coordinator |
| **Strategy** | Budget tiers (Conservative/Standard/Generous) |
| **Observer** | Audit trail subscribers; meta-loop metrics collection |
| **Chain of Responsibility** | Policy checks en secuencia (scope → budget → risk → approval) |
| **DAG Execution** | Task dependencies; harness coordination |
| **Circuit Breaker** | Overnight mode: pause tras 2-3 failures |
| **Registry** | Backend availability; tool catalog |

### 5.4 Project Structure Conventions

```
apps/api/mastermind_cli/
├── orchestrator/
│   ├── coordinator.py          # Main orchestration (existing)
│   ├── governance/             # NEW: SAL interceptor layer
│   │   ├── __init__.py
│   │   ├── policy_gate.py     # SAL policy evaluation
│   │   ├── budget_enforcer.py # Token budget tracking
│   │   ├── scope_validator.py # Task scope enforcement
│   │   └── audit_trail.py     # Evidence chain persistence
│   ├── evaluation/             # NEW: Memory eval harness
│   │   ├── __init__.py
│   │   ├── scorer.py          # recall@k, MRR, nDCG
│   │   ├── qrels.py           # Query-relevance pairs
│   │   └── ci_gate.py         # Regression detection
│   └── scheduler/             # NEW: Overnight/multi-backend
│       ├── __init__.py
│       ├── overnight_loop.py  # Cautious execution loop
│       └── backend_router.py  # Available backend selection
```

---

## 6. Security

### 6.1 Authentication

| Aspect | Approach |
|---|---|
| Internal auth | JWT tokens |
| API keys | Format `mmsk_` + bcrypt hash (migrating from legacy `mm_`) |
| Row-Level Security | Per-org isolation (future, when multi-tenant) |

### 6.2 Secrets Management

| Environment | Method |
|---|---|
| Development | `.env` files (gitignored) |
| Production | Docker secrets |
| NEVER | Hardcoded in code (enforced by AGENTS.md + SAL gate) |

### 6.3 SAL Security Policies (governance harness)

| Category | Policy | Action |
|---|---|---|
| Destructive ops | rm -rf, git reset --hard, git clean -fdx, mass delete/move | **DENY** |
| Production writes | POST/PUT/PATCH/DELETE to production endpoints | **DENY** without dry-run + approval |
| Main branch | push, merge, release, tagging to main/master | **DENY** without approval |
| Secrets detection | Tokens, keys, .env, cookies, auth headers in commits/logs | **DENY** always |
| Out-of-scope files | Changes to CI, deploy, infra, billing, auth, migrations not in task | **DENY** |
| Irreversible commands | Destructive migrations, shared DB cleanup, external side effects | **DENY** |
| Large changes | >20 files OR >500 LOC OR sensitive dirs | **PAUSE** + approval |
| High-cost tool calls | >100K tokens per call | **WARN** at 80K, **APPROVAL** at 100K |
| No checkpoint | Attempt to continue without audit trail | **DENY** |

### 6.4 Input Validation

- Pydantic v2 models for all API inputs
- `@validate_call` decorator on public functions (already in use in Coordinator)
- JSON Schema validation for tool call parameters

---

## 7. Testing

### 7.1 Test Types Required

| Type | Framework | Purpose | Trigger |
|---|---|---|---|
| Unit | pytest | Isolated function/class tests | Every commit |
| Integration | pytest + Docker | DB + service interaction | PR/merge |
| E2E | Playwright | Full browser flow (dashboard) | Pre-release |
| Eval | Custom scorer (pytest-based) | Memory retrieval quality | PR/merge (CI gate) |
| Load | Rust benchmarks (benches/) | Control plane performance | Manual/weekly |
| Property-based | hypothesis (optional, AI-DLC extension) | Edge case discovery | Optional |

### 7.2 Coverage Targets

| Scope | Target |
|---|---|
| Governance module (SAL, budget) | ≥90% line coverage |
| Evaluation module (scorer, qrels) | ≥85% line coverage |
| Coordinator (existing) | Maintain current coverage |
| New code overall | ≥80% |

### 7.3 CI/CD Gates

| Gate | Condition | Action |
|---|---|---|
| Lint | ruff check passes | Block merge |
| Type check | mypy/pyright passes | Block merge |
| Unit tests | All pass | Block merge |
| Eval scorer | Score ≥ baseline - 5% | Block merge |
| Pre-commit | Conventional commit format | Block commit |
| Secret scan | No credentials detected | Block merge |

---

## 8. Token Budget Architecture

### 8.1 Tiers

| Tier | Per-Task | Per-Session | Use Case |
|---|---|---|---|
| A) Conservative | 50K | 200K | Fixes chicos, docs, revisión acotada |
| **B) Standard** (default) | **100K** | **500K** | Trabajo real de development/planning |
| C) Generous | 200K | 1M | Discovery, reverse-engineering, síntesis multi-doc |

### 8.2 Behavior at Limits

| Threshold | Behavior |
|---|---|
| 80% of task budget (80K default) | Warning emitted to audit trail |
| 100% of task budget (100K default) | Approval gate — pause, ask to continue or stop |
| 100% of session budget (500K default) | Hard stop — checkpoint written, session ends cleanly |
| >2X per single tool call | Require explicit approval before executing |

---

## 9. Example Code Patterns

### 9.1 SAL Policy Gate (Pseudocode)

```python
from pydantic import BaseModel
from enum import Enum
from typing import Literal

class PolicyVerdict(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    PAUSE_AND_ASK = "pause_and_ask"

class Intention(BaseModel):
    action: str
    target: str
    scope: str
    estimated_tokens: int | None = None

class GovernanceInterceptor:
    """SAL policy gate — deterministic, no LLM calls."""

    def __init__(self, policies: list["Policy"]):
        self.policies = policies

    def evaluate(self, intention: Intention, task_context: "TaskContext") -> PolicyVerdict:
        """Chain of responsibility: first policy to deny/pause wins."""
        for policy in self.policies:
            verdict = policy.check(intention, task_context)
            if verdict != PolicyVerdict.ALLOW:
                self.audit(intention, verdict, policy)
                return verdict
        return PolicyVerdict.ALLOW

    def audit(self, intention, verdict, policy):
        """Append to evidence chain — append-only, never truncate."""
        ...
```

### 9.2 Budget Enforcer (Pseudocode)

```python
class BudgetEnforcer:
    """Token budget tracking with tiered gates."""

    def __init__(self, tier: Literal["conservative", "standard", "generous"] = "standard"):
        self.limits = TIER_LIMITS[tier]
        self.task_consumed = 0
        self.session_consumed = 0

    def pre_call(self, estimated_tokens: int) -> PolicyVerdict:
        projected = self.task_consumed + estimated_tokens
        if projected > self.limits.task * 2:
            return PolicyVerdict.DENY  # >2X single call
        if self.session_consumed >= self.limits.session:
            return PolicyVerdict.DENY  # Session exhausted
        if projected > self.limits.task:
            return PolicyVerdict.PAUSE_AND_ASK  # Over task budget
        if projected > self.limits.task * 0.8:
            self.emit_warning()
        return PolicyVerdict.ALLOW

    def post_call(self, actual_tokens: int):
        self.task_consumed += actual_tokens
        self.session_consumed += actual_tokens
```

### 9.3 Overnight Cautious Loop (Pseudocode)

```python
async def overnight_loop(tasks: list[Task], governance: GovernanceInterceptor):
    """Cautious mode: one task at a time, checkpoint, reevaluate."""
    consecutive_failures = 0

    for task in tasks:
        # Pre-check
        verdict = governance.evaluate(task.as_intention(), current_context())
        if verdict != PolicyVerdict.ALLOW:
            break

        # Execute
        result = await execute_task(task)
        write_checkpoint(task, result)

        # Reevaluate continuation
        if not result.success:
            consecutive_failures += 1
            if consecutive_failures >= 3:
                break
        else:
            consecutive_failures = 0

        if not budget_healthy() or not backend_available():
            break

    generate_morning_report()
```

---

## 10. Existing System Inventory (Brownfield Context)

### 10.1 What Must Stay Unchanged

| Component | Reason |
|---|---|
| `Coordinator.orchestrate()` interface | All MM-Flow commands depend on it |
| `.mm-flow/planning/` structure | Active objectives + handoffs in progress |
| Brain routing via MCP | 8 cerebros already configured |
| `AGENTS.md` / `CLAUDE.md` | Active rules for all agents |
| PostgreSQL schema (existing tables) | Data in production |

### 10.2 What Can Be Extended

| Component | How |
|---|---|
| `Coordinator.__init__()` | Add governance interceptor injection |
| `coordinator.py` orchestrate method | Add pre-call governance check |
| `.mm-flow/commands/` | Add new commands for eval/governance |
| `tests/` | Add eval harness test suites |
| CI pipeline | Add eval scorer gate |

### 10.3 Prohibited Patterns (from existing codebase)

| Pattern | Reason | Alternative |
|---|---|---|
| Global mutable state | Race conditions; testability | Dependency injection |
| LLM-based policy decisions | Non-deterministic; expensive | Deterministic code policies |
| Monolithic Coordinator | Already too large (55K file) | Extract governance as separate module |
| SQLite for new data | Legacy being removed | PostgreSQL always |
