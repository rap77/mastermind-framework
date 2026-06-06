---
name: mastermind-harness-evolution
description: >
  Improve the MasterMind harness safely by turning lifecycle gaps into explicit
  contracts, incremental enforcement, and deterministic evals.
  Trigger: When changing .mm-flow commands/agents/skills, evolving the harness
  lifecycle, or closing reliability gaps in the model-agnostic workflow.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

Use this skill when work touches any of these:

- `.mm-flow/commands/mm/*.py`
- `.mm-flow/agents/mm/*`
- `.mm-flow/skills/mm/*`
- `bin/mm`
- harness lifecycle docs, handoffs, or objective-package flow

Especially load it when you need to:

- integrate a new lifecycle gate into the real operating path
- reduce ambiguity between Claude, Codex, and shell flows
- add warnings/blocking without breaking current projects
- make harness state inferable from artifacts, not only terminal output
- define evals for harness behavior before implementation

## Critical Patterns

### 1. Preserve the active harness flow

Treat this as the current lifecycle unless the objective explicitly changes it:

1. `context-to-canonical`
2. `objective-context-check`
3. `discover`
4. `discover-contract-check`
5. `complete-task`
6. `archive-objective`

Do not let docs, handlers, or agent guidance recommend shortcuts that silently skip the gate.

### 2. Source of truth stays in `.mm-flow/commands/mm/*.py`

- Runtime adapters may guide or wrap behavior.
- Core lifecycle rules belong in `.mm-flow/commands/mm/*.py`.
- Avoid pushing critical behavior into runtime-specific UX.

### 3. Warning-first enforcement

For harness-sensitive changes:

- prefer **recommendation/warning** first
- introduce **blocking** only when the condition is deterministic and low-risk
- never hard-block broad flows without a clear artifact or reproducible check

### 4. Make state visible

Another model or operator must be able to answer:

- Has the gate run?
- Did it pass?
- Did it fail?
- Does it need more input?

Prefer one of these, in order:

1. a small persisted artifact
2. a deterministic rule over adjacent artifacts
3. a safe recomputation path

### 5. Design tool/handler outputs for recovery

When changing handlers, outputs should make the next step obvious.
Each important path should expose:

- status (`PASSED`, `FAILED`, `NEEDS_INPUT`, or equivalent)
- one-line summary
- exact next command
- stop condition if the operator should not continue

### 6. Eval before implementation

Before changing harness behavior, define:

- capability eval: what the harness should do after the change
- regression eval: what existing lifecycle behavior must not break
- deterministic grader whenever possible

### 7. Keep changes surgical

- Touch only files needed for the active harness objective.
- Do not redesign canonical formats unless the objective requires it.
- Do not replace an existing command when lifecycle integration is enough.

## Workflow

### Step 1 — Name the gap precisely

Write the gap as an operational failure, not a vague improvement.

Good:
- "discover can still recommend a path that bypasses objective-context-check"
- "another model cannot infer gate status from artifacts"

Bad:
- "make the harness smarter"

### Step 2 — Choose the narrowest enforcement

Use this table:

| Situation | First move |
|---|---|
| Behavior is ambiguous but recoverable | warning + exact next step |
| Status is known `NEEDS_INPUT` | stop progression and request missing input |
| Status is known `FAILED` | block readiness claims and point to remediation |
| Status is inferable deterministically | allow narrow blocking in the relevant path |

### Step 3 — Define evals before coding

Create at least one of each:

- **Capability eval**: proves the new lifecycle behavior exists
- **Regression eval**: proves current objective execution still works

### Step 4 — Implement in the smallest viable surface

Prefer this order of touchpoints:

1. lifecycle messaging / next-step guidance
2. deterministic status inference
3. narrow enforcement in directly relevant entrypoints
4. docs/handoff refresh

### Step 5 — Verify as an operator

Validate from the perspective of another model/operator, not only from unit tests.
Ask: "Could a fresh session know what to do next from the artifacts and command output?"

## Commands

```bash
# Inspect the active harness objective
ls .mm-flow/planning/changes/
sed -n '1,220p' .mm-flow/planning/HANDOFF-CURRENT.md

# Check current lifecycle contract docs
sed -n '1,220p' .mm-flow/README.md
sed -n '1,220p' .mm-flow/commands/mm/objective-context-check.md

# Run deterministic contract checks
python3 .mm-flow/commands/mm/objective-context-check-handler.py --help
python3 .mm-flow/commands/mm/discover-contract-check.py --objective <objective-slug>

# Run focused tests
python3 -m unittest tests.unit.test_mm_discover_workflow
python3 -m unittest tests.unit.test_mm_complete_task_handler
```

## Resources

- **Checklist**: See [assets/lifecycle-improvement-checklist.md](assets/lifecycle-improvement-checklist.md)
- **Local references**: See [references/active-harness-references.md](references/active-harness-references.md)
