# Handoff — mm-harness-gap-registry-and-promotion

## Current objective
- `mm-harness-gap-registry-and-promotion`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- The first coherent slice is a **durable gap registry artifact plus a narrow
  helper workflow**, not a fully autonomous gap manager.
- Phase 1 should support explicit gap registration, listing, and promotion
  marking, while leaving automatic prioritization and auto-objective creation
  out of scope.
- The phase-1 slice is now implemented with:
  - `.mm-flow/planning/gaps/gap-registry.json`
  - `.mm-flow/commands/mm/gap-registry.py`
  - subcommands: `register`, `list`, `promote`
- Promotion only updates registry metadata; it does not create objectives
  automatically.

## Blockers / risks
- The next gap is no longer basic persistence; it is whether to add dedupe,
  stronger promotion policy, or roadmap-aware prioritization.
- Phase 1 does not backfill historical archived gaps into the registry.

## Exact next recommended task
- Archive this objective and open a follow-up only when the harness needs
  deduplication, prioritization, or automatic promotion guidance.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-gap-registry-and-promotion`
- `python3 -m unittest tests.unit.test_mm_gap_registry`
- `python3 .mm-flow/commands/mm/gap-registry.py list`
