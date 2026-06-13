# Design — context-window-management

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Reuse the existing `window_scheduler` core as the integration point.
- Extend `BackendSession` with the minimal context capability profile fields
  named in the canonical doc:
  - `max_context_window`
  - `recommended_working_window`
  - `max_output_window`
  - `long_context_quality`
  - `compression_preference`
- Add a small pure evaluator helper that receives:
  - backend capability profile
  - required context tokens
  - expected output tokens
  and returns a fit assessment with:
  - `fit_state`
  - `compression_required`
  - `risk_level`
  - `recommended_strategy`
- Prefer a pure function / dataclass-style contract for this first slice so it
  can be tested without DB or runtime orchestration.

## Dependencies
- Depends on `window-scheduler`

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer a reusable read-only evaluator over immediately coupling to scheduler
  state transitions.
- Prefer explicit capability fields over hidden provider heuristics.

## Context Notes
- Canonical architecture already defines the fit states and minimum model
  profile fields; the first slice should only encode those rules, not all
  downstream workflow effects.
