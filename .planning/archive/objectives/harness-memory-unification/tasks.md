# Tasks — harness-memory-unification

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Keep the first slice focused on contracts and manifest clarity.

## HM1: Define the project manifest

### Purpose
Make the unified objective and source-of-truth split explicit before any implementation work starts.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- `.planning/changes/harness-memory-unification/project-manifest.md`
- `.planning/changes/harness-memory-unification/HANDOFF-CURRENT.md`
- `.planning/changes/harness-memory-unification/execution-state.json`

### Validation Commands
- Review the manifest against `aidlc-docs/inception/plans/harness-memory-roadmap.md`

### Acceptance Criteria
 - [x] The project manifest exists and names the unified scope.
 - [x] The source-of-truth split is explicit.
 - [x] The first slice is named and bounded.

## HM2: Define harness and memory contracts

### Purpose
Specify the reusable runtime seam before connecting `.planning` to it.

### Depends On
HM1

### Parallelizable
no

### Files / Areas Likely Touched
- `aidlc-docs/inception/plans/harness-contract.md`
- `aidlc-docs/inception/plans/memory-contract.md`
- related canonical docs under `aidlc-docs/inception/application-design/`

### Validation Commands
- Cross-check contract requirements against the roadmap and canonical design docs

### Acceptance Criteria
 - [x] Harness contract boundaries are explicit.
 - [x] Memory contract boundaries are explicit.
 - [x] Ambiguity handling is specified.

## HM3: Define the planning bridge and adapter boundary

### Purpose
Map `.planning` artifacts into typed harness inputs/outputs without deleting history.

### Depends On
HM2

### Parallelizable
no

### Files / Areas Likely Touched
- `aidlc-docs/inception/plans/planning-bridge-contract.md`
- adapter design docs under `aidlc-docs/inception/application-design/`

### Validation Commands
- Review bridge inputs/outputs against the active `.planning` handoff state

### Acceptance Criteria
 - [x] `.planning` inputs and outputs are mapped explicitly.
 - [x] Project adapter responsibilities are separated from core runtime responsibilities.
 - [x] The bridge can be used by another repo without changing the core contracts.

## HM4: Validate the objective package

### Purpose
Confirm the objective package matches the roadmap and canonical contract surfaces.

### Depends On
HM1, HM2, HM3

### Parallelizable
no

### Files / Areas Likely Touched
- `.planning/changes/harness-memory-unification/requirements.md`
- `.planning/changes/harness-memory-unification/design.md`
- `.planning/changes/harness-memory-unification/HANDOFF-CURRENT.md`

### Validation Commands
- Compare the package docs with `aidlc-docs/inception/plans/harness-memory-roadmap.md`
- Compare bridge and contract docs with the canonical planning and architecture docs

### Acceptance Criteria
 - [x] The objective package is internally consistent.
 - [x] The package matches the roadmap’s first execution steps.
 - [x] The package is ready to hand off to execution without further scaffolding.

## HM5: Runtime implementation slice

### Purpose
Turn the harness and memory contracts into the first executable runtime slice.

### Depends On
HM4

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/`
- `apps/api/mastermind_cli/memory_layer/`
- `apps/api/mastermind_cli/mm_flow/`
- `apps/api/tests/unit/`

### Validation Commands
- `uv run pytest tests/unit/test_harness_state_guard.py tests/unit/test_planning_bridge.py -q`
- targeted tests for runtime contract and memory layer changes

### Acceptance Criteria
 - [x] Harness runtime selects a loop deterministically.
 - [x] Execution envelope is canonical and stable.
 - [x] Checkpoint/memory persistence can store and restore prior context safely.
 - [x] The slice is small enough to verify without staging or ops assumptions.
