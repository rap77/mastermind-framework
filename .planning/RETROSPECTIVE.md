# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

---

## Milestone: v2.1 — War Room Frontend

**Shipped:** 2026-03-25
**Phases:** 4 (05–08) | **Plans:** 16 (21 executed) | **Sessions:** ~12

### What Was Built

- **Command Center** — Magic UI Bento Grid with 24 brain tiles, live WebSocket status updates (RAF-batched), Raycast-style brief modal with Cmd+Enter, DOMPurify XSS prevention
- **The Nexus** — React Flow DAG with dagre layout, custom BrainNode (React.memo + nodrag/nopan), WS illumination state machine, Cooldown Mode, Ghost Trace edges
- **Strategy Vault** — Execution history list (TanStack Query), detail view with SmartMarkdown (GFM + VS Code Dark syntax highlighting), SnapshotScrubber timeline
- **Engine Room** — react-virtuoso virtual scroll logs, level filtering (info/warn/error), API key CRUD (show-once + masked), brain YAML config viewer
- **Focus Mode** — Auto-activates on task start, sidebar collapses, idle brain tiles dim, Esc exit with no re-trap logic

### What Worked

- **Brain consultations before planning:** mm:brain-context skill at Moments 1–3 caught architectural gaps early (INSERT OR IGNORE concurrency, slowapi rate limiting, GraphEdge schema) before they became bugs
- **Wave-based execution:** Breaking phases into atomic waves with commit-per-task kept work reversible and session-safe
- **TDD + Nyquist:** Starting each phase with test scaffolds and per-task verification map maintained 0 failures throughout — caught Immer MapSet issue in tests before runtime
- **Tech debt tracking:** Documenting 12 tech debt items explicitly prevented scope creep during execution — all deferred cleanly to v2.2
- **Gap closure as dedicated plan:** 05-04 gap closure pattern proved valuable — fix the bug in isolation, document explicitly, don't mix with feature work

### What Was Inefficient

- **Nyquist agents modified existing tests:** Nyquist auditor agents for phases 05–08 modified existing passing tests rather than only creating VALIDATION.md — required revert and manual VALIDATION.md creation. Cost: ~1 session
- **STATE.md staleness:** STATE.md reflects the state at last explicit update — it lagged behind actual progress in later sessions. Serena memories + git log were more reliable
- **Phase 07 ROADMAP.md not marked complete:** The ROADMAP had Phase 7 with `[ ]` checkboxes (no SUMMARY checkbox format) — caused confusing "roadmap_complete: false" in analysis
- **Tech debt branch needed:** 9 tech debt items accumulated over 5 weeks required a dedicated cleanup branch before milestone close — ideally some would be fixed in-phase

### Patterns Established

- **Moment 1–2–3 brain consultation protocol:** Before planning → During planning → After PLAN.md, before execution. Documented in `mm:brain-context` skill. Non-negotiable for all future milestones
- **RAF batching in brainStore (not WS handler):** Queue events in WS handler, drain in store's RAF loop — achieves 60fps at 24-brain concurrent events
- **NODE_TYPES/EDGE_TYPES at module level:** React Flow re-renders infinitely if these are defined inside component. Always module level + export for test isolation
- **React Flow CSS in @layer base:** Tailwind 4 silently breaks handles/edges if CSS imported from tsx. Must be in globals.css @layer base
- **JWT at Server Components + Route Handlers:** Not just middleware — CVE-2025-29927 requires dual-layer verification
- **enableMapSet() for Immer Maps:** Required for Map<brainId, BrainState> iteration in Immer set() callbacks. Include in boilerplate for future stores with Maps
- **Nyquist = VALIDATION.md only (never new tests for phases with existing tests):** When tests already exist, Nyquist auditing means writing/updating VALIDATION.md to map existing tests to requirements — not creating new tests

### Key Lessons

1. **Static star topology is fine for v2.1 Nexus:** The real DAG proxy exists but NexusCanvas uses star topology — this is acceptable UX for current phase. Don't over-engineer before requirements are proven
2. **Cursor pagination with composite keys prevents race conditions:** `WHERE (created_at, id) > (cursor_time, cursor_id)` eliminates duplicated entries under concurrent writes — use this pattern for all future paginated endpoints
3. **Session invocation counts work write-but-not-read:** Store writes `sessionInvocationCounts` correctly, but BrainNode read path needed explicit wiring (was stubbed) — catch these in integration tests, not unit tests
4. **Monorepo pre-commit hooks need `cd apps/X`:** All pre-commit hooks running Python/Node tools must explicitly `cd` to the correct app directory — `bash -c 'cd apps/api && uv run ...'`
5. **Immer mutation error is silent in non-test environments:** The brainStore RAF batching bug only surfaced in test (returned 0 events). Always test store mutations with actual drain verification

### Cost Observations

- Model mix: ~80% sonnet, ~20% opus (brain consultations + code review)
- Sessions: ~12 over 7 days (2026-03-18 → 2026-03-25)
- Most expensive: Phase 08 execution (5 waves, 48 commits, 90 files) — ~3 sessions
- Most efficient: Phase 06 (3 plans, single session) — brain consultations pre-validated architecture

---

## Cross-Milestone Trends

| Metric | v2.0 | v2.1 |
|--------|------|------|
| Phases | 4 | 4 |
| Plans | 17 | 21 |
| Tests | 467 | 982 |
| Sessions | ~10 | ~12 |
| LOC (total) | ~14,275 | ~30,311 |
| Gap closures | 2 | 5 |
| Tech debt items | 4 | 9 |

**Trend:** Gap closure plans are increasing (2 → 5). Consider building explicit gap-closure buffer into phase planning (e.g., reserve plan slot N+1 for gap closure at planning time).

**Trend:** Tech debt accumulation is growing. v2.2 should include a dedicated cleanup phase in the roadmap.
