# Todo — adaptive-delivery-harness-runtime

## Execution Checklist

- [x] ADH1: Define delivery readiness and unit contracts
  - [x] ADH1.1: Write request/unit/route/verdict tests
  - [x] ADH1.2: Add additive typed models
  - [x] ADH1.3: Validate invalid boundaries
  - depends_on: harness-stage-execution-runtime, domain-security-assurance-plane
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_delivery_models.py tests/unit/test_multi_harness_models.py`

- [x] ADH2: Implement deterministic decomposition and readiness
  - [x] ADH2.1: Write readiness/dependency/ownership tests
  - [x] ADH2.2: Implement services
  - [x] ADH2.3: Validate blocker paths
  - depends_on: ADH1
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_delivery_readiness.py tests/unit/test_delivery_units.py`

- [x] ADH3: Add Domain Delivery Adapter Registry
  - [x] ADH3.1: Write conformance and resolution tests
  - [x] ADH3.2: Implement adapter protocol and registry
  - [x] ADH3.3: Validate missing capability behavior
  - depends_on: ADH2
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_domain_delivery_adapter.py`

- [x] ADH4: Implement adaptive route planning
  - [x] ADH4.1: Write stage decision/depth/prerequisite tests
  - [x] ADH4.2: Implement planner and bundle projection
  - [x] ADH4.3: Validate route determinism
  - depends_on: ADH3
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_delivery_route_planner.py tests/unit/test_run_bundle_composer.py`

- [x] ADH5: Implement plan-before-production and unit loop
  - [x] ADH5.1: Write production plan and scheduling tests
  - [x] ADH5.2: Register harness and implement orchestration
  - [x] ADH5.3: Validate atomic checkpoints
  - depends_on: ADH4
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_unit_delivery_orchestrator.py tests/unit/test_run_bundle_stage_executor.py` | `cd apps/api && uv run mastermind evaluate-harness-routing --project-root ../..`

- [x] ADH6: Implement integration acceptance and assurance composition
  - [x] ADH6.1: Write verdict/security/review tests
  - [x] ADH6.2: Implement acceptance composition
  - [x] ADH6.3: Validate independent blockers
  - depends_on: ADH5
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_integration_acceptance.py tests/integration/test_adaptive_delivery_assurance.py`

- [x] ADH7: Add recovery, replanning, persistence and resume
  - [x] ADH7.1: Write recovery/replan/resume tests
  - [x] ADH7.2: Implement persistence and invalidation
  - [x] ADH7.3: Validate exact continuation
  - depends_on: ADH6
  - validation: `cd apps/api && uv run pytest -q tests/integration/test_adaptive_delivery_resume.py tests/unit/test_replanning.py`

- [x] ADH8: Validate cross-domain behavior and close the objective
  - [x] ADH8.1: Run cross-domain and routing matrix
  - [x] ADH8.2: Reconcile canonical/planning state
  - [x] ADH8.3: Run discovery contract check
  - depends_on: ADH7
  - validation: `cd apps/api && uv run pytest -q tests/integration/test_adaptive_delivery_runtime.py tests/integration/test_adaptive_delivery_assurance.py tests/integration/test_adaptive_delivery_resume.py` | `cd apps/api && uv run mastermind evaluate-harness-routing --project-root ../..` | `python3 .mm-flow/commands/mm/discover-contract-check.py --objective adaptive-delivery-harness-runtime`
