# Handoff — mm-harness-runtime-entrypoint-and-adapters

## Current objective
- `mm-harness-runtime-entrypoint-and-adapters`

## Decisions already made
- The existing MM flow is preserved; this objective adds a neutral entrypoint rather than replacing the lifecycle.
- `.mm-flow/commands/mm/*.py` remains the source of truth for flow logic.
- Claude is treated as an adapter, not the canonical runtime interface.
- The safest first harness milestone is to introduce a neutral CLI before deeper context-intake improvements.
- The next major harness improvement after this objective is a new validation gate between `context-to-canonical` and `discover`, tentatively named `objective-context-check`.

## Blockers / risks
- Projects linked by symlink receive framework changes immediately, so adapter/dispatch changes should roll out between tasks, not mid-subtask.
- Claude and Codex differ in slash-command UX, so the entrypoint contract must be validated via shell/core execution, not assumed from one runtime.

## Exact next recommended task
- `T2` from `tasks.md` — depends on T1.

## Validation commands
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-runtime-entrypoint-and-adapters`
- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- `python3 -m unittest tests.unit.test_mm_complete_task_handler_regressions`
