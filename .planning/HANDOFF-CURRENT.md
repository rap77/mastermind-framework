# Handoff — artifact-versioning-and-lineage

## Current objective
- `artifact-versioning-and-lineage`

## Decisions already made
- Use a per-objective planning package instead of relying on a single global spec forever.
- Another model should be able to resume from artifacts, not from chat memory alone.

## Blockers / risks
- The package is scaffolded from repository evidence and may need refinement for deeper implementation context.
- Legacy/global MM discovery artifacts still coexist during the transition to the hybrid flow.

## Exact next recommended task
- Start with `T1` from `tasks.md`.

## Validation commands
- `/mm:discover-contract-check` (legacy/global validator still active)
- Run targeted tests for touched files before handing off again
