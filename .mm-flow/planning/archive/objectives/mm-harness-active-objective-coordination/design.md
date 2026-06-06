# Design — mm-harness-active-objective-coordination

## Architecture / Boundaries

This objective does not add a new planning surface. It reconciles behavior
across existing entrypoints:

- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/commands/mm/activate-next-objective-handler.py`
- `.mm-flow/commands/mm/complete-task-handler.py`
- root handoff and active objective package artifacts

## Technical Approach

### 1. Choose one explicit coordination policy

Phase-1 recommendation:

- default to **one active objective package at a time**
- allow exceptions only when the harness can explain them deterministically

This matches current activation behavior and reduces ambiguity for operators and
other models.

### 2. Normalize entrypoint behavior

At minimum, these entrypoints should agree:

- `activate-next-objective`
- `discover --existing --objective <slug>`
- any handoff/current-objective messaging that claims what is active

Candidate first implementation:

- if another active objective directory exists and the requested slug differs:
  - block package creation
  - print the active objective path/slug
  - tell the operator to complete/archive/resume the active objective first
- if the requested slug already exists:
  - treat it as resume/continue guidance, not a silent second active objective

### 3. Preserve low-risk compatibility

Do not delete or rewrite historical objective directories automatically.
Prefer explicit blocking/guidance over mutation.

## Dependencies

- active objective directory detection under `.mm-flow/planning/changes/`
- current handoff generation in `discover-handler.py`
- existing ambiguity handling in task execution

## Validation Strategy

Concrete checks should include:

```bash
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-active-objective-coordination
```

Need tests for at least:

- objective discovery blocked when another active objective exists
- objective discovery allowed when targeting the same active objective
- handoff/current-objective guidance remains coherent

## Important Tradeoffs

- **Strict single-active policy vs flexibility:** strict policy is safer, but may
  constrain advanced workflows
- **Blocking vs warning:** blocking is stronger but may reveal hidden workflows;
  warning is weaker but preserves ambiguity
- **Filesystem truth vs handoff truth:** filesystem state must win when they disagree

## Files / Areas Likely Touched

- `.mm-flow/commands/mm/discover-handler.py`
- `.mm-flow/planning/HANDOFF-CURRENT.md`
- tests for objective discovery / activation coordination
