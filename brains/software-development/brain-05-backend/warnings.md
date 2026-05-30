# Brain #05-Backend — Warnings & Anti-Patterns

These patterns trigger automatic rejection. When rejecting, cite the source using the Oracle Pattern:

```
Rejected: [specific library or pattern] violates [constraint].
Source: global-protocol.md > [Section] | brain-05-backend/warnings.md > [pattern name]
```

Generic rejections without source citation = Rating 2 maximum.

---

## Universal BRAIN-FEED Poisoning Patterns

These 4 patterns apply across ALL brain domains. Source: Brain #6 consultation (2026-03-27).

### 1. Stack Hallucination

**Definition:** Brain suggests a library or tool not declared in the root `uv.lock` or `pnpm-lock.yaml`.

**Rule:** `PROHIBITED: Suggesting external dependencies not declared in the root lockfile.`

**Backend examples:** Suggesting Celery (not in stack), proposing SQLModel instead of SQLAlchemy 2.x, suggesting aiohttp when httpx is already in uv.lock.

**Rejection format:**
```
Rejected: [library name] is not declared in root uv.lock.
Source: global-protocol.md > Stack Hard-Lock | brain-05-backend/warnings.md > Stack Hallucination
```

---

### 2. Toil-Inducer

**Definition:** Brain suggests manual steps instead of code — direct DB access, SSH, manual file edits in production.

**Rule:** `ANTI-PATTERN: Any recommendation requiring manual production access is an architecture failure.`

**Backend examples:** "Manually run this SQL to fix the data." "SSH into the server and restart the FastAPI process." "Directly edit the SQLite file to reset the state."

**Rejection format:**
```
Rejected: [manual step] requires manual production access.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-05-backend/warnings.md > Toil-Inducer
```

---

### 3. Security Bypass

**Definition:** Brain suggests hardcoded credentials, plain-text secrets, or disabled authentication — even in test examples or "temporary" configurations.

**Rule:** `BLOCKER: Never suggest hardcoded credentials, not even in test examples.`

**Backend examples:** "Use api_key='test-123' in the fixture." "Disable JWT validation for this endpoint during development." "Hardcode the DB connection string for local testing."

**Rejection format:**
```
Rejected: hardcoded credentials violates Security Bypass rule.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-05-backend/warnings.md > Security Bypass
```

---

### 4. Legacy Drift

**Definition:** Brain ignores existing tests in `tests/` or proposes changes that break existing contracts without a migration plan.

**Rule:** `PROHIBITED: Proposals that invalidate existing test contracts without explicit migration plan.`

**Backend examples:** Changing a FastAPI route signature that breaks `tests/api/` endpoint tests. Altering a Pydantic model without updating all test fixtures. Changing async DB session handling without verifying pytest-asyncio fixtures.

**Rejection format:**
```
Rejected: [proposal] invalidates existing test contracts without migration plan.
Source: global-protocol.md > Cross-Domain Anti-Patterns | brain-05-backend/warnings.md > Legacy Drift
```

---

## Domain-Specific Anti-Patterns — Backend Architecture

### Any Contamination

**Definition:** Using `dict[str, Any]` or `Any` type in a Pydantic model or function signature without explicit TypeVar or Protocol justification.

**Rule:** `PROHIBITED. Strict mode means strict mode. Pydantic v2 docs — model_config = {'strict': True}.`

**Why:** `Any` bypasses the entire type checking system. A Pydantic model with `Any` fields is not a type-safe model — it's a dict with extra steps. Type-Safety Zealot core violation.

**Examples:**
- `class BrainResponse(BaseModel): data: dict[str, Any]`
- `def process(payload: Any) -> dict:`
- Using `model_config = ConfigDict(arbitrary_types_allowed=True)` to paper over type violations

**Rejection format:**
```
Rejected: dict[str, Any] violates Type-Safety Zealot constraint.
Source: global-protocol.md > Stack Hard-Lock | brain-05-backend/warnings.md > Any Contamination
Cite: Pydantic v2 docs — model_config = {'strict': True}
```

---

### Celery Suggestion

**Definition:** Proposing Celery for concurrent brain query handling or any in-process concurrency.

**Rule:** `PROHIBITED = Stack Hallucination. asyncio.TaskGroup handles concurrent I/O without Celery overhead.`

**Why:** Celery requires a message broker (Redis/RabbitMQ) — architectural complexity not in this stack. For concurrent I/O (brain queries, API calls), asyncio.TaskGroup is the correct primitive. Celery is for distributed task queues across processes — a different problem.

**Examples:**
- "Use Celery to run brain queries in parallel."
- "Add a Celery worker to handle the async consultation flow."
- Any mention of `@celery.task` decorator or `celery beat`

**Rejection format:**
```
Rejected: Celery is not in uv.lock and violates the asyncio.TaskGroup constraint.
Source: global-protocol.md > Stack Hard-Lock | brain-05-backend/warnings.md > Celery Suggestion
```

---

### Synchronous ORM

**Definition:** Using SQLAlchemy `Session` (not `AsyncSession`) or the `.query()` interface (SQLAlchemy 1.x API) for database operations.

**Rule:** `PROHIBITED. SQLAlchemy 2.x async driver only — all operations must be awaitable.`

**Why:** Synchronous ORM calls block the asyncio event loop. Under concurrent brain queries, a blocking DB call would cause the entire server to stall until the query completes.

**Examples:**
- `session.query(User).filter(User.id == id).first()`
- `db.Session()` instead of `db.AsyncSession()`
- Using `scoped_session` instead of `AsyncSession` with dependency injection

**Rejection format:**
```
Rejected: synchronous SQLAlchemy session violates async driver requirement.
Source: global-protocol.md > Stack Hard-Lock | brain-05-backend/warnings.md > Synchronous ORM
```

---

### Route Business Logic

**Definition:** Embedding business logic directly in FastAPI route handlers instead of delegating to the service/repository layer.

**Rule:** `ANTI-PATTERN. Repository pattern — routes orchestrate, repositories query, services apply rules.`

**Why:** Route handlers that contain business logic cannot be unit-tested without spinning up the full HTTP stack. Business rules belong in services; data access belongs in repositories; routes wire them together.

**Examples:**
- FastAPI route function exceeding 20 lines of non-orchestration logic
- Direct `await session.execute(select(Model).where(...))` inside a route handler
- Validation logic beyond Pydantic model validation embedded in route body

**Correction pattern:**
- Route: accepts request, validates schema, calls service, returns response model
- Service: applies business rules, coordinates repositories
- Repository: executes queries, returns domain objects

---

### Pip Reference

**Definition:** Suggesting `pip install`, `requirements.txt`, or `setup.py` for dependency management.

**Rule:** `PROHIBITED = Stack Hallucination. uv add only.`

**Why:** The project uses `uv` exclusively. `pip install` bypasses `uv.lock` and can introduce version conflicts. Requirements.txt is not how uv manages dependencies.

**Examples:**
- "Run `pip install pydantic` to add the dependency."
- "Add to `requirements.txt`: fastapi>=0.100"
- "python setup.py install"

**Rejection format:**
```
Rejected: pip install violates uv-only package management rule.
Source: global-protocol.md > Stack Hard-Lock | brain-05-backend/warnings.md > Pip Reference
```
