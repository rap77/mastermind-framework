# Tasks — domain-security-assurance-plane

## Execution Rules

- Use TDD for behavior.
- Keep policy, profile, verification and approval boundaries separate.
- Never persist secrets or raw sensitive payloads.
- Update planning state after each task.

## SAP1: Define SecurityProfile and overlay contracts

### Purpose

Create typed models and deterministic composition precedence.

### Depends On

None

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/models.py`
- `apps/api/mastermind_cli/project_state/schemas/overview.py`
- `apps/api/tests/unit/test_security_profile.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_security_profile.py`
- `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/models.py tests/unit/test_security_profile.py`

### Acceptance Criteria

- [x] Profile composition is deterministic and versioned.
- [x] Domain, jurisdiction and project overlays are represented.
- [x] Weaker overrides require explicit exception metadata.

## SAP2: Extend Gap Registry for security findings

### Purpose

Represent threats, controls, residual risk and treatment in the shared gap model.

### Depends On

SAP1

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/project_state/models/`
- `apps/api/mastermind_cli/project_state/repositories/`
- `apps/api/tests/api/test_security_gap_registry.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/api/test_security_gap_registry.py`

### Acceptance Criteria

- [x] Security findings use the universal Gap Registry.
- [x] Evidence and control references are queryable.
- [x] Sensitive values are rejected or redacted.

## SAP3: Implement domain overlay and source resolution

### Purpose

Resolve software, marketing and finance overlays with source/jurisdiction metadata.

### Depends On

SAP1

### Parallelizable

yes, after SAP1 and coordinated with SAP2 schema

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/security_overlays.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/capability_registry.py`
- `apps/api/tests/unit/test_security_overlays.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_security_overlays.py`

### Acceptance Criteria

- [x] Domains resolve distinct control sets.
- [x] Source version and jurisdiction are retained.
- [x] Missing or stale sources escalate explicitly.

## SAP4: Implement assurance loop and evidence verifier

### Purpose

Run asset, boundary, threat, control, evidence and residual-risk passes.

### Depends On

SAP2, SAP3

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/security_assurance.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/verification.py`
- `apps/api/tests/unit/test_security_assurance.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_security_assurance.py`

### Acceptance Criteria

- [x] Passes use distinct rubrics and bounded iterations.
- [x] Unperformed checks cannot pass.
- [x] Evidence verdicts include limitations and source version.

## SAP5: Enforce readiness veto and risk acceptance lifecycle

### Purpose

Block unsafe readiness and manage approved, expiring exceptions.

### Depends On

SAP4

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/orchestrator/runtime_contracts/security_readiness.py`
- `apps/api/mastermind_cli/project_state/services/project_overview.py`
- `apps/api/tests/unit/test_security_readiness.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_security_readiness.py`

### Acceptance Criteria

- [x] Critical/high findings apply policy-driven veto.
- [x] Acceptance requires owner, approval, scope and expiry.
- [x] Expired acceptance reopens the finding.

## SAP6: Persist assurance evidence and remediation lineage

### Purpose

Make profiles, findings, verdicts and decisions auditable and resumable.

### Depends On

SAP5

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/mastermind_cli/project_state/repositories/artifacts.py`
- `apps/api/mastermind_cli/orchestrator/runtime_contracts/memory_runtime.py`
- `apps/api/tests/integration/test_security_assurance_runtime.py`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/integration/test_security_assurance_runtime.py`

### Acceptance Criteria

- [x] Security history and lineage are persisted.
- [x] Checkpoint supports resumption.
- [x] Secrets and sensitive payloads are absent.

## SAP7: Validate domain behavior and close the objective

### Purpose

Prove domain differences, veto behavior, regressions and documentation status.

### Depends On

SAP6

### Parallelizable

no

### Files / Areas Likely Touched

- `apps/api/tests/integration/test_security_assurance_runtime.py`
- `docs/canonical/112-DOMAIN-AWARE-SECURITY-ASSURANCE-PLANE.md`
- `.planning/changes/domain-security-assurance-plane/`

### Validation Commands

- `cd apps/api && uv run pytest -q tests/unit/test_security_profile.py tests/unit/test_security_overlays.py tests/unit/test_security_assurance.py tests/unit/test_security_readiness.py tests/integration/test_security_assurance_runtime.py`
- `python3 .mm-flow/commands/mm/discover-contract-check.py --objective domain-security-assurance-plane`

### Acceptance Criteria

- [x] Software, marketing and finance cases behave differently where required.
- [x] Existing harness regressions remain green.
- [x] Canonical implementation status matches evidence.
