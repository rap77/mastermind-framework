# Tasks — adaptive-delivery-harness-runtime

## Execution Rules

- Execute after shared stage execution and security assurance are complete.
- Use TDD and keep core domain-agnostic.
- Use one primary Role Harness only.
- Persist progress after every task.
- Do not run build commands.

## ADH1: Define delivery readiness and unit contracts

### Purpose

Model requests, readiness, DeliveryUnits, dependencies, routes and integration
verdicts as additive runtime contracts.

### Depends On

harness-stage-execution-runtime, domain-security-assurance-plane

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/delivery_models.py`
- `apps/api/tests/unit/test_delivery_models.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_delivery_models.py tests/unit/test_multi_harness_models.py`

### Acceptance Criteria

- [x] Contracts represent readiness, units, routes and verdicts.
- [x] Unit dependencies and artifact ownership are explicit.
- [x] Invalid or ambiguous requests fail at the boundary.

## ADH2: Implement deterministic decomposition and readiness

### Purpose

Create traceable units from approved scope and block production when criteria,
permissions or dependencies are insufficient.

### Depends On

ADH1

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/delivery_readiness.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/delivery_units.py`
- `apps/api/tests/unit/test_delivery_readiness.py`
- `apps/api/tests/unit/test_delivery_units.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_delivery_readiness.py tests/unit/test_delivery_units.py`

### Acceptance Criteria

- [x] Every in-scope requirement maps to a unit and acceptance path.
- [x] Dependency cycles and ownership conflicts are rejected.
- [x] Missing permissions or criteria produce blocked/escalated state.

## ADH3: Add Domain Delivery Adapter Registry

### Purpose

Resolve versioned domain adapters and enforce their capability, artifact, policy
and verification contracts.

### Depends On

ADH2

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/domain_delivery_adapter.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/domain_adapter_registry.py`
- `apps/api/tests/unit/test_domain_delivery_adapter.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_domain_delivery_adapter.py`

### Acceptance Criteria

- [x] Adapter selection is deterministic and explains rationale.
- [x] Missing capabilities fail loudly.
- [x] Domain extensions do not mutate core contracts ad hoc.

## ADH4: Implement adaptive route planning

### Purpose

Decide concern stages and depth per unit while preserving prerequisites and
artifact contracts.

### Depends On

ADH3

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/delivery_route_planner.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/run_bundle_composer.py`
- `apps/api/tests/unit/test_delivery_route_planner.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_delivery_route_planner.py tests/unit/test_run_bundle_composer.py`

### Acceptance Criteria

- [x] Each stage records execute/skip/block and rationale.
- [x] Depth changes detail, not required artifacts.
- [x] Invalid prerequisite combinations are rejected.

## Checkpoint A: Delivery route foundation

- [ ] ADH1-ADH4 tests pass.
- [ ] Software and non-software fixtures produce valid routes.
- [ ] Human reviews core/adapter boundary.

## ADH5: Implement plan-before-production and unit loop

### Purpose

Execute dependency-ready units through versioned plans, production, verification
and checkpoints using the shared stage executor.

### Depends On

ADH4

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/unit_delivery_orchestrator.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/production_plans.py`
- `.mm-flow/harness-library/roles/adaptive-delivery-lead/HARNESS.md`
- `.mm-flow/harness-library/registry.yaml`
- `apps/api/tests/unit/test_unit_delivery_orchestrator.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_unit_delivery_orchestrator.py tests/unit/test_run_bundle_stage_executor.py`
- `cd apps/api && uv run mastermind evaluate-harness-routing --project-root ../..`

### Acceptance Criteria

- [x] Mutating units require a versioned production plan.
- [x] Units execute dependency-ready and end-to-end.
- [x] Step/stage progress and checkpoints update atomically.

## ADH6: Implement integration acceptance and assurance composition

### Purpose

Evaluate the complete objective using unit evidence, contracts, quality,
security, review and approvals without averaging blockers.

### Depends On

ADH5

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/integration_acceptance.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/security_assurance.py`
- `apps/api/tests/unit/test_integration_acceptance.py`
- `apps/api/tests/integration/test_adaptive_delivery_assurance.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_integration_acceptance.py tests/integration/test_adaptive_delivery_assurance.py`

### Acceptance Criteria

- [x] Verdict covers requirements, units, contracts and evidence.
- [x] Security/review blockers remain independent.
- [x] Conditional acceptance requires owner, conditions and expiry.

## ADH7: Add recovery, replanning, persistence and resume

### Purpose

Handle bounded failures and route changes while preserving lineage and exact
continuation state.

### Depends On

ADH6

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/delivery_recovery.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/memory_runtime.py`
- `apps/api/mastermind_cli/project_state/repositories/artifacts.py`
- `apps/api/tests/integration/test_adaptive_delivery_resume.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/integration/test_adaptive_delivery_resume.py tests/unit/test_replanning.py`

### Acceptance Criteria

- [x] Recovery respects attempts and budgets.
- [x] Replan invalidates downstream artifacts/evidence/approvals.
- [x] Resume selects exact unit, stage and step.

## ADH8: Validate cross-domain behavior and close the objective

### Purpose

Prove the universal contract, routing regressions, persistence and documentation
before enabling production adapters.

### Depends On

ADH7

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/tests/integration/test_adaptive_delivery_runtime.py`
- `.mm-flow/harness-library/routing-cases.yaml`
- `docs/canonical/114-ADAPTIVE-DELIVERY-HARNESS-RUNTIME-CONTRACT.md`
- `.planning/changes/adaptive-delivery-harness-runtime/`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/integration/test_adaptive_delivery_runtime.py tests/integration/test_adaptive_delivery_assurance.py tests/integration/test_adaptive_delivery_resume.py`
- `cd apps/api && uv run mastermind evaluate-harness-routing --project-root ../..`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective adaptive-delivery-harness-runtime`

### Acceptance Criteria

- [x] Two domain fixtures satisfy the same core contract.
- [x] Positive, blocked, recovery and replan paths pass.
- [x] Existing harness routes remain green.
- [x] Canonical implementation status matches evidence.
