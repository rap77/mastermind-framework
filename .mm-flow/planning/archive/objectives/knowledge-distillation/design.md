# Design — knowledge-distillation

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Reuse existing backend analytics routes (`/api/analytics/system-health`,
  `/api/analytics/templates`, `/api/analytics/outcome-metrics`) instead of
  inventing a second knowledge-distillation backend.
- Favor a read-only web surface first so operators can observe whether
  distillation is alive before changing the learning loop itself.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.
- For the first slice, prefer a focused web/API integration path that proves the
  current UI can consume existing knowledge-distillation signals.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer surfacing already-implemented backend signals over rebuilding dormant
  knowledge-distillation machinery.

## Context Notes
- Historical evidence shows backend KD infrastructure already exists:
  - `apps/api/mastermind_cli/orchestration/distillation_service.py`
  - `apps/api/mastermind_cli/orchestration/analytics_service.py`
  - `apps/api/mastermind_cli/api/routes/analytics.py`
- The likely product gap is visibility, not core pipeline absence.

## Phase 1 Slice

### Goal
Expose a read-only knowledge-distillation panel in a current operator surface by
reusing existing analytics/template endpoints.

### Likely Touchpoints
- `apps/web/src/lib/...` fetch helpers for analytics routes
- a current dashboard surface (likely `/project-state` or another existing
  operator console)
- focused frontend/API tests

### Explicit Non-Goals
- no changes to scoring thresholds
- no changes to template extraction persistence
- no new KD backend API unless the current routes prove insufficient
