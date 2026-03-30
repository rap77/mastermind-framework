# BRAIN-FEED-06 — QA Domain Feed

> Written by Brain #6 (QA/DevOps). Read-only for other agents.
> Orchestrator reads this after all domain feeds to write BRAIN-FEED.md (global synthesis).
> Last updated: 2026-03-28

---

## Test Infrastructure

- `uv run pytest` must run from `apps/api/` — running from project root fails with pre-existing `ModuleNotFoundError` for `mastermind_cli`
- Vitest over Jest — ESM-native, better Next.js 16 integration
- `websocket-metrics.ts` with `WS_SLOS` — define guardrail metrics before implementing

---

## Baseline Anchors

- Adversarial baseline delta_velocity=4 signal: `@xyflow/react v12 nodeInternals` + `IntersectionObserver` was an unprompted Senior insight from Brain #4 — genuine delta_velocity=4 output not in the ticket. This is the stretch target for Phase 11 agent comparison.
- Current test suite state: 575 backend (apps/api/) + 407 frontend (apps/web/) — established Phase 08 completion baseline

---

## Anti-patterns (QA)

- `uv run pytest` from project root → use `cd apps/api && uv run pytest` (pre-existing conftest discovery issue)
