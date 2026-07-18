# Todo — domain-security-assurance-plane

## Execution Checklist

- [x] SAP1: Define SecurityProfile and overlay contracts
  - [x] SAP1.1: Write profile composition tests
  - [x] SAP1.2: Implement typed contracts and precedence
  - [x] SAP1.3: Run targeted validation
  - depends_on: None
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_security_profile.py` | `cd apps/api && uv run ruff check mastermind_cli/orchestrator/runtime_contracts/models.py tests/unit/test_security_profile.py`

- [x] SAP2: Extend Gap Registry for security findings
  - [x] SAP2.1: Write security gap persistence tests
  - [x] SAP2.2: Implement shared schema extensions
  - [x] SAP2.3: Validate redaction and queries
  - depends_on: SAP1
  - validation: `cd apps/api && uv run pytest -q tests/api/test_security_gap_registry.py`

- [x] SAP3: Implement domain overlay and source resolution
  - [x] SAP3.1: Define minimal domain overlay fixtures
  - [x] SAP3.2: Implement source/jurisdiction resolution
  - [x] SAP3.3: Validate stale-source escalation
  - depends_on: SAP1
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_security_overlays.py`

- [x] SAP4: Implement assurance loop and evidence verifier
  - [x] SAP4.1: Write bounded pass and evidence tests
  - [x] SAP4.2: Implement assurance passes
  - [x] SAP4.3: Validate unperformed-check behavior
  - depends_on: SAP2, SAP3
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_security_assurance.py`

- [x] SAP5: Enforce readiness veto and risk acceptance lifecycle
  - [x] SAP5.1: Write veto and expiry tests
  - [x] SAP5.2: Implement readiness and acceptance rules
  - [x] SAP5.3: Validate reopen on expiry
  - depends_on: SAP4
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_security_readiness.py`

- [x] SAP6: Persist assurance evidence and remediation lineage
  - [x] SAP6.1: Write integration persistence tests
  - [x] SAP6.2: Persist verdicts, decisions and checkpoint
  - [x] SAP6.3: Verify sensitive-data exclusion
  - depends_on: SAP5
  - validation: `cd apps/api && uv run pytest -q tests/integration/test_security_assurance_runtime.py`

- [x] SAP7: Validate domain behavior and close the objective
  - [x] SAP7.1: Run full domain matrix
  - [x] SAP7.2: Run regressions and contract check
  - [x] SAP7.3: Reconcile canonical and planning status
  - depends_on: SAP6
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_security_profile.py tests/unit/test_security_overlays.py tests/unit/test_security_assurance.py tests/unit/test_security_readiness.py tests/integration/test_security_assurance_runtime.py` | `python3 .mm-flow/commands/mm/discover-contract-check.py --objective domain-security-assurance-plane`
