# Handoff — mm-harness-exception-replace-workflow

## Current objective
- `mm-harness-exception-replace-workflow`

## Decisions already made
- New exception creation is scaffold-based.
- Existing exception updates are now render-by-id and print-first.
- Phase 1 replace ergonomics are now defined as a narrow direct-write helper.
- The next real gap is replacing one rendered entry back into the artifact safely.
- The implemented helper is `.mm-flow/commands/mm/replace-active-objective-exception.py`.
- The workflow is now: render by `id` -> edit JSON file -> replace by `id` -> validate.

## Blockers / risks
- The remaining weakness is lack of a preview/dry-run before the write.
- A generic mutation helper would still be too opaque for this phase.

## Exact next recommended task
- Objective is ready to archive.
- Next likely follow-up: add a narrow diff/preview step for replace-by-id writes.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-exception-replace-workflow`
