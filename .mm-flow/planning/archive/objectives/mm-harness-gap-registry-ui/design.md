# Design — mm-harness-gap-registry-ui

## Architecture / Boundaries
- Reuse the existing `/project-state` dashboard surface instead of inventing a separate harness UI route.
- Keep the first slice read-only and backend/artifact-authoritative.

## Technical Approach
- Add a small read-only gap registry panel to the existing project-state dashboard flow.
- Prefer reading the registry from the existing server-side/project-state load path rather than client-only filesystem access.
- Phase 1 should show, at minimum:
  - gap id
  - title
  - status
  - suggested follow-up
  - promoted objective slug
  - readiness / impact / urgency when available
- If there are no gaps, the panel should render an explicit empty state.
- Keep duplicate/next views out of phase 1 unless they are trivially available from existing backend surfaces.

## Dependencies
- Depends on the existing gap registry artifact and helper.
- Should align with the current `project-state` dashboard composition.

## Validation Strategy
- Run targeted web/frontend tests for touched files.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer visibility now over interactive controls.
- Prefer embedding in `/project-state` over proliferating routes.
- Prefer simple table/card rendering over a full triage workflow.

## Context Notes
- The backend lifecycle loop for gaps is now materially stronger; the missing layer is operator-facing visibility.
