---
phase: 09-baselines-agent-authoring
plan: "01"
subsystem: testing
tags: [baselines, delta-velocity, cognitive-load, brain-agents, measurement]

requires:
  - phase: 08-strategy-vault-ux-polish
    provides: "Phase 07/08 implementation history used in retrospective tickets (NexusCanvas, Strategy Vault, brainStore RAF batching)"

provides:
  - "tests/baselines/baseline-schema.md — Delta-Velocity Matrix + Cognitive Load Split schema spec"
  - "5 pre-migration baseline consultation records with Frozen Context Blocks, cognitive_trace (T1/T2/T3), delta_velocity_score, and human_intervention_log"
  - "Measurement anchor at git commit bcfb93803e7ca5ca1c6b99c554fd190c77196f5a — enables exact reproduction in Phase 11 comparison"

affects:
  - "09-baselines-agent-authoring (plans 02+) — agent authoring follows these baselines"
  - "11-smoke-tests — identical tickets will be run through agents for comparison"
  - "12-parallel-dispatch — success criteria reference delta_velocity_score >= 3 from this baseline"

tech-stack:
  added: []
  patterns:
    - "Frozen Context Block as control variable — only ticket changes between baselines, product context fixed"
    - "Simulated baseline pattern — SIMULATED: prefix marks hypothetical responses for offline baseline capture"
    - "Oracle Pattern for adversarial validation — rejections cite specific source (global-protocol.md > rule name)"
    - "Multi-Brain Information Leak tracking — explicit table documenting what Brain #7 received vs what Brain #4 said"

key-files:
  created:
    - tests/baselines/baseline-schema.md
    - tests/baselines/baseline-01-frontend-single.md
    - tests/baselines/baseline-02-backend-single.md
    - tests/baselines/baseline-03-qa-single.md
    - tests/baselines/baseline-04-multibrain-e2e.md
    - tests/baselines/baseline-05-multibrain-e2e.md
  modified: []

key-decisions:
  - "All T1 values (210-270s) are below the 300s profitability threshold — manual skill is already profitable; agent ROI comes from T1 reduction, not from beating the threshold"
  - "Adversarial baseline 05 scored delta_velocity=4 (Senior) because Brain #4 detected IntersectionObserver + @xyflow/react v12 nodeInternals as the solution — a genuine architectural insight not in the ticket"
  - "Retrospective baseline 04 exposed information leak risk: imprecise language in Brain #4 output caused Brain #7 cascade error — enforces structured output requirement for Phase 09 agent system prompts"
  - "T3 in baseline 04 (310s) is elevated due to cascade re-run — primary driver for structured output enforcement in agent design"
  - "Backend suite run from root (uv run pytest apps/api/) fails with pre-existing ModuleNotFoundError for mastermind_cli — suite passes when run from apps/api/ directly (575 passed)"

patterns-established:
  - "T1 Profitability Threshold: baselines flag T1 > 300s as agent-unprofitable automation candidates"
  - "Retrospective = precision calibration (known ground truth); Adversarial = resilience test (adherence to principles)"
  - "Multi-brain cascade documented with Information Leak table — Brain #7 receives vs what domain brains originally said"

requirements-completed: [BASE-01, BASE-02]

duration: 10min
completed: "2026-03-28"
---

# Phase 09 Plan 01: Baselines Summary

**6 measurement-anchor files in tests/baselines/ capturing pre-migration Delta-Velocity scores (3 single-brain, 2 multi-brain E2E) with git timestamp proving baselines precede any .claude/agents/mm/ authoring**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-28T00:55:40Z
- **Completed:** 2026-03-28T01:05:11Z
- **Tasks:** 2
- **Files created:** 6

## Accomplishments

- Created `tests/baselines/` as an Intelligence Integration Test directory with a schema contract and 5 populated records
- All 5 baselines include Frozen Context Block, cognitive_trace (T1/T2/T3), delta_velocity_score, characterization_diff, and human_intervention_log — complete measurement surface for Phase 11 comparison
- Confirmed git timestamp ordering: baseline commits (b773258, a34f518) precede any `.claude/agents/mm/` commits (none exist yet)

## Task Commits

1. **Task 1: Create baseline-schema.md** - `b773258` (feat)
2. **Task 2: Create 5 baseline records** - `a34f518` (feat)

## Files Created

- `tests/baselines/baseline-schema.md` — Schema contract: Delta-Velocity Matrix (1-5), Cognitive Load Split (T1/T2/T3), T1 Profitability Threshold, Frozen Context Block template, ticket mix spec
- `tests/baselines/baseline-01-frontend-single.md` — Brain #4 Frontend, retrospective (RAF batching in brainStore), delta_velocity=3
- `tests/baselines/baseline-02-backend-single.md` — Brain #5 Backend, adversarial (SSE endpoint with asyncio.TaskGroup), delta_velocity=3
- `tests/baselines/baseline-03-qa-single.md` — Brain #6 QA, adversarial (agent integration test strategy, offline constraint), delta_velocity=3
- `tests/baselines/baseline-04-multibrain-e2e.md` — Multi-brain #4+#5+#7, retrospective (Strategy Vault state design), delta_velocity=3
- `tests/baselines/baseline-05-multibrain-e2e.md` — Multi-brain #4+#5+#7, adversarial (DAG virtualization, 50+ nodes), delta_velocity=4

## Delta-Velocity Summary

| Baseline | Brain(s) | Type | T1 (s) | delta_velocity | Flag |
|----------|----------|------|--------|----------------|------|
| 01 Frontend single | #4 | retrospective | 210 | 3 (Peer) | — |
| 02 Backend single | #5 | adversarial | 240 | 3 (Peer) | — |
| 03 QA single | #6 | adversarial | 225 | 3 (Peer) | — |
| 04 Multi-brain E2E | #4+#5+#7 | retrospective | 255 | 3 (Peer) | T3=310s elevated |
| 05 Multi-brain E2E | #4+#5+#7 | adversarial | 270 | 4 (Senior) | Highest T1 |

**Context ID (anchor for Phase 11 comparison):** `bcfb93803e7ca5ca1c6b99c554fd190c77196f5a`

## Decisions Made

- Baseline 05 scored delta_velocity=4 (not 3) because Brain #4 detected IntersectionObserver + @xyflow/react v12 nodeInternals as an unprompted architectural insight — this meets the Rating 4 definition (optimization not in the ticket).
- No T1 values exceeded 300s profitability threshold — all baselines are within the profitable range. T1 automation in Phase 10 will improve the margin, not rescue unprofitable workflows.
- Cascade re-run in baseline 04 (imprecise Brain #4 output → Brain #7 error → re-run) adds 50s to T3. This is the primary evidence for requiring structured output in agent system prompts (Phase 09 plans 02+).

## Deviations from Plan

None — plan executed exactly as written. All 6 files created with the specified content, ticket types, brain assignments, and delta_velocity scores.

## Issues Encountered

**Pre-existing backend suite failure (out of scope):** Running `uv run pytest apps/api/` from the project root fails with `ModuleNotFoundError: No module named 'mastermind_cli'` — a pre-existing conftest discovery issue unrelated to Plan 09-01. The suite passes fully when run from `apps/api/` directly (575 passed, 8 skipped). This failure existed before any changes in this plan (verified via git stash). Frontend suite: 407/407 passing.

## Next Phase Readiness

- Phase 09 Plan 02 (agent authoring) can begin — baseline timestamps are established as proof
- `.claude/agents/mm/` directory does not yet exist — any commit to that path will post-date these baselines
- Structured output requirement for agent system prompts is now evidence-backed (cascade re-run in baseline 04)
- delta_velocity=4 in baseline 05 (adversarial) sets the stretch target: agents should match or exceed manual on the same tickets

---
*Phase: 09-baselines-agent-authoring*
*Completed: 2026-03-28*
