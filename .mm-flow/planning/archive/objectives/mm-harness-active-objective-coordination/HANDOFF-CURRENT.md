# Handoff — mm-harness-active-objective-coordination

## Current objective
- `mm-harness-active-objective-coordination`

## Decisions already made
- Objective discovery and activation now align on **single active objective by
  default**.
- `discover --existing --objective <slug>` blocks if a different active
  objective directory already exists, while allowing refresh of the same slug.
- Filesystem reality now wins over chat/handoff assumptions when determining
  what is active.

## Blockers / risks
- Roadmap ranking still does not demote gate-blocked recommendations; it only
  surfaces gate status and blocks later at activation/discover time.
- Explicit multi-active workflows, if ever needed, still lack a deterministic
  coordination artifact or exception path.

## Exact next recommended task
- Validate/archive this objective package, then decide whether to tackle
  gate-aware roadmap re-ranking or formal multi-active exception metadata next.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-active-objective-coordination`
- `python3 -m unittest tests.unit.test_mm_discover_workflow`
- Run targeted tests for touched files before handing off again
