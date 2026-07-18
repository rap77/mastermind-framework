# Tasks — adaptive-onboarding-harness-runtime

## Execution Rules

- Execute after `domain-security-assurance-plane` and
  `harness-stage-execution-runtime` are complete.
- Use TDD and keep core domain-agnostic.
- Delegate domain execution; do not embed it in the supervisor.
- Persist progress after every task.

## AOH1: Define universal onboarding contracts and classifier

### Purpose

Model onboarding modes, domains, evidence and current/target state.

### Depends On

domain-security-assurance-plane, harness-stage-execution-runtime

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/onboarding_classifier.py`
- `apps/api/tests/unit/test_onboarding_classifier.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_onboarding_classifier.py`

### Acceptance Criteria

- [ ] Seven onboarding modes are represented.
- [ ] Classifier prefers explicit evidence and emits rationale.
- [ ] Incidental terms do not select a domain adapter.

## AOH2: Build evidence inventory and current/target state services

### Purpose

Create versioned baselines and completion definitions from project evidence.

### Depends On

AOH1

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/onboarding_state.py`
- `apps/api/mastermind_cli/project_state/repositories/artifacts.py`
- `apps/api/tests/unit/test_onboarding_state.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_onboarding_state.py`

### Acceptance Criteria

- [ ] Evidence carries source, confidence and version.
- [ ] Current and target snapshots are independently versioned.
- [ ] Missing target approval blocks completion planning.

## AOH3: Implement bounded multi-pass Gap Loop

### Purpose

Detect, deduplicate and prioritize gaps using distinct lenses and stop rules.

### Depends On

AOH2

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/onboarding_gaps.py`
- `apps/api/mastermind_cli/project_state/repositories/`
- `apps/api/tests/unit/test_onboarding_gaps.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_onboarding_gaps.py`

### Acceptance Criteria

- [ ] Each pass uses a distinct rubric.
- [ ] Duplicate findings merge without losing evidence.
- [ ] Loop stops on convergence, budget or escalation.

## AOH4: Add Domain Adapter Registry and contracts

### Purpose

Allow domains to extend evidence, readiness, security and artifact projection.

### Depends On

AOH3

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/domain_adapter_registry.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/tests/unit/test_domain_adapter_registry.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_domain_adapter_registry.py`

### Acceptance Criteria

- [ ] Adapters satisfy a stable typed contract.
- [ ] Missing capabilities fail loudly.
- [ ] Domain extensions do not mutate core models ad hoc.

## AOH5: Implement readiness, wave planning and delegation

### Purpose

Convert dependency-ready gaps into delegated RunBundles and readiness changes.

### Depends On

AOH4

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/onboarding_readiness.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/execution_wave_planner.py`
- `apps/api/mastermind_cli/mm_flow/harness_run_executor.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/run_bundle_stage_executor.py`
- `apps/api/tests/unit/test_onboarding_readiness.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_onboarding_readiness.py tests/unit/test_harness_run_executor.py`

### Acceptance Criteria

- [ ] Blockers and security veto control readiness.
- [ ] Waves contain dependency-ready gaps only.
- [ ] Delegation records selected harness and rationale.
- [ ] Delegated RunBundles execute through the shared stage executor.
- [ ] Mutating production waves target `adaptive-delivery-lead` plus a domain delivery adapter.
- [ ] Read-only verification/review waves can bypass production safely.

## AOH6: Implement reassessment, persistence and resumption

### Purpose

Apply execution results as deltas and preserve auditable continuation state.

### Depends On

AOH5

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/onboarding_reassessment.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/memory_runtime.py`
- `apps/api/tests/integration/test_onboarding_runtime.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/integration/test_onboarding_runtime.py`

### Acceptance Criteria

- [ ] Reassessment updates by delta and preserves lineage.
- [ ] Checkpoint resumes the active wave/iteration.
- [ ] Core-promotion candidates remain distinct from local learnings.

## AOH7: Validate the Software Onboarding Adapter seam

### Purpose

Prove the universal adapter contract and AI-DLC/MM-flow ownership with a fixture
without implementing the separate production adapter objective.

### Depends On

AOH6

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/tests/fixtures/software_onboarding_adapter.py`
- `apps/api/tests/integration/test_software_onboarding_adapter.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/integration/test_software_onboarding_adapter.py`
- `cd apps/api && uv run mastermind evaluate-harness-routing --project-root ../..`

### Acceptance Criteria

- [ ] Greenfield route produces validated intent then objective package.
- [ ] Brownfield route reconciles repository evidence before planning.
- [ ] AI-DLC and MM-flow artifact ownership remains distinct.
- [ ] No production adapter package is implemented by this objective.

## AOH8: Validate modes, close docs and handoff

### Purpose

Prove convergence, delegation, security integration and regression safety.

### Depends On

AOH7

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/tests/integration/test_onboarding_runtime.py`
- `docs/canonical/111-ADAPTIVE-ONBOARDING-HARNESS-RUNTIME-CONTRACT.md`
- `.planning/changes/adaptive-onboarding-harness-runtime/`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_onboarding_classifier.py tests/unit/test_onboarding_state.py tests/unit/test_onboarding_gaps.py tests/unit/test_domain_adapter_registry.py tests/unit/test_onboarding_readiness.py tests/integration/test_onboarding_runtime.py tests/integration/test_software_onboarding_adapter.py`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective adaptive-onboarding-harness-runtime`

### Acceptance Criteria

- [ ] Greenfield, brownfield, completion and audit cases pass.
- [ ] Security blocked and missing-adapter cases pass.
- [ ] Existing harness routing remains green.
- [ ] Canonical status matches implementation evidence.
