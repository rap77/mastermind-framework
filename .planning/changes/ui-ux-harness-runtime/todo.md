# Todo — ui-ux-harness-runtime

## Execution Checklist

- [ ] UXH1: Add the UI/UX objective profile contract
  - [ ] UXH1.1: Write failing profile and classification tests
  - [ ] UXH1.2: Implement delivery mode and UI/UX classification
  - [ ] UXH1.3: Run targeted validation
  - depends_on: none
  - validation: `uv run pytest -q tests/unit/test_harness_run_executor.py tests/unit/test_multi_harness_models.py`

- [ ] UXH2: Register UI/UX harness packages and routing cases
  - [ ] UXH2.1: Create Agent Harness package files
  - [ ] UXH2.2: Add registry entries and routing cases
  - [ ] UXH2.3: Run catalog and routing validation
  - depends_on: UXH1
  - validation: `uv run pytest -q tests/unit/test_file_system_harness_catalog.py tests/unit/test_multi_harness_selector.py`

- [ ] UXH3: Resolve installed skills and conditional capability routes
  - [ ] UXH3.1: Write resolver and conditional routing tests
  - [ ] UXH3.2: Implement resolver, precedence and content hash
  - [ ] UXH3.3: Validate missing-capability behavior
  - depends_on: UXH2
  - validation: `uv run pytest -q tests/unit/test_installed_skill_resolver.py tests/unit/test_multi_harness_selector.py`

- [ ] UXH4: Integrate UI/UX stages with the shared executor
  - [ ] UXH4.1: Write UI/UX stage materialization tests
  - [ ] UXH4.2: Register UI/UX stages and gates
  - [ ] UXH4.3: Validate skips and shared recovery routing
  - depends_on: UXH3, harness-stage-execution-runtime
  - validation: `uv run pytest -q tests/unit/test_ui_ux_stages.py tests/integration/test_ui_ux_harness_runtime.py`

- [ ] UXH5: Implement UI/UX verification and review gates
  - [ ] UXH5.1: Write delivery-mode verification tests
  - [ ] UXH5.2: Implement evidence and review boundaries
  - [ ] UXH5.3: Validate unavailable-tooling behavior
  - depends_on: UXH4
  - validation: `uv run pytest -q tests/unit/test_ui_ux_verification.py tests/integration/test_ui_ux_harness_runtime.py`

- [ ] UXH6: Persist stage evidence, lineage and recovery state
  - [ ] UXH6.1: Write persistence and lineage tests
  - [ ] UXH6.2: Persist stage/check/recovery records
  - [ ] UXH6.3: Validate checkpoint resumption and secret exclusion
  - depends_on: UXH5
  - validation: `uv run pytest -q tests/unit/test_memory_runtime.py tests/api/test_artifact_lineage.py`

- [ ] UXH7: Validate end-to-end routing, execution and regressions
  - [ ] UXH7.1: Add end-to-end happy and failure paths
  - [ ] UXH7.2: Run behavioral routing evaluation
  - [ ] UXH7.3: Run existing harness regressions
  - depends_on: UXH6
  - validation: `uv run pytest -q tests/integration/test_ui_ux_harness_runtime.py tests/unit/test_harness_run_executor.py tests/unit/test_multi_harness_pipeline.py`

- [ ] UXH8: Close documentation, operator guidance and handoff
  - [ ] UXH8.1: Reconcile canonical status with evidence
  - [ ] UXH8.2: Update planning state and handoff
  - [ ] UXH8.3: Run discovery contract validation
  - depends_on: UXH7
  - validation: `python3 .mm-flow/commands/mm/discover-contract-check.py --objective ui-ux-harness-runtime`
