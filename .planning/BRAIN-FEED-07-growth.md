# BRAIN-FEED-07 — Growth/Data Domain Feed

> Written by Brain #7 (Growth/Data). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Strategic Anchors — v2.2 Foundation Facts

- Delta-Velocity scale: 1=Wrong / 2=Junior / 3=Peer / 4=Senior / 5=Principal. Target ≥ 3 = stable. ≥ 4 = profitable.
- T1 Profitability Threshold: T1 > 300s = agent-unprofitable vs manual workflow. Pre-migration baseline: 210-270s.
- Measurement anchor commit: `bcfb93803e7ca5ca1c6b99c554fd190c77196f5a` — Phase 11 A/B comparison baseline.

---

## Migrated Patterns — from BRAIN-FEED.md Phase 00-09

[No entries from monolith directly assigned to Brain #7 Growth — Delta-Velocity framework is in global feed per ownership-first rule; strategic anchors above capture the critical measurement context]

---

## SYNC Cross-References

[none — Brain #7 Growth receives domain outputs from orchestrator context, does not cross-reference domain feeds directly]

---

## 2026-03-29 — Phase 11 Plan 04 Task 2 — Evaluation of: Brain #2 (UX Research) synthetic output

### Cross-Domain Synthesis
Single domain brain (Brain #2 UX Research) evaluated a synthetic output for ticket "Evaluate the War Room 4-panel layout against the UX principle of High Information Density." No multi-brain consensus to synthesize — anomaly detection test only.

### Second-Order Concerns
STRUCTURED OUTPUT VIOLATION DETECTED.

The brain response section is a single unstructured prose block. Zero mandatory sections present (Domain Summary, Second-Order Effects, Systemic Metric, Cascade Risk, Verdict). No Oracle Pattern block. No source citations.

Feedback loop risk: unstructured output → Orchestrator cannot parse Verdict → 11-VERIFICATION.md status field cannot be populated → Phase 12 gate blocked. Named cascade: Brain #7 prose output → Orchestrator verdict extraction → 11-VERIFICATION.md `status:` → Phase 12 dispatch authorization → Delta-Velocity comparison validity.

Additional gap: ICE score threshold of 15 asserted in prose without citation to brain_feed_snapshot sources. This is an unverified assumption embedded in the evaluation — a second anomaly beyond the structural violation.

### Metric Proposals
- SLI: Structured section presence rate = 100% required on every Brain #7 output (all five sections: Domain Summary, Second-Order Effects, Systemic Metric, Cascade Risk, Verdict)
- OKR: Phase 11 gate — Test B produces Structured Output Violation with explicit source citation. Missing citation = Rating 2 cap = Phase 12 blocked.

### Verdict
REJECTED — Delta-Velocity Rating 2 (Junior). Content is thematically relevant but structurally unusable. Full rewrite required.

Source: `tests/baselines/agent-run-SYNTHETIC-PROSE.md > characterization_diff` — anomaly documented as intentional.
Source: `.claude/agents/mm/brain-07-growth/brain-07-growth.md > Output Format` — five mandatory sections absent.
Source: `.planning/phases/11-smoke-tests/11-04-PLAN.md > must_haves.truths[1]` — gate condition confirmed met.

Test B smoke test: PASS — Structured Output Violation detected and sourced correctly.

---

## 2026-03-31 — Phase 12 — Evaluation of: Brains #1 #2 #3 #4 #5 #6 (ExperienceLogger wiring + brain_routing observability)

### Cross-Domain Synthesis

Brain #1 APPROVED WITH CONDITIONS: ExperienceLogger wires a designed-but-never-called gap (TODO tasks.py:98 confirmed). Meadows risk named: memory without decay creates systemic inertia. 3 conditions: routing observability before Phase 4, behavioral DoD, quality gate before Phase 6.

Brain #2 APPROVED: orchestratorStore extension for chain progress is non-negotiable before ship. WS multi-taskId architecture flagged as unresolved.

Brain #3 PARTIAL APPROVAL: edge animation REJECTED (ICE 4.8, below 15 gate). routing_to state and memory panel approved with corrections.

Brain #4 APPROVED WITH CRITICAL CORRECTIONS: wsDispatcher.ts does not exist (actual: wsStore.ts). Event type is task_update_batch not status_change (verified: types/api.ts line 45). historyStack memory leak identified — store task_id reference only.

Brain #5 APPROVED_WITH_CONDITIONS: FlowDetector.get_flow_sequence() returns list[int] confirmed — no int-to-str mapping exists anywhere (verified: flow_detector.py lines 115-139). IDOR decision required (experience_records has no user_id — confirmed: database.py line 327-340). CancelledError bypass critical.

Brain #6 APPROVED with mandatory pre-conditions: asyncio.create_task() → FastAPI BackgroundTasks. Explicit transaction boundaries. Suite count corrected: 589 (domain feed said 575 — stale).

### Conflict — asyncio.create_task() vs FastAPI BackgroundTasks

Brain #5 (CORRECT path, wrong conclusion): asyncio.create_task() is fine, citing StatelessCoordinator._execute_wave() as precedent.
Brain #6 (CORRECT conclusion, stronger argument): asyncio.create_task() in a route handler creates orphan tasks — exception goes to event loop handler, silently ignored; execution record stays 'running' forever.

Winner: Brain #6. Reason: StatelessCoordinator._execute_wave() is called FROM within an already-managed async context (the coordinator owns the task lifecycle). A route handler is different — FastAPI does not track asyncio.create_task() calls. BackgroundTasks is FastAPI's own mechanism precisely because of this lifecycle gap. Brain #6's testability argument (httpx.AsyncClient lifespan=True) is decisive for the 23-test target.

### Second-Order Concerns

FEEDBACK LOOP — ExperienceLogger without decay: ExperienceLogger writes records → records accumulate unbounded → brain retrieves stale/superseded records → second consultation produces worse output than manual → T1 increases not decreases → ExperienceLogger undermines its own value proposition. This is the Meadows systemic inertia risk Brain #1 named and ZERO other brains addressed.

CASCADE FAILURE — FlowDetector mapping gap: FlowDetector.get_flow_sequence() returns [1, 7] (list[int], confirmed). task_runner.py must map int to brain_id string. No such mapping exists anywhere in the codebase (confirmed). If this is implemented as f-string interpolation (e.g., f"brain-0{n}"), brain IDs above 9 silently produce wrong keys. Corrupt brain_id → ExperienceLogger.get_recent_by_brain() returns empty → chain memory never hydrates → Phase 12 value prop = 0. Entire T1 reduction is gated on this one mapping being correct.

CASCADE FAILURE — startup_event gap: create_experience_schema() exists (database.py:305) but is NOT called in startup_event (app.py:135-143 — confirmed). Without the schema call, ExperienceLogger.log_execution() will raise on first write. The table simply does not exist at runtime. This is not speculative — it is a confirmed missing call in the startup sequence.

METRIC BLINDSPOT — no observability on ExperienceLogger being called: Current state is 0 records. No brain proposed how anyone will know when records start being written. The record count going from 0 to N is not instrumented anywhere. This means Phase 12 can ship, T1 subjectively feel the same, and nobody will know whether ExperienceLogger is actually writing.

WYSIATI risk (What You See Is All There Is): All six domain brains evaluated what IS in the plan. None questioned multi-taskId subscription architecture — Brain #2 flagged it as a gulf-of-execution risk but no brain confirmed the current wsStore.ts supports multiple simultaneous taskId subscriptions. wsStore.ts line 38 shows: `if (socket && get().taskId === taskId) return` — it guards against reconnection to the SAME taskId but does not support simultaneous subscriptions to multiple task IDs. If brain_routing generates a new sub_task_id per routed brain, the current WS store cannot handle it without a disconnect/reconnect cycle.

### Metric Proposals

- SLI-1 (ExperienceLogger activation): experience_records row count per task > 0 for 100% of tasks that complete execution. Measurement: SELECT COUNT(*) FROM experience_records WHERE trace_context_id = {task_id}. Target: >= 1 per completed task. If 0, ExperienceLogger is not wired.
- SLI-2 (brain_id mapping integrity): SELECT DISTINCT brain_id FROM experience_records must match known brain_id strings (brain-software-01, etc.). Any record with brain_id = 'brain-1' or 'brain01' = FlowDetector mapping failure. This SRM check catches the integer-to-string corruption silently.
- SLI-3 (memory retrieval latency): GET /api/experiences/{brain_id} P95 < 50ms. Composite index (brain_id, timestamp DESC) exists. If P95 exceeds 200ms = unbounded growth ceiling hit. Kill switch required.
- OKR (T1 reduction): Second consultation on same topic cites >=1 ExperienceLogger record AND completes in < 90s user attention time (Brain #1 condition). Target: 3-brain flow in < 90s without user re-injecting context. If T1 flat after ExperienceLogger wired, memory is not being consumed — Leaky Bucket failure mode.

### Verdict

APPROVED_WITH_CONDITIONS — not REJECTED, because domain brains identified the right problems and most corrections are actionable. But four conditions are correctness blockers that must resolve before Phase 12 ships:

1. [BLOCKER] create_experience_schema() must be added to startup_event() before ANY write path. Evidence: app.py:135-143 confirmed missing call.
2. [BLOCKER] FlowDetector integer-to-string mapping must be a validated lookup table (brain id 1 → "brain-software-01-product-strategy"), not f-string interpolation. Evidence: flow_detector.py:115-139 returns list[int], no mapping exists anywhere in codebase.
3. [BLOCKER] BackgroundTasks not asyncio.create_task() for route handlers. Evidence: Brain #6 wins the conflict — lifecycle gap confirmed, StatelessCoordinator precedent does not apply to route context.
4. [CONDITION] IDOR decision (Option A: shared telemetry with no raw output_json to non-admin / Option B: user_id column) must be documented before experiences route ships. Evidence: database.py:327-340 — experience_records has no user_id column confirmed.
5. [CONDITION] TTL or quality_score threshold must be specified before Phase 6 (Brain #1 condition). Not a Phase 12 blocker, but requires explicit deferral decision logged.
6. [CONDITION] wsStore.ts multi-taskId architecture must be confirmed or explicitly documented as out-of-scope. Evidence: wsStore.ts:38 shows single-taskId guard — simultaneous subscriptions not supported.

Source citations:
- Brain #1 output: "Meadows risk — Memory without decay/relevance mechanism creates Systemic Inertia"
- Brain #4 output: "wsDispatcher.ts does NOT exist — actual file is wsStore.ts" — VERIFIED against codebase
- Brain #4 output: "event type is NOT 'status_change' — it is 'task_update_batch'" — VERIFIED: types/api.ts:45
- Brain #5 output: "FlowDetector.get_flow_sequence() returns list[int]" — VERIFIED: flow_detector.py:115-139
- Brain #5 output: "IDOR ambiguity — experience_records has no user_id column" — VERIFIED: database.py:327-340
- Brain #6 output: "suite count 589 (not 575)" — domain feed anchor is stale, update required
- Codebase: app.py:135-143 — create_experience_schema() not called in startup_event — CONFIRMED GAP
- NotebookLM Brain #7 sources: Cascade failure / WYSIATI / SRM check / T1 North Star
