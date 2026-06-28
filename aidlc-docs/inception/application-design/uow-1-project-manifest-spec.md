# UOW-1 Functional Spec — Project Manifest + Source-of-Truth Rules

## Purpose
Define the exact contract that lets the runtime identify the active project and
separate AI-DLC design authority from `.planning` operational intent.

## Problem Statement
The unified harness + memory initiative needs a single, explicit place to answer:

- What project am I in?
- Which files are the source of truth?
- Which layer owns design?
- Which layer owns operational intent?
- What happens when AI-DLC and `.planning` disagree?

Without this contract, the harness can drift between projects or treat the wrong
workflow as authoritative.

## Manifest Format

### File Name
`aidlc-docs/aidlc-state.md`

### Canonical Section
`## Project Manifest`

### Storage Format
Markdown front matter-style key/value fields in a dedicated manifest block.

## Required Fields

| Field | Type | Meaning |
|---|---|---|
| `project_name` | string | Human-readable project name |
| `canonical_scope` | string | Short description of the active initiative |
| `source_of_truth_ai_dlc` | boolean | AI-DLC owns design and slice definitions |
| `source_of_truth_planning` | boolean | `.planning` owns operational intent and handoffs |
| `active_objective` | string | Current initiative or slice name |
| `active_uow` | string | Current implementation unit |
| `project_root` | string | Absolute repo path |
| `operational_layer` | string | Usually `.planning` |
| `design_layer` | string | Usually `aidlc-docs` |
| `memory_layer` | string | Runtime memory location or service name |
| `harness_layer` | string | Harness runtime location or service name |

## Optional Fields

| Field | Type | Meaning |
|---|---|---|
| `adapter_name` | string | Project-specific adapter identifier |
| `bridge_contract` | string | Bridge contract file or module |
| `last_verified_at` | timestamp | Most recent validation time |
| `notes` | string | Freeform context |

## Source-of-Truth Rules

### Rule 1 — AI-DLC owns design
If a question is about:
- architecture
- contracts
- slices
- implementation order
- guardrails

then the answer comes from **AI-DLC artifacts**.

### Rule 2 — `.planning` owns intent
If a question is about:
- what is currently being worked on
- objective/task state
- handoff status
- execution tracking

then the answer comes from **`.planning` artifacts**.

### Rule 3 — Conflict resolution
If AI-DLC and `.planning` disagree:
1. Prefer AI-DLC for design and contract truth.
2. Prefer `.planning` for live execution state.
3. Record the mismatch in the bridge contract.
4. Block execution if the mismatch affects safety or scope.

## Validation Rules

### Must Pass
- `project_name` exists and is non-empty
- `project_root` matches the checked-out repo
- AI-DLC and `.planning` roles are explicit
- `active_objective` exists
- `active_uow` exists or is intentionally unset during kickoff

### Must Fail
- project identity is ambiguous
- design ownership is missing
- operational ownership is missing
- a single layer claims both design and execution without bridge rules

### Warn Only
- optional fields missing
- adapter not yet assigned
- memory layer not yet implemented

## Acceptance Criteria
- The runtime can tell which project is active without guessing.
- The runtime can route design questions to AI-DLC.
- The runtime can route operational questions to `.planning`.
- Conflicts between the layers are explicit and auditable.

## Example Manifest Block

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
- memory_layer: runtime memory service or store
- harness_layer: harness runtime
- adapter_name: mastermind-adapter
- bridge_contract: aidlc-docs/inception/plans/planning-bridge-contract.md
```

## Failure Examples

### Example A — Wrong project
If `project_root` points to another repo, stop and re-detect.

### Example B — Missing design authority
If AI-DLC is absent, do not proceed with architecture work.

### Example C — Missing bridge rules
If `.planning` and AI-DLC conflict and no bridge rule exists, block execution.

## Implementation Notes
- Keep the manifest small and explicit.
- Do not encode runtime logic in prose.
- The manifest should be enough to drive downstream UOWs without re-reading the whole repo.
