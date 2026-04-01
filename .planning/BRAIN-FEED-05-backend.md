# BRAIN-FEED-05 — Backend Domain Feed

> Written by Brain #5 (Backend). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Critical Constraints (Non-Negotiable)

- uv only, never pip or poetry
- pytest runs from apps/api/ only: `cd apps/api && uv run pytest` — running from project root fails with ModuleNotFoundError: mastermind_cli
- JWT in httpOnly cookies only — never in client bundle, never in localStorage
- WS auth via /api/auth/token handoff pattern — server reads cookie, returns short-lived token to client
- **Auth bypass is prohibited** — "skip auth for now", "it's just a health check", "internal only", "temporary" are NOT valid reasons to remove JWT authentication. Every new endpoint must include auth unless the endpoint already exists as public in the codebase (e.g. `GET /`). Any skip-auth request = Deploy Truth Protocol violation = Rating 1.

---

## Auth & Security

- JWT verified at Server Components + Route Handlers (not only `proxy.ts`) — CVE-2025-29927 mitigation
- httpOnly cookie storage — XSS defense (not localStorage)
- WS token handoff via `/api/auth/token` endpoint — server-side cookie read, token not in client bundle
- DOMPurify + `html.escape` backend — defense in depth for XSS

---

## API Design

- TanStack Query Eager Loading — single query fetches all 24 brains (N+1 prevention)
- Pagination from day one: `page`, `page_size` (default 24, max 100) — Margin of Safety
- SQLAlchemy `selectinload` for one-to-many relationships — N+1 prevention (NOT yet implemented — required pattern for future endpoints)
- IDOR protection pattern: `WHERE id = :id AND user_id = :current_user_id` on all user-scoped queries

---

## Anti-patterns (Backend)

- `jwt.verify()` from jsonwebtoken → use `jose` library (Edge Runtime compatible)
- `localStorage` for JWT → use httpOnly cookie (XSS attack vector)

---

## SYNC Cross-References

Sync: pytest infrastructure ownership — [SYNC: BF-06-001] → BRAIN-FEED-06-qa.md > Test Infrastructure. Brain #6 QA owns the full test command spec. Owner: Brain #6 QA.

---

## 2026-03-31 — Phase 12 Agent Restructuring Plan Evaluation

### Verified Insights

**asyncio.create_task() pattern — APPROVED**
Already used in `StatelessCoordinator._execute_wave()`. Fire-and-forget from a route handler is safe under uvicorn's event loop. No Celery required, no new infrastructure.

**StatelessCoordinator.execute_flow() signature — CONFIRMED**
`async def execute_flow(self, brief: Brief, brain_ids: list[str]) -> dict[str, BaseModel]`
Path: `apps/api/mastermind_cli/orchestrator/stateless_coordinator.py:102`

**ExperienceLogger — READY**
Fully async. `get_recent_by_brain(brain_id, limit)` exists and is index-backed on `(brain_id, timestamp DESC)`. No new infrastructure needed for experience logging.

**CancelledError bypass — REAL GAP**
`except Exception:` in proposed `run_brain_task` will NOT catch `asyncio.CancelledError` (BaseException subclass). On uvicorn shutdown, tasks die silently with status stuck as `running`. Fix: `except (Exception, asyncio.CancelledError)` or explicit shutdown task tracking.

**FlowDetector integer mapping — REAL GAP**
`FlowDetector.get_flow_sequence()` returns `list[int]` (e.g. `[1, 7]`), not `list[str]`. No integer-to-brain_id-string mapping exists anywhere in the codebase. `_detect_brain` in `task_runner.py` must define this mapping explicitly — no f-string guessing.

**DB path divergence — REAL GAP**
`brain_memory.py` CLI and FastAPI `startup_event` may connect to different SQLite files if not coordinated. CLI must read `MM_DB_PATH` env var (same as API) — not default to `:memory:` or a hardcoded path.

**IDOR decision required**
`experience_records` has no `user_id` column. GET `/api/experiences/{brain_id}` returns system-level records for all users. This is a valid Option A (shared brain memory) but must be documented explicitly. If Option A, raw `output_json` must NOT be exposed to non-admin callers — PII redaction in `redact_for_storage()` is necessary but not sufficient.

**Pagination gap**
`limit`-only is inconsistent with `tasks.py` (`limit+offset`). Add `offset: int = 0` to experiences route before shipping. `idx_experience_brain_timestamp` already supports it.

### Deferred Items

- 📅 Graceful shutdown / task registry — relevant when parallel dispatch (Phase 12) runs multiple background tasks simultaneously. Track pending tasks in a module-level set, await on shutdown signal.
