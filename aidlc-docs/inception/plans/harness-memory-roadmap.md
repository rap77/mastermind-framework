# Harness + Memory Master Roadmap

## Objective
Build a reusable harness system for MasterMind that can:
- select and run agent loops
- verify, review, and recover deterministically
- persist and retrieve project memory
- drive `.planning` as an input/output layer instead of a manual workflow
- be reused in other repos through adapters

## Scope
In scope:
- harness core
- memory core
- project adapters
- `.planning` bridge
- runtime contracts

Out of scope:
- rewriting all existing planning artifacts at once
- merging AI-DLC and `.planning` into one folder
- deleting historical context

## Current Facts
- AI-DLC already contains the harness/loop architecture work.
- `.planning` currently contains the active operational flow.
- The two systems are related but not identical.
- The right approach is to connect them through a stable contract.

## First Execution Steps
1. Define the project manifest for the unified initiative.
2. Define the harness contract: input, output, loop states, recovery.
3. Define the memory contract: checkpoint, retrieval, update, retention.
4. Map `.planning` artifacts to harness inputs and outputs.
5. Add the adapter layer for project-specific routing.

## Implementation Roadmap

### Slice 1 — Manifest + Contracts
Goal: make the project identity and source-of-truth split executable.

Deliverables:
- canonical `ProjectManifest`
- harness contract
- memory contract
- planning bridge contract

Exit criteria:
- the runtime can identify the active project without guessing
- AI-DLC vs `.planning` ownership is explicit
- downstream slices can consume a stable contract surface

### Slice 2 — Core Runtime + Memory
Goal: make the reusable runtime deterministic and stateful.

Deliverables:
- harness core
- loop selector
- execution envelope
- checkpoint store
- memory retrieval and persistence primitives

Exit criteria:
- the runtime can select a loop deterministically
- runs emit a canonical envelope
- prior context can be loaded and updated safely

### Slice 3 — Planning Bridge + Adapter
Goal: connect `.planning` to the runtime and make the repo the first runnable host.

Deliverables:
- planning bridge implementation
- project adapter
- end-to-end integration tests
- structured write-back to planning artifacts

Exit criteria:
- a planning objective can flow into the harness
- results can be written back structurally
- the unified flow works in this repo before reuse elsewhere

## Guardrails
- Do not mix project scopes.
- Do not assume `.planning` and AI-DLC are the same workflow.
- Always check the active objective before editing.
- Prefer additive migration over replacement.

## Status
Status: Slice 5 project adapter cross-project reuse closed (commit `d5f3561a`)
Next step: extend the reuse boundary into a second repo template and operational maintenance

## Draft Artifacts
- `project-manifest.md`
- `harness-contract.md`
- `memory-contract.md`
- `planning-bridge-contract.md`
- `../application-design/harness-memory-architecture.md`
- `../application-design/harness-memory-unit-of-work.md`
- `uow-1-project-manifest-implementation-plan.md`
- `../application-design/uow-1-project-manifest-spec.md`
- `../application-design/uow-2-harness-core-spec.md`
- `../application-design/uow-3-memory-core-spec.md`
- `../application-design/uow-4-planning-bridge-spec.md`
- `../application-design/uow-5-project-adapter-integration-spec.md`
- `../../construction/plans/UOW-1-project-manifest-code-generation-plan.md`
