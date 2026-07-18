# Todo — software-delivery-domain-adapter

## Execution Checklist

- [ ] SDA1: Define software adapter and AI-DLC profile contracts
  - [ ] SDA1.1: Write profile/ownership/approval tests
  - [ ] SDA1.2: Implement adapter and pinned profile metadata
  - [ ] SDA1.3: Validate conformance
  - depends_on: adaptive-delivery-harness-runtime, harness-stage-execution-runtime, domain-security-assurance-plane
  - validation: `uv run pytest -q tests/unit/test_software_delivery_adapter.py`

- [ ] SDA2: Map software units, concerns and artifacts
  - [ ] SDA2.1: Write UOW/stage/artifact mapping tests
  - [ ] SDA2.2: Implement unit and concern mappers
  - [ ] SDA2.3: Validate prerequisites and depth
  - depends_on: SDA1
  - validation: `uv run pytest -q tests/unit/test_software_unit_mapper.py`

- [ ] SDA3: Implement methodology and capability routing
  - [ ] SDA3.1: Write minimal-route and missing-capability tests
  - [ ] SDA3.2: Register lifecycle/capabilities/routing cases
  - [ ] SDA3.3: Run behavioral routing
  - depends_on: SDA2
  - validation: `uv run pytest -q tests/unit/test_software_methodology_router.py tests/unit/test_multi_harness_selector.py`

- [ ] SDA4: Implement production plans and brownfield safety
  - [ ] SDA4.1: Write plan/path/duplicate tests
  - [ ] SDA4.2: Implement planner and safe-edit integration
  - [ ] SDA4.3: Validate greenfield/brownfield behavior
  - depends_on: SDA3
  - validation: `uv run pytest -q tests/unit/test_software_production_planner.py tests/integration/test_brownfield_software_delivery.py`

- [ ] SDA5: Implement evidence-backed software integration verification
  - [ ] SDA5.1: Write evidence matrix and instruction-only negative tests
  - [ ] SDA5.2: Implement verifier package and evidence capture
  - [ ] SDA5.3: Validate skipped/inconclusive semantics
  - depends_on: SDA4
  - validation: `uv run pytest -q tests/unit/test_software_integration_verifier.py tests/integration/test_software_delivery_evidence.py`

- [ ] SDA6: Integrate security, approvals, AI-DLC state and continuity
  - [ ] SDA6.1: Write strict approval/state/audit/resume tests
  - [ ] SDA6.2: Implement projections and invalidation
  - [ ] SDA6.3: Validate security veto and resume
  - depends_on: SDA5
  - validation: `uv run pytest -q tests/integration/test_aidlc_construction_profile.py tests/integration/test_software_delivery_resume.py`

- [ ] SDA7: Validate end-to-end profile and close the objective
  - [ ] SDA7.1: Run AI-DLC/standalone/regression matrix
  - [ ] SDA7.2: Reconcile canonical/planning status
  - [ ] SDA7.3: Run discovery contract check
  - depends_on: SDA6
  - validation: `python3 .mm-flow/commands/mm/discover-contract-check.py --objective software-delivery-domain-adapter`
