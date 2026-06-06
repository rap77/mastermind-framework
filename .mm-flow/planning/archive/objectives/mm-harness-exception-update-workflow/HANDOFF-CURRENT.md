# Handoff — mm-harness-exception-update-workflow

## Current objective
- `mm-harness-exception-update-workflow`

## Decisions already made
- Runtime semantics, named refs, machine expiry, and authoring validation are implemented and archived.
- The next real gap is safer update ergonomics for existing exception entries.
- Phase 1 update ergonomics are now **print-first**, not mutate-first.
- The implemented helper is `.mm-flow/commands/mm/render-active-objective-exception.py`.
- The workflow is now: render by `id` → paste/replace manually → validate explicitly.

## Blockers / risks
- Direct in-place replacement is still intentionally out of scope.
- The remaining manual step is replacing the rendered entry back into the artifact safely.

## Exact next recommended task
- Objective is ready to archive.
- Next likely follow-up: define a narrow replace-by-id workflow that preserves auditability.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-exception-update-workflow`
