# Loops

## Purpose

Loops are the reusable execution patterns used by the harness to solve different kinds of objectives with the smallest safe composition of roles.

## Core Loops

### `clarify`
- Use when the objective is ambiguous or underspecified.
- Output: a focused clarification question.
- Roles: classifier, optionally chairman.

### `deliberate`
- Use for decisions that need multiple perspectives.
- Output: recommendation plus confidence.
- Roles: domain role, contrarian, chairman.

### `build`
- Use for implementation work with clear scope.
- Output: concrete next actions and verification steps.
- Roles: executor, relevant domain role, verifier.

### `red_team`
- Use when risk is high or failure would be expensive.
- Output: failure modes, blind spots, and mitigation.
- Roles: domain role, red-team, verifier, chairman.

### `recover`
- Use when a previous run failed or needs continuation.
- Output: checkpoint recovery and next safe action.
- Roles: memory-steward, chairman, domain role if needed.

## Selection Principles

- Choose the smallest loop that can safely finish the job.
- Add roles only for missing capability or risk coverage.
- Prefer deterministic selection for the same objective and context.
- Do not run deliberation loops for simple deterministic tasks.

## Role Overlays

Some roles are better modeled as overlays than permanent brains:
- `contrarian`
- `first_principles`
- `outsider`
- `executor`

These overlays can be attached to an existing brain or loop without creating a new persistent brain.
