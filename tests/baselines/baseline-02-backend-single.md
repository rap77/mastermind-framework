---
schema_version: "1.0"
context_id: "bcfb93803e7ca5ca1c6b99c554fd190c77196f5a"
brain_id: 5
ticket_type: adversarial

brain_feed_snapshot:
  - .planning/BRAIN-FEED.md
  - .planning/STATE.md
  - apps/api/app/schemas/

input_prompt_raw: |
  Design the endpoint contract for streaming brain consultation results via Server-Sent Events (SSE).
  The endpoint must support mid-stream cancellation, return partial results on cancellation, and use
  asyncio.TaskGroup for concurrent brain queries. Specify exact Pydantic v2 models for request and response.

cognitive_trace:
  T1_setup_seconds: 240
  T2_ai_latency_seconds: 62
  T3_review_seconds: 175

delta_velocity_score: 3

characterization_diff: |
  Expected: Brain might suggest Celery for async task management, or use dict[str, Any] for flexible response schemas. Would likely omit mid-stream cancellation semantics.
  Observed: Brain correctly used asyncio.TaskGroup (not Celery), correctly specified Pydantic v2 strict models with no dict[str, Any], correctly addressed mid-stream cancellation via asyncio.shield() and CancelledError handling. Did not propose any out-of-stack dependencies.

human_intervention_log:
  - gap: "SSE response model used Optional[str] for partial result fields without explicit None default"
    correction: "Changed to Optional[str] = None across all partial response fields — Pydantic v2 requires explicit defaults for Optional fields in strict mode"
  - gap: "mid-stream cancellation returned 200 with partial data — no status differentiation"
    correction: "Added X-Cancellation-Reason header and 206 Partial Content status for cancelled streams — required for client-side state management"
---

# Baseline 02 — Backend Single-Brain (Adversarial: SSE Endpoint Contract)

## Frozen Context Block

**Vision (3-5 años):** Autonomous brain agents that accumulate domain knowledge and execute the intermediary protocol faster than a human expert.
**Strategic Intent:** v2.2 — Convert mm:brain-context skill workflows to autonomous subagents
**Outcome Metrics:** Agent executes protocol in <20% human T1 time; Delta-Velocity >= 3 on first run

---

## Ticket

Design the endpoint contract for streaming brain consultation results via Server-Sent Events (SSE). The endpoint must support mid-stream cancellation, return partial results on cancellation, and use asyncio.TaskGroup for concurrent brain queries. Specify exact Pydantic v2 models for request and response.

---

## Brain(s) Consulted

Brain #5 — Backend (Type-Safety Zealot)
Notebook: `c6befbbc-b7dd-4ad0-a677-314750684208`

---

## Raw Brain Response (Summary)

SIMULATED: Brain #5 response on SSE endpoint design:

**Endpoint:** `POST /api/v1/brains/consult/stream`

**Request model (Pydantic v2 strict):**
```python
class BrainConsultRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    brain_ids: list[int] = Field(..., min_length=1, max_length=7)
    ticket: str = Field(..., min_length=10, max_length=4000)
    frozen_context: FrozenContextBlock
    timeout_seconds: int = Field(default=120, ge=10, le=600)
```

**Response stream format (SSE):**
```python
class BrainChunk(BaseModel):
    model_config = ConfigDict(strict=True)

    brain_id: int
    chunk_type: Literal["insight", "gap", "warning", "complete", "cancelled"]
    content: str
    sequence: int
    is_final: bool
```

**asyncio.TaskGroup pattern:**
```python
async def query_brains_concurrent(brain_ids: list[int], ticket: str) -> AsyncIterator[BrainChunk]:
    async with asyncio.TaskGroup() as tg:
        tasks = {brain_id: tg.create_task(query_single_brain(brain_id, ticket)) for brain_id in brain_ids}
    for brain_id, task in tasks.items():
        yield BrainChunk(brain_id=brain_id, ..., is_final=True)
```

**Mid-stream cancellation:** Brain proposed wrapping individual brain queries with `asyncio.shield()` to allow task cancellation without corrupting the TaskGroup. On `CancelledError`, the endpoint flushes partial results before closing the SSE stream.

---

## Filtered Insights

**Survived grep verification (Step 5):**
- `asyncio.TaskGroup`: CONFIRMED — in Python 3.11+ stdlib, available in Python 3.14. No external dep.
- `Pydantic v2 ConfigDict(strict=True)`: CONFIRMED — correct v2 pattern, no v1 validators.
- `asyncio.shield()` for cancellation: CONFIRMED — correct pattern for partial-result SSE.
- No `dict[str, Any]` anywhere in the response: CONFIRMED — fully typed.

**Rejected:**
- `Optional[str]` without `= None` default: Minor Pydantic v2 strict mode violation. Corrected.
- 200 status for cancelled streams: Missing HTTP semantics. Corrected to 206 + `X-Cancellation-Reason` header.

---

## Gaps Found

1. **Optional field defaults** — Pydantic v2 strict mode requires explicit `= None` on all `Optional[str]` fields. Brain omitted defaults. Required 2 field corrections across the response model.

2. **HTTP status for partial delivery** — Brain returned 200 for both complete and cancelled streams. In practice, clients need to distinguish. Added 206 Partial Content for cancelled streams and `X-Cancellation-Reason` header. Brain did not spontaneously propose this — required human domain knowledge about HTTP streaming semantics.

3. **No Rate Limiting mention** — Brain did not mention that the `/brains/consult/stream` endpoint needs rate limiting given concurrent TaskGroup spawning. This is a correctness gap for production, not a strict Pydantic violation.

---

## T1 Analysis

`T1_setup_seconds: 240` — Within the 300-second profitability threshold.

Steps during T1:
- Read `.planning/BRAIN-FEED.md` (70s) — find Backend architecture constraints, Python version, asyncio patterns in use
- Review `apps/api/app/schemas/` (60s) — understand existing Pydantic v2 model conventions and ConfigDict usage
- Build `[IMPLEMENTED REALITY]` block (60s) — document current API patterns, Pydantic version, asyncio usage
- Build `[CORRECTED ASSUMPTIONS]` block (50s) — confirm TaskGroup availability in Python 3.14, no Celery in stack

**Flag:** Not agent-unprofitable. T1 < 300s.

---

## Adversarial Validation Notes

Ground truth for adversarial ticket = adherence to system principles. Brain #5 passed on:
- No Celery suggestion (uses asyncio.TaskGroup as required)
- No `dict[str, Any]` anywhere in the response
- Pydantic v2 strict mode patterns throughout
- No unlocked external dependencies proposed

Brain scored 3 (Peer) — correct and principled, but did not proactively propose rate limiting or the HTTP 206 semantics for partial delivery. A Rating 4 response would have included both unprompted.
