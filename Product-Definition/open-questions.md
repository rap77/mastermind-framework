# Open Questions — Multi-Harness Architecture

> Ambiguities pre-declared during Discovery that AI-DLC Workflows must resolve during
> Inception (Requirements Analysis) before proceeding to Application Design.
>
> Total: 8 questions. Priority-ordered.

---

## OQ-1: SAL Gate Implementation Pattern

**Context:** The governance interceptor must evaluate intentions before the Coordinator executes them.

**Options to resolve:**
- A) **Decorator pattern** — `@governance_check` on Coordinator methods
- B) **Context manager** — `async with governance.gate(intention): ...`
- C) **Middleware class** — Separate class injected via DI that wraps the Coordinator call
- D) **Pre-hook in orchestrate()** — First lines of `Coordinator.orchestrate()` call `self.governance.evaluate()`

**Constraints:**
- Must not require modifying existing callers of `Coordinator.orchestrate()`
- Must be testable in isolation (mock governance, test Coordinator; mock Coordinator, test governance)
- Must produce audit trail entries regardless of verdict

**Recommendation:** C or D — C for cleanliness, D for minimal diff. Resolve during Application Design.

---

## OQ-2: Budget Tracking Persistence

**Context:** Token consumption must be tracked per-task and per-session. Question is WHERE to persist.

**Options:**
- A) **In-memory counter** — Simple, fast, lost on crash
- B) **PostgreSQL record per call** — Durable, queryable, overhead per call
- C) **Append-only JSON Lines file** — Durable, low overhead, parsed at session start for resume
- D) **Redis counter** — Fast, semi-durable, natural TTL for sessions

**Constraints:**
- Must survive process restart (checkpoint resume requires knowing tokens spent)
- Must not add >1ms latency per tool call
- Must be queryable for morning reports and meta-loop metrics

**Recommendation:** C for MVP (JSON Lines in `.mm-flow/planning/`), migrate to B when PostgreSQL is the primary runtime store.

---

## OQ-3: Meta-loop Trigger Mechanism

**Context:** The meta-loop collects execution metrics and proposes harness rule updates. When does it run?

**Options:**
- A) **Cron** — Weekly scheduled job (e.g., Monday morning before work starts)
- B) **Event-driven** — Triggers after N consecutive failures of same type, or after threshold metric drop
- C) **Post-session** — Runs analysis at end of every session (lightweight check)
- D) **Hybrid** — C for lightweight anomaly detection + A for full rule-update cycle

**Constraints:**
- Must not consume significant tokens itself (meta-loop is governance, not production work)
- Must produce actionable rule proposals, not just reports
- Must respect Q3 decision: auto-apply minor rules, require approval for execution rules

**Recommendation:** D — lightweight post-session check catches urgent patterns; weekly full analysis proposes structural changes.

---

## OQ-4: Qrel Generation Automation

**Context:** 18-20 qrels are needed for the first eval harness. User provided 12 concrete examples. The rest need creation.

**Options:**
- A) **Manual curation only** — Human writes all qrels by hand (highest quality, lowest scale)
- B) **Semi-automated extraction** — Script scans canonical docs, proposes candidate queries + gold answers; human validates
- C) **LLM-assisted** — Use a model to generate candidate qrels from docs; human curates top-K

**Constraints:**
- Qrels MUST be sealed (system under test cannot see them)
- Gold sources must be exact file references
- Expected answers must be specific enough to score objectively
- User prioritized: Decisions (4), Fixes (4), Temporal (4), State (3), Isolation (3), Cross-project (1-2)

**Recommendation:** B — script extracts decision/fix patterns from docs; human validates and adds temporal/isolation cases manually.

---

## OQ-5: Eval Scorer Integration with pytest

**Context:** The eval harness runs as a CI gate. How does it integrate with the existing pytest infrastructure?

**Options:**
- A) **pytest plugin** — Custom pytest markers (`@pytest.mark.eval_harness`) that run scorer and assert threshold
- B) **Standalone script** — Separate `python -m evaluation.scorer` invoked by CI after tests pass
- C) **pytest conftest fixture** — Scorer as a session-scoped fixture that loads qrels and asserts at teardown

**Constraints:**
- Must not slow down regular test suite (eval may take 5-10s due to retrieval calls)
- Must produce machine-readable scorecard (JSON) for baseline comparison
- Must fail CI explicitly with clear "score dropped from X to Y" message
- Must run against the Phase 1 corpus (99 docs)

**Recommendation:** B — standalone script keeps eval decoupled from unit tests; CI runs it as separate job with its own pass/fail.

---

## OQ-6: Governance Interceptor Registration Pattern

**Context:** The GovernanceInterceptor needs to be injected into or before the Coordinator. How?

**Options:**
- A) **Constructor injection** — `Coordinator(governance=GovernanceInterceptor(...))`
- B) **Module-level registration** — `governance.register(coordinator)` at startup
- C) **Factory function** — `create_coordinator(with_governance=True)` that wires dependencies
- D) **Middleware stack** — Coordinator has a `middleware: list[Middleware]` field; governance is one entry

**Constraints:**
- Existing callers of `Coordinator()` must not break (backward-compatible)
- Must allow disabling governance for tests that don't need it
- Must allow multiple governance policies (SAL + budget + scope) in defined order

**Recommendation:** A with defaults — `Coordinator(governance=None)` preserves backward compat; when governance is provided, it's called first. Future: D for multiple middlewares.

---

## OQ-7: Evidence Chain Format

**Context:** Every governance decision needs an audit trail. What format?

**Options:**
- A) **JSON Lines file** — One JSON object per event, append-only, per-session file
- B) **SQLite** — Single-file DB, queryable, portable
- C) **PostgreSQL table** — Part of main DB, joins with tasks/runs
- D) **Structured log (structlog)** — Emitted as log entries, captured by log infrastructure

**Constraints:**
- Must be append-only (never truncate or rewrite)
- Must be human-readable for debugging
- Must be machine-parseable for meta-loop analysis
- Must support replay (reconstruct what happened in order)
- Must survive session crashes (no buffered-only data)

**Recommendation:** A for MVP (JSON Lines in `.mm-flow/planning/audit/` — already have audit dir pattern). Migrate to C when PostgreSQL is primary runtime.

---

## OQ-8: Overnight Mode Resume Protocol

**Context:** After overnight cautious mode pauses (due to failures or budget exhaustion), how does the next session resume?

**Options:**
- A) **Checkpoint file** — `overnight-checkpoint.json` with last completed task, remaining queue, failure log
- B) **Morning report + manual resume** — Generate report; human decides what to resume/skip
- C) **Auto-resume next morning** — If failures were transient, retry automatically at next scheduled window
- D) **Hybrid** — A + B: checkpoint always written; morning report generated; human reviews before next run

**Constraints:**
- Must not lose work (completed tasks are committed before pause)
- Must not retry known-bad tasks without human review
- Must provide clear "here's what happened, here's what's left" summary
- Must respect the cautious policy (don't resume aggressively)

**Recommendation:** D — checkpoint always persisted; morning report generated (per doc 18 template); human reviews and triggers next run or skips failed tasks.

---

## Summary for AI-DLC Inception

| Question | Key Decision | Resolve During |
|---|---|---|
| OQ-1 | SAL gate pattern (decorator/middleware/hook) | Application Design |
| OQ-2 | Budget persistence (JSON Lines → PostgreSQL) | Application Design |
| OQ-3 | Meta-loop trigger (post-session + weekly) | Application Design |
| OQ-4 | Qrel generation (semi-automated + human validation) | Requirements Analysis |
| OQ-5 | Eval/pytest integration (standalone script) | Functional Design |
| OQ-6 | Governance registration (constructor injection) | Application Design |
| OQ-7 | Evidence chain format (JSON Lines → PostgreSQL) | Functional Design |
| OQ-8 | Overnight resume (checkpoint + morning report + human review) | Application Design |
