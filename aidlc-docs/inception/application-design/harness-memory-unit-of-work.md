# Harness + Memory Unit of Work Map

## Purpose
Break the unified harness + memory architecture into implementation-sized slices.

## UOW-1 — Project Manifest + Source-of-Truth Rules

### Goal
Define the active project, scope boundaries, and authoritative workflow split.

### Includes
- `ProjectManifest`
- source-of-truth rules
- project detection rules

### Output
- a stable manifest that tells the runtime which project is active and where
  planning vs execution responsibilities live

## UOW-2 — Harness Core Contracts

### Goal
Implement the core harness execution contract.

### Includes
- `HarnessCore`
- `LoopSelector`
- `ExecutionEnvelope`
- `CapabilityRegistry`

### Output
- deterministic loop selection and canonical run output

## UOW-3 — Memory Core

### Goal
Persist and retrieve project memory and checkpoints.

### Includes
- `MemoryStore`
- `CheckpointStore`
- memory retrieval APIs
- checkpoint write/read APIs

### Output
- resumable context across sessions and tool calls

## UOW-4 — Planning Bridge

### Goal
Translate `.planning` intent into harness input and persist structured results
back into planning artifacts.

### Includes
- `PlanningBridge`
- intent parser
- handoff writer
- structured status writer

### Output
- a reversible bridge between operational planning and harness execution

## UOW-5 — Project Adapter + Integration

### Goal
Adapt the shared harness and memory runtime to the current repo and prepare it
for reuse in other projects.

### Includes
- `ProjectAdapter`
- repo-specific wiring
- integration tests
- validation for end-to-end flow

### Output
- first runnable path from planning intent to harness execution to memory update

## Execution Order
1. UOW-1
2. UOW-2
3. UOW-3
4. UOW-4
5. UOW-5

## Notes
- Keep `.planning` as the intent layer.
- Keep AI-DLC as the design and implementation source of truth.
- Prefer additive evolution over rewrites.
