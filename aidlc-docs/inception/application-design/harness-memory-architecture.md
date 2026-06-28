# Harness + Memory Architecture

## Summary
The unified initiative uses a three-layer split:

1. **Planning layer** — `.planning` expresses intent, task state, and handoffs.
2. **Harness layer** — executes loops, verifies results, and performs recovery.
3. **Memory layer** — stores checkpoints, decisions, and reusable context.

This keeps the runtime reusable while preserving operational history.

## Core Components

- `ProjectManifest`
- `HarnessCore`
- `LoopSelector`
- `VerificationHarness`
- `ReviewHarness`
- `RecoveryHarness`
- `MemoryStore`
- `CheckpointStore`
- `PlanningBridge`
- `ProjectAdapter`
- `CapabilityRegistry`
- `ExecutionEnvelope`

## Responsibilities

### ProjectManifest
Defines the active project, scope boundaries, and source-of-truth rules.

### HarnessCore
Coordinates loop execution and orchestrates verification/review/recovery.

### LoopSelector
Chooses the minimal loop set required for the current objective.

### VerificationHarness
Checks whether the output satisfies acceptance criteria.

### ReviewHarness
Applies fresh-context or maker-checker review when needed.

### RecoveryHarness
Chooses retry, patch, replan, or escalation when a run fails.

### MemoryStore
Persists durable project memory and structured decisions.

### CheckpointStore
Captures resumable state for long-running or interrupted work.

### PlanningBridge
Translates `.planning` intent into harness input and writes structured results back.

### ProjectAdapter
Adapts the shared runtime to one specific repo or project.

### CapabilityRegistry
Exposes available harnesses, loops, and project capabilities.

### ExecutionEnvelope
Canonical output contract for each run.

## Runtime Flow

1. Read `ProjectManifest`.
2. Read the current `.planning` objective or handoff.
3. Load relevant memory and checkpoint state.
4. Use `LoopSelector` to choose the execution path.
5. Execute work through `HarnessCore`.
6. Verify and review as required.
7. Recover or escalate on failure.
8. Persist the outcome to memory.
9. Write structured results back to `.planning`.

## Invariants

- Planning is not the executor.
- Memory is not volatile chat state.
- Harness decisions are deterministic for the same context.
- The adapter layer isolates project-specific differences.
- Historical handoffs are preserved, not overwritten.

## Intended Outcome

The same runtime can support:
- the current MasterMind repo
- future repos using the same harness
- continued development without losing context
- evolution of `.planning` into a harness-driven flow
