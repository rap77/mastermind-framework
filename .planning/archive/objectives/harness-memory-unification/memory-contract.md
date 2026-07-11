# Memory Contract — harness-memory-unification

## Purpose
Define how the unified system persists and retrieves useful context so the runtime can resume safely and avoid relearning prior decisions.

## Core Memory Elements
- `MemoryStore`
- `CheckpointStore`
- `DecisionRecord`
- `ContextSnapshot`
- `RunSummary`
- `RetrievalResult`

## Responsibilities
- store checkpoints, decisions, and run summaries
- retrieve relevant prior context
- preserve continuity across sessions and tools
- keep project memory separate from transient chat memory

## Inputs
- run outputs from the harness
- decisions made during execution
- project context and identifiers
- checkpoint data

## Outputs
- recalled context
- relevant prior decisions
- checkpoint state
- retrieval results for the harness and adapters

## Invariants
- memory must be project-scoped
- memory must be resumable
- memory must not depend on volatile chat state
- retrieval must be explicit and auditable
- checkpoints and decisions remain separate artifacts

## Checkpoint Rules
- write a checkpoint at a safe boundary
- load the latest checkpoint before continuation
- mark checkpoints with project and objective
- treat malformed or stale checkpoints as invalid

## Retrieval Rules
- return only context needed for the active run
- prefer current-project memory
- do not silently mix unrelated projects
- keep retrieval bounded and explainable

## Resume Rules
- resume from the latest safe checkpoint
- if checkpoint is missing or invalid, start clean
- if memory and manifest conflict, manifest rules dominate
- if the resume point is ambiguous, stop or escalate

## Success Criteria
- a later session can resume from stored memory
- the harness can fetch prior decisions before selecting a loop
- memory records remain usable across projects through adapters
