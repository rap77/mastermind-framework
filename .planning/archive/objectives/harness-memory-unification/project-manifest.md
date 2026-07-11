# Project Manifest — Unified Harness + Memory

## Project
- **Name:** MasterMind Unified Harness + Memory
- **Canonical Scope:** reusable harness core, memory core, and project adapters
- **Primary Goal:** turn `.planning` into an intention layer executed by a reusable harness

## Manifest Block

```markdown
## Project Manifest
- project_name: MasterMind Unified Harness + Memory
- canonical_scope: reusable harness core, memory core, and project adapters
- source_of_truth_ai_dlc: true
- source_of_truth_planning: true
- active_objective: manifest-contract-bridge-v1
- active_uow: UOW-1
- project_root: /home/rpadron/proy/mastermind
- operational_layer: .planning
- design_layer: aidlc-docs
- memory_layer: first-party memory service/store; Engram bridge only
- harness_layer: apps/api/mastermind_cli and tools/mastermind-cli
- adapter_name: mastermind-adapter
- bridge_contract: .planning/changes/harness-memory-unification/planning-bridge-contract.md
```

## Active References
- **AI-DLC source of truth:** `aidlc-docs/`
- **Operational tracking:** `.planning/`
- **Current roadmap:** `aidlc-docs/inception/plans/harness-memory-roadmap.md`
- **Contracts:** `.planning/changes/harness-memory-unification/harness-contract.md`, `.planning/changes/harness-memory-unification/memory-contract.md`, `.planning/changes/harness-memory-unification/planning-bridge-contract.md`
- **Adapter boundary:** `.planning/changes/harness-memory-unification/adapter-boundary.md`

## Scope Boundaries
### In scope
- harness selection and execution
- verification / review / recovery loops
- memory persistence and retrieval
- project-specific adapters
- contract-driven bridge between AI-DLC and `.planning`

### Out of scope
- deleting historical planning artifacts
- merging both workflows into one folder
- broad refactors unrelated to harness/memory

## Working Model
- **AI-DLC** defines the methodology and slice-level implementation.
- **.planning** stores the active operational intent and handoff trail.
- **Harness** executes loops and enforces contracts.
- **Memory** persists context, checkpoints, and decisions.

## Source-of-Truth Rules
- AI-DLC owns design, slices, and contracts.
- `.planning` owns live operational intent and handoffs.
- If the two disagree, design truth comes from AI-DLC and execution truth comes from `.planning`.
- Any mismatch that affects safety or scope blocks execution until resolved.

## First Slice
### Slice Name
`manifest-contract-bridge-v1`

### Slice Goal
Define the contracts that let the harness read from `.planning` and write back structured outputs without losing project context.

### Deliverables
- project manifest
- harness contract
- memory contract
- `.planning` bridge contract
- adapter boundary definition

## Guardrails
- Detect the active project before acting.
- Keep AI-DLC as the primary design surface.
- Keep `.planning` as the operational surface.
- Prefer additive changes.

## Status
- **State:** defined
- **Next:** formal contract documents
