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

## Milestone: v2.2 — Brain Agents

**Shipped:** 2026-03-30
**Phases:** 4 (09–12) | **Plans:** 15 | **Sessions:** ~10

### What Was Built

- **7 Brain Subagents** — `.claude/agents/mm/brain-NN-*/` with embedded intermediary protocol, domain-specific criteria.md, anti-patterns.md, and warnings.md
- **Two-Level BRAIN-FEED** — Global `BRAIN-FEED.md` (cross-domain patterns) + 7 domain feeds `BRAIN-FEED-NN-domain.md` — no cross-domain pollution
- **5 Pre-Migration Baselines** — `tests/baselines/baseline-01..05.md` with Delta-Velocity schema before any agent migration
- **Sentinel Script** — `tests/smoke/verify_feed_isolation.sh` extended with barrier-order, crosstalk, and mcp-elimination checks
- **Parallel Dispatch** — `mm:brain-context` rewritten (moment-2, moment-3, ask-all, ask-*.md × 7) to use Agent tool dispatch with Phase A (SYNC) / B (parallel) / C (Brain #7 barrier) pattern
- **RED Test Stubs** — `tests/brain_agents/test_parallel_dispatch.py` + `test_sync_injection.py` documenting expected behavior for future GREEN implementation

### What Worked

- **model:inherit discovery early (Phase 11):** Smoke tests caught that `model: inherit` is not a valid keyword — caught in dedicated validation phase before wiring dispatch. Cost: 0 rework in Phase 12
- **Adversarial prompt design:** Hardcoded adversarial prompts (e.g., Brain #4 asked about Redux when Zustand 5 is locked) provided objective pass/fail — subjective "does it look good" tests avoided
- **Wave 0 pattern for infrastructure:** Creating test stubs + extending sentinel script before feature work (Phase 12) kept infrastructure always ahead of implementation
- **Scoped grep in sentinel:** `mcp-elimination` check scoped to operational files prevented test noise from MCP references in test fixtures — learned from false-positive in code review

### What Was Inefficient

- **Inline execution when subagent permissions denied:** Phase 12 all 4 plans executed inline when subagent write permissions were denied at session start — required same-session re-execution. Cost: ~2 sessions
- **ROADMAP.md Phase 11 stale checkbox:** Phase 11 had `[ ]` plans in ROADMAP even after completion — caught in code review before closure. Now fixed: ROADMAP updated atomically at phase completion
- **Milestone closure context limit:** v2.2 closure attempted at 81% context — required fresh session. `/gsd:complete-milestone` should be the first command in a fresh context

### Patterns Established

- **Phase A/B/C dispatch pattern:** Phase A = SYNC resolution (required data before parallel), Phase B = parallel domain agents, Phase C = Brain #7 barrier. Standard template for all future mm:brain-context workflows
- **model:""  not model:inherit:** Brain agents must use `model: ""` (empty string = inherit from launcher) — `model: inherit` is not a valid Claude Code keyword, causes silent fallback
- **Brain #7 barrier:** Evaluator always dispatched after domain agents complete, never in parallel — it needs domain outputs as context to synthesize
- **RED stubs as contracts:** When full implementation deferred, RED stubs document expected behavior and prevent "silent passing" if test file deleted

### Key Lessons

1. **Fresh context for milestone closure:** Always `/clear` before `/gsd:complete-milestone` — the closure workflow reads and writes many files, needs full context budget
2. **Sentinel false-positive risk:** Grep patterns that match test fixtures cause false-positive failures — always scope to operational file paths, not whole repo
3. **Subagent write permission must be confirmed at session start:** If subagent writes are denied, the entire wave-based strategy needs to switch to inline. Catch this before writing plans
4. **Delta-Velocity schema as objective metric:** Baseline schema (T1/T2/T3, gap-count, quality-rating 1–5) enables objective comparison post-migration — without it v2.2 would have no measurement of improvement

### Cost Observations

- Model mix: ~75% sonnet, ~25% opus (brain consultations + code review + plan generation)
- Sessions: ~10 over 3 days (2026-03-27 → 2026-03-30)
- Most expensive: Phase 09 (7 brain bundles + 5 baselines, 4 plans) — ~3 sessions
- Most efficient: Phase 10 (3 plans, feed split was mechanical) — ~1 session

---

## Cross-Milestone Trends

| Metric | v2.0 | v2.1 | v2.2 |
|--------|------|------|------|
| Phases | 4 | 4 | 4 |
| Plans | 17 | 21 | 15 |
| Tests | 467 | 982 | 985 (+3 RED stubs) |
| Sessions | ~10 | ~12 | ~10 |
| LOC (total) | ~14,275 | ~30,311 | ~30,311 + agents |
| Gap closures | 2 | 5 | 1 (validation gaps) |
| Tech debt items | 4 | 9 | 9 (carried) |

**Trend:** Gap closure plans are increasing (2 → 5 → 1). The single gap closure in v2.2 (Nyquist validation fixes) suggests the audit + fix loop is tightening.

**Trend:** v2.2 was faster (3 days vs 7 days for v2.1) despite similar scope — parallel planning + brain consultation upfront reduces mid-execution surprises.

**Trend:** Tech debt at 9 items — unchanged since v2.1. v3.0 should include a dedicated cleanup phase or the list will compound.
