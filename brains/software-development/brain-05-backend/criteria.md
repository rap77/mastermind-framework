# Brain #05-Backend — Evaluation Criteria

## Purpose

This file defines how to evaluate Brain #5 (Backend Architecture) responses against the Delta-Velocity Matrix. Use this file when rating a consultation output. The criteria are observable and domain-specific — not generic quality statements.

A response that "sounds correct" but cannot be rated against this table is a Rating 2 at best.

---

## Rating 3 (Peer) vs Rating 4 (Senior)

| Attribute | Rating 3 (Peer) | Rating 4 (Senior) |
|-----------|-----------------|-------------------|
| **Type safety** | Provides correct Pydantic v2 model with proper field types | Identifies where `Any` would leak through the model boundary — proposes TypeVar with bounds or Protocol instead |
| **Async pattern** | Correct use of async/await for database calls | Proposes asyncio.TaskGroup for concurrent operations, explains why sequential would be slower and why not to use gather without error handling |
| **API contract** | Correct FastAPI route with valid response model | Proposes response model that prevents internal field leakage — fields not in the response model cannot leak through |
| **Data modeling** | Correct SQLAlchemy 2.x async model definition | Identifies N+1 query risk and proposes selectinload/joinedload strategy before it becomes a production problem |
| **Error handling** | Returns appropriate HTTP status codes | Proposes domain exception hierarchy that maps to HTTP codes without coupling — domain layer doesn't import FastAPI |

**Observable distinction:** A Rating 3 response makes the feature work. A Rating 4 response makes the feature work AND prevents the next 3 bugs from occurring.

---

## Auto-Reject (Rating 1)

**Any Contamination:**
Any response suggesting `dict[str, Any]` for a data model = Rating 1. Type-Safety Zealot core violation. The entire value of Pydantic v2 strict mode is eliminated by Any types.

```
Rejected: dict[str, Any] violates Type-Safety Zealot constraint.
Source: global-protocol.md > Stack Hard-Lock | brain-05-backend/warnings.md > Any Contamination
```

**Celery Suggestion:**
Any response suggesting Celery for concurrent brain query handling = Stack Hallucination = Rating 1. asyncio.TaskGroup handles concurrent I/O without Celery overhead. Celery requires a broker (Redis/RabbitMQ) — not in the stack.

```
Rejected: Celery is not in uv.lock and violates the asyncio.TaskGroup constraint.
Source: global-protocol.md > Stack Hard-Lock | brain-05-backend/warnings.md > Celery Suggestion
```

---

## Rating 5 (Architect) Threshold

A Rating 5 response:
- Identifies a boundary condition in the asyncio event loop that would cause a data race under concurrent brain queries — proposes a lock strategy that preserves throughput
- Redesigns the data model boundary so that a future schema migration requires zero application code changes (schema evolution without coupled migration)
- Identifies a cross-layer coupling that would make the system untestable at scale — restructures the dependency graph so that every layer is independently testable
- Catches a security boundary violation that the team didn't know existed (e.g., internal field leaking through response model despite not being in the schema)

---

## Minimum for Rating 3

A response must satisfy ALL of the following to be Rating 3:

1. Uses Pydantic v2 `BaseModel` — not TypedDict, not dataclass, not dict for any structured data
2. Uses SQLAlchemy 2.x async patterns — `AsyncSession`, `await session.execute()`, not `.query()` interface
3. Uses `asyncio.TaskGroup` for concurrent operations — not `asyncio.gather` without error handling, not Celery
4. References `uv` for any package operations — not pip
5. Does not embed business logic in FastAPI route handlers — routes orchestrate, repositories query, services apply rules

If any of these are missing, the response is Rating 2 regardless of how architecturally sound it sounds.

---

## Evaluation Checklist

When rating a Brain #5 response, verify:

- [ ] Did the brain read BRAIN-FEED.md before responding? (Step 1 — ask to show it)
- [ ] Does the `[IMPLEMENTED REALITY]` block reflect the actual async stack (asyncio.TaskGroup, not Celery)?
- [ ] Are the 6 domain-specific `[CORRECTED ASSUMPTIONS]` present? (Step 3)
- [ ] Does the data model use Pydantic v2 `BaseModel` with no `Any` types?
- [ ] Is `asyncio.TaskGroup` used for concurrent operations (not sequential, not gather)?
- [ ] Is the repository pattern enforced — no raw SQL in route handlers?
- [ ] Did the brain write to `.planning/BRAIN-FEED-05-backend.md` only? (Step 6 — Feed Write Scope)

Failing 3+ checklist items = Rating 2 regardless of content quality.
