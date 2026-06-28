# UOW-5 Functional Spec — Project Adapter + Integration

## Purpose
Define how the shared harness + memory runtime is adapted to the current repo
and prepared for reuse in other projects.

## Problem Statement
The harness and memory contracts are only useful if they can be wired into a
real project without custom, one-off glue everywhere. The adapter layer must
connect project-specific state to the shared runtime while preserving the same
contracts across projects.

## Adapter Responsibilities

- identify the active project
- load the project manifest
- connect planning intent to the bridge
- connect memory to the runtime
- provide project-specific wiring without changing core contracts
- validate the end-to-end flow

## Required Inputs

| Input | Source | Meaning |
|---|---|---|
| `ProjectManifest` | UOW-1 | active project identity and scope |
| `HarnessRequest` | UOW-4 | normalized execution request |
| `MemorySnapshot` | UOW-3 | resumable context |
| `ExecutionEnvelope` | UOW-2 | runtime output contract |
| `ProjectConfig` | repo-specific | adapter settings and local paths |

## Required Outputs

| Output | Meaning |
|---|---|
| `IntegratedRun` | end-to-end execution result |
| `AdapterWarnings` | project-specific mismatch or setup issues |
| `ValidationReport` | confirmation that the integration path works |
| `ReusableAdapterBoundary` | documented reusable interface for future repos |

## Integration Rules

### Keep core contracts untouched
The adapter must not alter the harness, memory, or bridge contracts.

### Localize project differences
Repo-specific paths, commands, and conventions belong in the adapter.

### Validate end-to-end
The adapter must prove the flow from planning intent to harness execution to
memory update.

### Preserve reuse
The same adapter pattern must work for future projects with different planning
content or runtime locations.

## Integration Flow

1. Read the project manifest.
2. Load the current `.planning` objective through the bridge.
3. Load memory and checkpoint context.
4. Build the harness request.
5. Execute the harness core.
6. Store execution results in memory.
7. Write structured output back to `.planning`.
8. Emit a validation report for the run.

## Acceptance Criteria

- The current repo can run through the unified flow without custom ad hoc logic.
- The adapter can be swapped or copied for another project.
- Core contracts remain stable while project-specific wiring changes.
- The end-to-end integration path is documented and verifiable.

## Failure Cases

### Example A — Project mismatch
If the adapter loads a manifest for the wrong repo, stop before execution.

### Example B — Bridge failure
If the planning bridge cannot produce a harness request, block the run.

### Example C — Memory failure
If memory cannot provide a valid snapshot, fall back only if the manifest allows
it and the run remains safe.

## Implementation Notes

- Keep the adapter thin and explicit.
- Do not encode project policy in the core harness.
- Prefer small, reusable integration points.
- The adapter is the only place where project-specific wiring should live.
