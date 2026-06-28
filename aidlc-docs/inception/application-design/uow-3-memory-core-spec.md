# UOW-3 Functional Spec — Memory Core

## Purpose
Define the durable memory contract for the unified harness system so the runtime
can preserve checkpoints, decisions, and useful context across sessions.

## Problem Statement
The harness can execute loops correctly only if it can remember:

- what was already decided
- what was already attempted
- where to resume
- what context matters for the next run
- which project the memory belongs to

Without this contract, the system becomes session-bound and loses continuity.

## Core Memory Elements

- `MemoryStore`
- `CheckpointStore`
- `DecisionRecord`
- `ContextSnapshot`
- `RunSummary`
- `RetrievalResult`

## Memory Responsibilities

### Store durable context
Keep decisions, checkpoints, and summaries beyond the current chat session.

### Retrieve relevant history
Return prior context for the active project and objective.

### Support resume
Allow the harness to continue from the latest safe checkpoint.

### Keep scope isolated
Memory from one project must not bleed into another unless explicitly bridged.

## Required Inputs

| Input | Source | Meaning |
|---|---|---|
| `ProjectManifest` | UOW-1 | project identity and scope rules |
| `ExecutionEnvelope` | UOW-2 | the last run result |
| `CheckpointState` | memory layer | resume point |
| `DecisionHistory` | memory layer | prior choices and outcomes |
| `Objective` | `.planning` bridge | current task or slice |

## Required Outputs

| Output | Meaning |
|---|---|
| `ContextSnapshot` | compact memory bundle for the next run |
| `CheckpointState` | resumable state artifact |
| `DecisionRecord` | stored decision or resolution |
| `RetrievalResult` | relevant prior context for the harness |
| `RunSummary` | persistent summary of what happened |

## Memory Rules

### Must be project-scoped
Each memory record must know which project it belongs to.

### Must be resumable
The latest valid checkpoint must be enough to continue safely.

### Must be explicit
Retrieval should be intentional, not accidental or hidden.

### Must be auditable
The runtime should be able to explain why a piece of memory was used.

### Must preserve useful history
Do not discard decisions that still influence future runs.

## Checkpoint Rules

- Write a checkpoint when a run reaches a safe boundary.
- Load the latest checkpoint before starting a continuation run.
- Mark checkpoints with the project and objective that produced them.
- Treat malformed or stale checkpoints as invalid.

## Decision Storage Rules

- Store important design and execution decisions separately from raw logs.
- Keep decisions searchable by project and objective.
- Preserve the reasoning behind the decision.
- Allow later runs to reference the decision as context.

## Retrieval Rules

- Retrieval should return only the context needed for the active run.
- Retrieval must prefer current-project memory.
- Retrieval must not silently mix unrelated projects.
- Retrieval should be bounded and explainable.

## Resume Rules

- Resume from the latest safe checkpoint.
- If the checkpoint is missing or invalid, fall back to a clean run.
- If memory and manifest conflict, manifest rules dominate.
- If the resume point is ambiguous, stop and ask or escalate.

## Acceptance Criteria

- The system can store a checkpoint and later resume from it.
- The system can retrieve prior decisions for the active project.
- The system can keep memory scoped to one project.
- The harness can request a memory snapshot before selecting a loop.
- Memory operations remain compatible with future adapters.

## Failure Cases

### Example A — Missing checkpoint
If no checkpoint exists, start from a clean state instead of guessing.

### Example B — Cross-project leak
If a memory record belongs to another project, do not use it unless bridged.

### Example C — Corrupt state
If stored memory is malformed, mark it invalid and continue safely.

## Implementation Notes

- Keep the memory API small.
- Separate checkpoints from decisions.
- Separate summaries from raw history.
- Prefer deterministic retrieval rules over heuristic mixing.
