# Handoff — mm-flow-cli

## Current objective
- `mm-flow-cli`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.

## Blockers / risks
- The package is scaffolded from repository evidence and may need refinement for deeper implementation context.
- Historical legacy material may still exist under archive/legacy, but it is not part of the active workflow.

## Exact next recommended task
- `T2` from `tasks.md` — depends on T1.

## Validation commands
- `/mm:discover-contract-check --objective mm-flow-cli`
- Run targeted tests for touched files before handing off again
