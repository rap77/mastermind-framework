# Handoff — mm-harness-exception-replace-preview

## Current objective
- `mm-harness-exception-replace-preview`

## Decisions already made
- New exception creation is scaffold-based.
- Existing exception updates are render-by-id and print-first.
- Existing exception replacements are now replace-by-id from an explicit JSON file.
- The next real gap is preview/dry-run visibility before replacement writes.
- Phase 1 preview should be a `--dry-run` mode on the existing replace helper.
- This gap is useful but deferrable; current replace semantics are already explicit and fail-closed.
- The implemented preview now lives on `.mm-flow/commands/mm/replace-active-objective-exception.py --dry-run`.
- The current safe flow is: render -> edit file -> dry-run preview -> replace -> validate.

## Blockers / risks
- The remaining preview is top-level and concise, not a deep semantic diff.
- A generic diff surface would still be too broad for this phase.

## Exact next recommended task
- Objective is ready to archive.
- Next likely follow-up: richer field-level or semantic diff guidance only if operators still feel uncertainty.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-exception-replace-preview`
