"""Deterministic local verification harness for runtime contracts."""

from __future__ import annotations

from mastermind_cli.orchestrator.runtime_contracts.envelope import (
    validate_execution_envelope,
)
from mastermind_cli.orchestrator.runtime_contracts.models import (
    ExecutionEnvelope,
    TaskProfile,
    VerificationCheck,
    VerificationOutcome,
)


class VerificationHarness:
    """Run deterministic verification checks over the base envelope."""

    def verify(
        self,
        base_envelope: ExecutionEnvelope,
        task_profile: TaskProfile,
    ) -> VerificationOutcome:
        """Return the aggregated verification outcome."""
        valid, errors = validate_execution_envelope(base_envelope)
        checks = (
            VerificationCheck(
                check_id="artifacts-present",
                label="artifacts_present",
                passed=bool(base_envelope.artifacts),
                reason="artifacts present"
                if base_envelope.artifacts
                else "no artifacts generated",
            ),
            VerificationCheck(
                check_id="envelope-valid",
                label="envelope_valid",
                passed=valid,
                reason="valid envelope" if valid else "; ".join(errors),
            ),
            VerificationCheck(
                check_id="acceptance-shape",
                label="acceptance_shape",
                passed=base_envelope.verification is not None,
                reason="verification payload present"
                if base_envelope.verification is not None
                else "verification payload missing",
            ),
        )
        passed = all(check.passed for check in checks)
        return VerificationOutcome(
            performed=True,
            passed=passed,
            checks=checks,
            acceptance_criteria_satisfied=passed,
            evidence_refs=(task_profile.task_id,),
        )
