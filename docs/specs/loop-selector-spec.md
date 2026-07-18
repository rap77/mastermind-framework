# Loop Selector Spec

## Status

Draft

## Purpose

Define how the harness selects the minimal safe loop and the participating roles for a given objective.

## Scope

In scope:
- objective classification
- risk and ambiguity assessment
- role composition
- loop selection
- selection explanation

Out of scope:
- domain-specific output generation
- UI behavior
- memory storage internals

## Inputs

- objective text
- project context
- current checkpoint or memory snapshot
- available roles and brains
- risk policy thresholds

## Outputs

- selected loop name
- selected roles/cerebros
- selection reason
- clarification request, if needed

## Selection Rules

1. Choose the smallest loop that can safely complete the objective.
2. Prefer deterministic selection for the same context.
3. Add roles only for required capability or risk coverage.
4. If ambiguity is high, return `clarify` instead of guessing.
5. If risk is high, include `red-team` and `verifier`.
6. If the task is implementation-only, avoid deliberation roles.

## Candidate Loops

- `clarify`
- `deliberate`
- `build`
- `red_team`
- `recover`

## Decision Tree

1. If the objective is underspecified or conflicting, select `clarify`.
2. Else if the objective is primarily about choosing among options, select `deliberate`.
3. Else if the objective is primarily implementation work with clear scope, select `build`.
4. Else if the objective has high risk, security, or failure impact, select `red_team`.
5. Else if the objective is resuming from a failed or interrupted run, select `recover`.

### Role Composition by Loop

#### `clarify`
- `classifier`
- optional `chairman`

#### `deliberate`
- domain brain for the objective
- `contrarian`
- `chairman`

#### `build`
- relevant domain brain
- `executor`
- `verifier`
- optional `chairman`

#### `red_team`
- relevant domain brain
- `red-team`
- `verifier`
- `chairman`

#### `recover`
- `memory-steward`
- relevant domain brain if needed
- `chairman`

### Brain Mapping Examples

- Product objective -> `brain-01-product-strategy`
- UX objective -> `brain-02-ux-research`
- UI objective -> `brain-03-ui-design`
- Frontend objective -> `brain-04-frontend`
- Backend objective -> `brain-05-backend`
- QA or reliability objective -> `brain-06-qa-devops`
- Growth or evaluation objective -> `brain-07-growth-data`

## Acceptance Criteria

- The same input context produces the same selected loop.
- Ambiguous inputs do not silently enter a random loop.
- The selector can explain why the loop was chosen.
- The output maps cleanly to the loop-envelope contract.

## Open Questions

- Should ambiguity be scored by rules only, or by a dedicated classifier brain?
- Should `chairman` be implicit in some loops or always explicit?
- Which roles are overlays only, and which should become persistent brains?
