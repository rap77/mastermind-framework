# UOW-2 Functional Spec — Harness Core Contracts

## Purpose
Define the execution contract for the reusable harness core so the system can
select, run, verify, review, and recover from work without ad hoc decisions.

## Problem Statement
The unified system needs a deterministic runtime that can answer:

- What loop should run for this objective?
- What capabilities are required?
- What output format is expected?
- When do we verify, review, or recover?
- How do we keep the same behavior across projects?

Without this contract, the system becomes a set of loose scripts and cannot be
reused safely.

## Core Runtime Elements

- `HarnessCore`
- `LoopSelector`
- `ExecutionEnvelope`
- `CapabilityRegistry`
- `VerificationHarness`
- `ReviewHarness`
- `RecoveryHarness`

## Execution Model

### Step 1 — Select
The runtime reads the project manifest and current planning intent, then asks
`LoopSelector` to choose the smallest useful loop set.

### Step 2 — Resolve capabilities
The runtime asks `CapabilityRegistry` for the minimum capabilities required to
run the selected loop safely.

### Step 3 — Execute
`HarnessCore` runs the objective through the selected loop path and produces an
`ExecutionEnvelope`.

### Step 4 — Verify
`VerificationHarness` checks the result against acceptance criteria when the
task is testable.

### Step 5 — Review
`ReviewHarness` performs a fresh-context or maker-checker review when risk or
complexity requires it.

### Step 6 — Recover
`RecoveryHarness` decides retry, patch, replan, or escalate when verification or
review fails.

## Required Inputs

| Input | Source | Meaning |
|---|---|---|
| `ProjectManifest` | UOW-1 | active project and source-of-truth rules |
| `Objective` | `.planning` bridge | current task or slice |
| `Constraints` | manifest + planning | safety, scope, budget, time |
| `Capabilities` | registry | available harnesses and helpers |
| `MemorySnapshot` | memory layer | prior decisions and checkpoints |

## Required Outputs

| Output | Meaning |
|---|---|
| `selected_loop` | loop path chosen for execution |
| `selected_capabilities` | minimum runtime helpers required |
| `execution_envelope` | canonical typed output of the run |
| `verification_result` | pass/fail and evidence |
| `review_result` | approval/findings when review is required |
| `recovery_decision` | retry/patch/replan/escalate when needed |

## Loop Selection Rules

### Must use minimal control
Choose the smallest loop set that can safely complete the objective.

### Must be deterministic
The same manifest + objective + constraints should produce the same loop choice.

### Must be explainable
The selection result must include the reason for the chosen loop.

### Must fail loudly on ambiguity
If the objective cannot be classified safely, do not guess.

## Envelope Contract

### Required Fields
- `status`
- `summary`
- `artifacts`
- `risks`
- `next_actions`
- `verification`
- `recovery`

### Invariants
- The envelope is the canonical handoff output.
- The envelope is not freeform prose.
- The envelope must be readable by the bridge and memory layer.

## Verification Rules

- Run verification when the task has acceptance criteria.
- Verification must be deterministic.
- Verification result must cite what passed or failed.
- Verification does not replace review when review is required.

## Review Rules

- Run review when complexity or risk exceeds the no-review threshold.
- Review uses fresh context when possible.
- Review must produce actionable findings, not vague approval.
- Review can block continuation if findings are material.

## Recovery Rules

- Retry only when the failure is local and bounded.
- Patch only when the fix is small and safe.
- Replan when the failure is structural.
- Escalate when ambiguity or risk exceeds safe autonomy.

## Acceptance Criteria
- The harness can choose a loop without manual interpretation.
- The harness can emit a canonical envelope.
- Verification and review are separate decisions.
- Recovery is bounded and explainable.
- The same contract can be reused across projects through adapters.

## Failure Cases

### Example A — Ambiguous objective
If the objective cannot be classified, the harness must pause or escalate.

### Example B — Missing capabilities
If required capabilities are absent, the harness must not silently substitute.

### Example C — Verification failure
If checks fail, recovery must produce a bounded next step.

## Implementation Notes
- Keep loop selection pure and easy to test.
- Keep the envelope schema stable.
- Avoid hardcoding repo-specific behavior in the core.
- The bridge and adapter layers should carry project differences, not the core.
