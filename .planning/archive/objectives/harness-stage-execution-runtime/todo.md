# Todo — harness-stage-execution-runtime

## Execution Checklist

- [x] HSR1: Define stage execution contracts
  - [x] HSR1.1: Write model and invalid-state tests
  - [x] HSR1.2: Add typed contracts additively
  - [x] HSR1.3: Run targeted model validation
  - depends_on: engineering-doctrine-layer, artifact-versioning-and-lineage
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_multi_harness_models.py tests/unit/test_stage_execution_models.py` | `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/models.py tests/unit/test_stage_execution_models.py`

- [x] HSR2: Extend package and bundle contracts
  - [x] HSR2.1: Write review package and bundle graph tests
  - [x] HSR2.2: Materialize stages and content hash
  - [x] HSR2.3: Validate graph failures and deterministic hash normalization
  - depends_on: HSR1
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_file_system_harness_catalog.py tests/unit/test_run_bundle_composer.py tests/unit/test_run_bundle_validator.py`

- [x] HSR3: Implement deterministic stage scheduling and gates
  - [x] HSR3.1: Write scheduler and evidence-gate tests
  - [x] HSR3.2: Implement executor and gate evaluator
  - [x] HSR3.3: Validate capability isolation
  - depends_on: HSR2
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_run_bundle_stage_executor.py tests/unit/test_stage_gates.py` | `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/run_bundle_stage_executor.py mastermind_cli/orchestrator/runtime_contracts/stage_gates.py`

- [x] HSR4: Wire RunBundle execution into HarnessRunExecutor
  - [x] HSR4.1: Write bundle-governs-execution integration tests
  - [x] HSR4.2: Wire executor and compatibility graph
  - [x] HSR4.3: Validate existing coordinator behavior
  - depends_on: HSR3
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_harness_run_executor.py tests/unit/test_stateless_coordinator.py`

- [x] HSR5: Add authoritative checkpoint transaction and resume
  - [x] HSR5.1: Write expected-version, idempotency and resume tests
  - [x] HSR5.2: Implement atomic checkpoint/outbox transaction
  - [x] HSR5.3: Validate replay and bundle hash handling
  - depends_on: HSR4
  - validation: `cd apps/api && uv run pytest -q tests/api/test_stage_checkpoint_repository.py tests/integration/test_stage_execution_resume.py`

- [x] HSR6: Implement projection retry and side-effect recovery
  - [x] HSR6.1: Write outbox retry and side-effect replay tests
  - [x] HSR6.2: Implement projector and capability idempotency
  - [x] HSR6.3: Validate unknown-outcome recovery
  - depends_on: HSR5
  - validation: `cd apps/api && uv run pytest -q tests/integration/test_stage_projection_outbox.py tests/unit/test_capability_side_effect_recovery.py`

- [x] HSR7: Implement review routing, recovery and safe replanning
  - [x] HSR7.1: Write review/recovery/replan tests
  - [x] HSR7.2: Implement selection and invalidation
  - [x] HSR7.3: Validate bounded behavior
  - depends_on: HSR6
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_multi_harness_selector.py tests/unit/test_recovery.py tests/unit/test_replanning.py`

- [x] HSR8: Validate consumers, regressions and closure
  - [x] HSR8.1: Run three consumer fixtures and routing regressions
  - [x] HSR8.2: Reconcile canonical/planning status
  - [x] HSR8.3: Run discovery contract check
  - depends_on: HSR7
  - validation: `cd apps/api && uv run pytest -q tests/integration/test_stage_execution_consumers.py tests/unit/test_multi_harness_pipeline.py tests/unit/test_harness_run_executor.py` | `cd apps/api && uv run mastermind evaluate-harness-routing --project-root ../..` | `python3 .mm-flow/commands/mm/discover-contract-check.py --objective harness-stage-execution-runtime`
