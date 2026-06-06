# Tasks — mm-harness-gate-aware-roadmap-reranking

## Execution Rules

- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints,
  validation commands, and acceptance criteria.
- Treat this objective as **harness-sensitive**: prefer a small recommendation
  heuristic change over a broad roadmap redesign.

## T1: Define gate-aware reranking contract

### Purpose

Make the recommendation policy explicit before changing roadmap selection.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `requirements.md`
- `design.md`
- `tasks.md`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-gate-aware-roadmap-reranking`

### Acceptance Criteria

- [x] activation-ready gate statuses are explicit
- [x] reranking boundary is explicit
- [x] remaining tasks are specific enough to execute without improvisation

## T2: Implement gate-aware roadmap recommendation

### Purpose

Prefer an objective that can actually be activated now over a higher-priority
objective that is currently gate-blocked.

### Depends On

T1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/commands/mm/discover-handler.py`
- `tests/unit/test_mm_discover_workflow.py`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`

### Acceptance Criteria

- [x] roadmap recommendation prefers gate-ready objectives when available
- [x] blocked candidates still expose gate status in roadmap artifacts
- [x] tests cover reranking and activation follow-through

## T3: Refresh continuity and record the next harness gap

### Purpose

Update docs/handoff so another model knows the roadmap is now gate-aware and
what remains to be improved next.

### Depends On

T2

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/README.md`
- `.mm-flow/planning/HANDOFF-CURRENT.md`
- `HANDOFF-CURRENT.md`

### Validation Commands

- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-gate-aware-roadmap-reranking`

### Acceptance Criteria

- [x] docs and handoff describe gate-aware reranking clearly
- [x] the next harness gap is recorded explicitly
- [x] final validation passes and another model can continue from artifacts alone
