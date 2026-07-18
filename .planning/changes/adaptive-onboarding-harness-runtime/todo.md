# Todo — adaptive-onboarding-harness-runtime

## Execution Checklist

- [ ] AOH1: Define universal onboarding contracts and classifier
  - [ ] AOH1.1: Write mode/domain classification tests
  - [ ] AOH1.2: Implement contracts and rationale
  - [ ] AOH1.3: Run targeted validation
  - depends_on: domain-security-assurance-plane, harness-stage-execution-runtime
  - validation: `uv run pytest -q tests/unit/test_onboarding_classifier.py`

- [ ] AOH2: Build evidence inventory and current/target state services
  - [ ] AOH2.1: Write evidence and snapshot tests
  - [ ] AOH2.2: Implement versioned state services
  - [ ] AOH2.3: Validate target approval gate
  - depends_on: AOH1
  - validation: `uv run pytest -q tests/unit/test_onboarding_state.py`

- [ ] AOH3: Implement bounded multi-pass Gap Loop
  - [ ] AOH3.1: Write lens, deduplication and convergence tests
  - [ ] AOH3.2: Implement gap runtime
  - [ ] AOH3.3: Validate stop and escalation rules
  - depends_on: AOH2
  - validation: `uv run pytest -q tests/unit/test_onboarding_gaps.py`

- [ ] AOH4: Add Domain Adapter Registry and contracts
  - [ ] AOH4.1: Write adapter conformance tests
  - [ ] AOH4.2: Implement registry and capability checks
  - [ ] AOH4.3: Validate missing adapter behavior
  - depends_on: AOH3
  - validation: `uv run pytest -q tests/unit/test_domain_adapter_registry.py`

- [ ] AOH5: Implement readiness, wave planning and delegation
  - [ ] AOH5.1: Write readiness/veto/wave tests
  - [ ] AOH5.2: Implement wave planner and delegation
  - [ ] AOH5.3: Validate rationale and dependencies
  - depends_on: AOH4
  - validation: `uv run pytest -q tests/unit/test_onboarding_readiness.py tests/unit/test_harness_run_executor.py`

- [ ] AOH6: Implement reassessment, persistence and resumption
  - [ ] AOH6.1: Write delta and checkpoint tests
  - [ ] AOH6.2: Implement reassessment and persistence
  - [ ] AOH6.3: Validate lineage and resume
  - depends_on: AOH5
  - validation: `uv run pytest -q tests/integration/test_onboarding_runtime.py`

- [ ] AOH7: Validate the Software Onboarding Adapter seam
  - [ ] AOH7.1: Create a contract-only software onboarding fixture
  - [ ] AOH7.2: Exercise AI-DLC and MM-flow ownership boundaries
  - [ ] AOH7.3: Validate greenfield/brownfield without implementing the adapter objective
  - depends_on: AOH6
  - validation: `uv run pytest -q tests/integration/test_software_onboarding_adapter.py`

- [ ] AOH8: Validate modes, close docs and handoff
  - [ ] AOH8.1: Run full behavior matrix and regressions
  - [ ] AOH8.2: Reconcile canonical/planning state
  - [ ] AOH8.3: Run discovery contract check
  - depends_on: AOH7
  - validation: `python3 .mm-flow/commands/mm/discover-contract-check.py --objective adaptive-onboarding-harness-runtime`
