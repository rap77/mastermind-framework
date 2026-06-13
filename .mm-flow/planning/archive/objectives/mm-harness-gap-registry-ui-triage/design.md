# Design — mm-harness-gap-registry-ui-triage

## Architecture / Boundaries
- Reuse the existing `/project-state` dashboard panel for gap visibility.
- Reuse the existing Python helper as the source of truth for `duplicates` and `next` rather than reimplementing triage rules in the browser.

## Technical Approach
- Extend the server-side project-state API helper to invoke:
  - `gap-registry.py duplicates`
  - `gap-registry.py next`
- Render the returned read-only triage signals in the existing gap registry card:
  - highlighted next recommended gap
  - compact duplicate suspects list
- Keep the slice fail-soft:
  - if helper execution fails, the main dashboard still loads
  - empty states remain explicit

## Dependencies
- Depends on the existing gap registry helper and the base gap registry UI panel.

## Validation Strategy
- Run targeted frontend tests for the touched dashboard slice.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer helper reuse over duplicating triage logic in TypeScript.
- Prefer compact triage signals over a larger workflow surface.
- Prefer read-only visibility now over inline resolution controls.

## Context Notes
- The base gap registry panel already renders entries; the missing operational value was surfacing triage signals (`duplicates`, `next`) from the existing helper.
