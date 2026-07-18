# Tasks — harness-stage-execution-runtime

## Execution Rules

- Execute tasks in dependency order using TDD.
- Keep the executor domain-agnostic.
- Do not accept summaries or instructions as execution evidence.
- Persist planning state after every task.
- Do not run build commands.
- Do not activate this objective while another objective is active without an explicit decision.

## HSR1: Define stage execution contracts

### Purpose

Add typed stage graph, decision, result, evidence, approval, checkpoint and replan
models without breaking existing runtime contracts.

### Depends On

engineering-doctrine-layer, artifact-versioning-and-lineage

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/tests/unit/test_multi_harness_models.py`
- `apps/api/tests/unit/test_stage_execution_models.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_multi_harness_models.py tests/unit/test_stage_execution_models.py`
- `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/models.py tests/unit/test_stage_execution_models.py`

### Acceptance Criteria

- [x] Models represent stage, evidence, approval, checkpoint and replan state.
- [x] StageGraph defines versioned nodes, edges, loops and canonical hash input.
- [x] Existing model construction remains compatible where required.
- [x] Invalid status/policy combinations fail at boundaries.

## HSR2: Extend package and bundle contracts

### Purpose

Add review package support and materialize executable stage metadata in validated
RunBundles.

### Depends On

HSR1

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/file_system_catalog.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/run_bundle_composer.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/run_bundle_validator.py`
- `apps/api/tests/unit/test_file_system_harness_catalog.py`
- `apps/api/tests/unit/test_run_bundle_composer.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_file_system_harness_catalog.py tests/unit/test_run_bundle_composer.py tests/unit/test_run_bundle_validator.py`

### Acceptance Criteria

- [x] Catalog accepts a distinct review package type.
- [x] Bundle contains versioned stage graph and content hash.
- [x] Semantically equivalent unordered manifests produce the same hash.
- [x] Validator rejects missing prerequisites, policies and producers.

## HSR3: Implement deterministic stage scheduling and gates

### Purpose

Resolve dependency-ready stages, invoke selected capabilities and evaluate gates
against typed evidence.

### Depends On

HSR2

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/run_bundle_stage_executor.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/stage_gates.py`
- `apps/api/tests/unit/test_run_bundle_stage_executor.py`
- `apps/api/tests/unit/test_stage_gates.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_run_bundle_stage_executor.py tests/unit/test_stage_gates.py`
- `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/run_bundle_stage_executor.py mastermind_cli/orchestrator/runtime_contracts/stage_gates.py`

### Acceptance Criteria

- [x] Scheduler order is deterministic and prerequisite-safe.
- [x] Only bundle-selected capabilities execute.
- [x] Skips include rationale and unperformed checks cannot pass.

## Checkpoint A: Executable graph foundation

- [ ] HSR1-HSR3 targeted tests pass.
- [ ] Invalid bundles fail before capability invocation.
- [ ] A minimal graph reaches a typed envelope.

## HSR4: Wire RunBundle execution into HarnessRunExecutor

### Purpose

Make the validated bundle govern coordinator execution instead of remaining
detached metadata.

### Depends On

HSR3

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/mm_flow/harness_run_executor.py`
- `apps/api/mastermind_cli/orchestrator/stateless_coordinator.py`
- `apps/api/tests/unit/test_harness_run_executor.py`
- `apps/api/tests/unit/test_stateless_coordinator.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_harness_run_executor.py tests/unit/test_stateless_coordinator.py`

### Acceptance Criteria

- [x] Coordinator receives and follows the validated stage graph.
- [x] Bundle validation failure prevents execution.
- [x] Existing non-stage routes use an explicit compatibility graph.

## HSR5: Add authoritative checkpoint transaction and resume

### Purpose

Atomically persist transitions, evidence refs, checkpoint and outbox using
expected-version concurrency and the canonical idempotency key.

### Depends On

HSR4

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/project_state/repositories/stage_checkpoints.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/memory_runtime.py`
- `apps/api/tests/api/test_stage_checkpoint_repository.py`
- `apps/api/tests/integration/test_stage_execution_resume.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/api/test_stage_checkpoint_repository.py tests/integration/test_stage_execution_resume.py`

### Acceptance Criteria

- [x] Result, evidence refs, checkpoint and outbox commit atomically.
- [x] Expected-version concurrency rejects conflicting transitions.
- [x] Replaying the canonical idempotency key returns the persisted result.
- [x] Resume selects the correct stage/attempt or blocks incompatible hashes.

## HSR6: Implement projection retry and side-effect recovery

### Purpose

Project committed transitions to `.planning` and memory through a retryable
outbox while preventing duplicate or blind retries of external side effects.

### Depends On

HSR5

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/stage_projection_worker.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/capability_invoker.py`
- `apps/api/tests/integration/test_stage_projection_outbox.py`
- `apps/api/tests/unit/test_capability_side_effect_recovery.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/integration/test_stage_projection_outbox.py tests/unit/test_capability_side_effect_recovery.py`

### Acceptance Criteria

- [x] Failed projectors retry from outbox without changing authoritative state.
- [x] Replayed transitions and capabilities suppress duplicate side effects.
- [x] Unknown external outcomes route to `needs_recovery`, never blind retry.

## HSR7: Implement review routing, recovery and safe replanning

### Purpose

Compose independent review and handle bounded failures or workflow changes with
auditable invalidation.

### Depends On

HSR6

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/multi_harness_selector.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/recovery.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/replanning.py`
- `apps/api/tests/unit/test_multi_harness_selector.py`
- `apps/api/tests/unit/test_replanning.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_multi_harness_selector.py tests/unit/test_recovery.py tests/unit/test_replanning.py`

### Acceptance Criteria

- [x] Review selection is distinct from verification selection.
- [x] Recovery respects attempts and budgets.
- [x] Replan records impact and invalidates downstream outputs/approvals.

## HSR8: Validate consumers, regressions and closure

### Purpose

Prove the shared runtime supports representative UI/UX, onboarding and delivery
graphs without embedding their semantics.

### Depends On

HSR7

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/tests/integration/test_stage_execution_consumers.py`
- `apps/api/tests/unit/test_multi_harness_pipeline.py`
- `.mm-flow/harness-library/routing-cases.yaml`
- `docs/canonical/113-HARNESS-STAGE-EXECUTION-RUNTIME-CONTRACT.md`
- `.planning/changes/harness-stage-execution-runtime/`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/integration/test_stage_execution_consumers.py tests/unit/test_multi_harness_pipeline.py tests/unit/test_harness_run_executor.py`
- `cd apps/api && uv run mastermind evaluate-harness-routing --project-root ../..`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective harness-stage-execution-runtime`

### Acceptance Criteria

- [x] Three consumer fixtures use one executor contract.
- [x] Domain imports are absent from the foundation.
- [x] Existing routing and executor tests remain green.
- [x] Canonical implementation status matches evidence.
