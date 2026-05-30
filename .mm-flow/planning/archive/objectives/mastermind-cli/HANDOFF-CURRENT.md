# Handoff — mastermind-cli

## Current objective
- `mastermind-cli`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- CLI router implemented: `mastermind` shell script routes to 9 Python handlers based on subcommand.

## What's implemented
- `mastermind` shell script with subcommand routing to:
  - init, discover, complete-task, archive-objective, activate-next-objective
  - extract-objectives, new-canonical, validate, safe-commit
- Handlers live in `.mm-flow/commands/mm/` (authoritative location)
- Slash commands live in `.mm-flow/commands/mm/*.md` (symlinked from `.claude/commands/mm/`)
- Both entry points (CLI and slash) produce identical results

## Blockers / risks
- Pre-existing test failures in ship_handler and integration tests (not caused by this change)
- Historical legacy material may still exist under archive/legacy, but it is not part of the active workflow.

## Exact next recommended task
- Objective package has no pending root tasks.

## Validation commands
- `./mastermind validate --objective mastermind-cli` → PASSED
- Run targeted tests for touched files before handing off again
