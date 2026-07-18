# Tasks — ui-ux-harness-runtime

## Execution Rules

- Execute tasks in dependency order.
- Use TDD for runtime behavior changes.
- Keep generic runtime changes domain-agnostic.
- Do not mark checks passed without evidence.
- Update `execution-state.json`, `todo.md` and handoff after each task.
- Do not activate this objective while another objective is active without an
  explicit project-level decision.

## UXH1: Add the UI/UX objective profile contract

### Purpose

Model `domain`, `output_type` and `delivery_mode` signals required for
deterministic UI/UX selection while preserving existing profiles.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/mastermind_cli/mm_flow/harness_run_executor.py`
- `apps/api/tests/unit/test_harness_run_executor.py`
- `apps/api/tests/unit/test_multi_harness_models.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_harness_run_executor.py tests/unit/test_multi_harness_models.py`
- `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/models.py mastermind_cli/mm_flow/harness_run_executor.py tests/unit/test_harness_run_executor.py tests/unit/test_multi_harness_models.py`

### Acceptance Criteria

- [ ] UI/UX profiles support the five canonical delivery modes.
- [ ] Classification is pure, deterministic and explains its evidence.
- [ ] Existing software/product classifications remain compatible.
- [ ] Incidental UI words do not activate `domain: ui-ux`.

## UXH2: Register UI/UX harness packages and routing cases

### Purpose

Create Agent Harness-compliant packages and declarative behavioral cases before
runtime execution is added.

### Depends On

UXH1

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/harness-library/roles/ui-ux-delivery/HARNESS.md`
- `.mm-flow/harness-library/verification/ui-ux-verifier/HARNESS.md`
- `.mm-flow/harness-library/registry.yaml`
- `.mm-flow/harness-library/routing-cases.yaml`
- `apps/api/tests/unit/test_multi_harness_selector.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_file_system_harness_catalog.py tests/unit/test_multi_harness_selector.py`
- `cd apps/api && uv run mastermind evaluate-harness-routing --project-root ../..`

### Acceptance Criteria

- [ ] Both harness packages satisfy Agent Harness structure.
- [ ] Positive UI/UX cases select `ui-ux-delivery`.
- [ ] Backend negative cases reject UI/UX capabilities.
- [ ] Supporting verifier selection follows risk/verifiability rules.

## UXH3: Resolve installed skills and conditional capability routes

### Purpose

Resolve the minimum external capabilities by delivery mode with project-first
precedence, metadata validation and source lineage.

### Depends On

UXH2

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/file_system_catalog.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/multi_harness_selector.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/installed_skill_resolver.py`
- `apps/api/tests/unit/test_file_system_harness_catalog.py`
- `apps/api/tests/unit/test_installed_skill_resolver.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_file_system_harness_catalog.py tests/unit/test_multi_harness_selector.py tests/unit/test_installed_skill_resolver.py`
- `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts tests/unit/test_installed_skill_resolver.py`

### Acceptance Criteria

- [ ] Delivery modes select only required skill IDs.
- [ ] Project skills override global candidates deterministically.
- [ ] Resolved skills include source path and content hash.
- [ ] Missing required skills fail with an actionable error.

## Checkpoint A: Selection foundation

- [ ] UXH1–UXH3 tests pass.
- [ ] Behavioral routing passes positive and negative cases.
- [ ] Context budget remains within configured maximum.
- [ ] Human reviews selector behavior before stage execution work.

## UXH4: Integrate UI/UX stages with the shared executor

### Purpose

Materialize UI/UX stage definitions, capabilities and gates for the already
implemented shared stage execution boundary.

### Depends On

UXH3, harness-stage-execution-runtime

### Parallelizable

no

### Files / Areas Likely Touched

- `.mm-flow/harness-library/roles/ui-ux-delivery/HARNESS.md`
- `.mm-flow/harness-library/registry.yaml`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/ui_ux_stages.py`
- `apps/api/tests/unit/test_ui_ux_stages.py`
- `apps/api/tests/integration/test_ui_ux_harness_runtime.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_ui_ux_stages.py tests/integration/test_ui_ux_harness_runtime.py`
- `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/ui_ux_stages.py tests/unit/test_ui_ux_stages.py`

### Acceptance Criteria

- [ ] UI/UX stages materialize through the shared executor contract.
- [ ] Optional stages record `skipped` with a reason.
- [ ] Stage failure stops or routes to recovery according to policy.
- [ ] No generic executor behavior is reimplemented in UI/UX.

## UXH5: Implement UI/UX verification and review gates

### Purpose

Produce structured UI evidence and maker-checker findings instead of accepting
source code inspection as sufficient.

### Depends On

UXH4

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/ui_ux_verification.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `.mm-flow/harness-library/references/ui-ux-verification.md`
- `apps/api/tests/unit/test_ui_ux_verification.py`
- `apps/api/tests/integration/test_ui_ux_harness_runtime.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_ui_ux_verification.py tests/integration/test_ui_ux_harness_runtime.py`
- `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/ui_ux_verification.py tests/unit/test_ui_ux_verification.py`

### Acceptance Criteria

- [ ] Required checks vary correctly by delivery mode.
- [ ] Unperformed checks cannot produce `passed=true`.
- [ ] Browser tooling absence is explicit and policy-driven.
- [ ] Review findings are distinct from deterministic verification.

## UXH6: Persist stage evidence, lineage and recovery state

### Purpose

Make UI/UX runs resumable and auditable through existing project-state and
memory boundaries.

### Depends On

UXH5

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/memory_runtime.py`
- `apps/api/mastermind_cli/project_state/repositories/artifacts.py`
- `apps/api/tests/unit/test_memory_runtime.py`
- `apps/api/tests/api/test_artifact_lineage.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_memory_runtime.py tests/api/test_artifact_lineage.py`
- `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/memory_runtime.py mastermind_cli/project_state/repositories/artifacts.py tests/unit/test_memory_runtime.py`

### Acceptance Criteria

- [ ] Envelope persists stage, verification, review and recovery results.
- [ ] Artifact lineage links spec, prototype, implementation and verdict.
- [ ] Checkpoint contains enough state to resume the next stage.
- [ ] Sensitive browser payloads and secrets are excluded.

## Checkpoint B: Executable pipeline

- [ ] UXH4–UXH6 tests pass.
- [ ] A simulated production UI run reaches persisted `passed` state.
- [ ] A failed verification reaches bounded recovery.
- [ ] A missing capability reaches explicit `blocked` state.

## UXH7: Validate end-to-end routing, execution and regressions

### Purpose

Prove the harness works through the real planning bridge and does not regress
existing harness routes.

### Depends On

UXH6

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/tests/integration/test_ui_ux_harness_runtime.py`
- `apps/api/tests/unit/test_harness_run_executor.py`
- `.mm-flow/harness-library/routing-cases.yaml`
- `apps/api/tests/unit/test_multi_harness_pipeline.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/integration/test_ui_ux_harness_runtime.py tests/unit/test_harness_run_executor.py tests/unit/test_multi_harness_pipeline.py`
- `cd apps/api && uv run mastermind evaluate-harness-routing --project-root ../..`
- `cd apps/api && uv run ruff check mastermind_cli tests/integration/test_ui_ux_harness_runtime.py`

### Acceptance Criteria

- [ ] Planning request produces the expected UI/UX bundle and stage run.
- [ ] Positive, negative, recovery and missing-capability paths pass.
- [ ] Existing product/software routing cases remain green.
- [ ] No build command is required by this objective.

## UXH8: Close documentation, operator guidance and handoff

### Purpose

Align canonical status with actual behavior and leave an auditable continuation
or archive path.

### Depends On

UXH7

### Parallelizable

no

### Files / Areas Likely Touched

- `docs/canonical/110-UI-UX-HARNESS-RUNTIME-CONTRACT.md`
- `.planning/changes/ui-ux-harness-runtime/HANDOFF-CURRENT.md`
- `.planning/changes/ui-ux-harness-runtime/tasks.md`
- `.planning/changes/ui-ux-harness-runtime/todo.md`
- `.planning/changes/ui-ux-harness-runtime/execution-state.json`

### Validation Commands

- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective ui-ux-harness-runtime`
- Review canonical implementation status against test evidence.

### Acceptance Criteria

- [ ] Canonical doc says implemented only after all runtime criteria pass.
- [ ] Handoff identifies exact final state and next action.
- [ ] Planning state matches completed tasks.
- [ ] Archive is allowed only after verification evidence is linked.
