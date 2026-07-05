"""Behavioral routing case evaluator for multi-harness selection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import yaml

from .file_system_catalog import FileSystemHarnessCatalog
from .models import Complexity, ObjectiveProfile, RiskLevel, SignalLevel
from .multi_harness_selector import MultiHarnessSelector


@dataclass(frozen=True, slots=True)
class BehavioralRoutingCaseResult:
    """Result for a single behavioral routing case."""

    case_id: str
    passed: bool
    errors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class BehavioralRoutingReport:
    """Aggregate report for versioned behavioral routing cases."""

    schema_version: str
    passed: bool
    case_results: tuple[BehavioralRoutingCaseResult, ...]


@dataclass(frozen=True, slots=True)
class BehavioralRoutingEvaluator:
    """Evaluate YAML routing cases against the deterministic selector."""

    catalog: FileSystemHarnessCatalog
    context_budget: int = 4_000

    def evaluate_file(self, path: Path | str) -> BehavioralRoutingReport:
        """Evaluate routing cases from a YAML file."""
        payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            raise ValueError("routing cases file must contain a mapping")
        cases = payload.get("routing_cases", [])
        if not isinstance(cases, list):
            raise ValueError("routing_cases must be a list")
        return self.evaluate_cases(
            tuple(self._require_mapping(item) for item in cases),
            schema_version=str(payload.get("schema_version") or "1"),
        )

    def evaluate_cases(
        self,
        cases: tuple[dict[str, Any], ...],
        schema_version: str = "1",
    ) -> BehavioralRoutingReport:
        """Evaluate routing case mappings."""
        selector = MultiHarnessSelector(
            self.catalog,
            context_budget=self.context_budget,
        )
        results = tuple(self._evaluate_case(selector, case) for case in cases)
        return BehavioralRoutingReport(
            schema_version=schema_version,
            passed=all(result.passed for result in results),
            case_results=results,
        )

    def _evaluate_case(
        self,
        selector: MultiHarnessSelector,
        case: dict[str, Any],
    ) -> BehavioralRoutingCaseResult:
        """Evaluate one routing case."""
        case_id = self._require_str(case, "case_id")
        profile = self._build_profile(case)
        plan = selector.select(profile)
        errors: list[str] = []

        expected_primary = self._require_str(case, "expected_primary_harness")
        if plan.primary_harness.package_id != expected_primary:
            errors.append(
                f"primary expected {expected_primary} got {plan.primary_harness.package_id}"
            )

        expected_supporting = self._str_tuple(
            case.get("expected_supporting_harnesses", ())
        )
        actual_supporting = tuple(item.package_id for item in plan.supporting_harnesses)
        if actual_supporting != expected_supporting:
            errors.append(
                "supporting expected "
                f"{list(expected_supporting)} got {list(actual_supporting)}"
            )

        expected_skills = self._str_tuple(case.get("expected_skills", ()))
        actual_skills = tuple(item.skill_id for item in plan.selected_skills)
        if actual_skills != expected_skills:
            errors.append(
                f"skills expected {list(expected_skills)} got {list(actual_skills)}"
            )

        forbidden_skills = set(self._str_tuple(case.get("forbidden_skills", ())))
        forbidden_selected = tuple(
            skill for skill in actual_skills if skill in forbidden_skills
        )
        if forbidden_selected:
            errors.append(f"forbidden skills selected {list(forbidden_selected)}")

        expected_references = self._str_tuple(case.get("expected_references", ()))
        missing_references = tuple(
            ref for ref in expected_references if ref not in plan.selected_references
        )
        if missing_references:
            errors.append(f"missing expected references {list(missing_references)}")

        max_budget = case.get("max_context_budget")
        if isinstance(max_budget, int) and plan.context_budget > max_budget:
            errors.append(
                f"context_budget {plan.context_budget} exceeds max {max_budget}"
            )

        return BehavioralRoutingCaseResult(
            case_id=case_id,
            passed=not errors,
            errors=tuple(errors),
        )

    def _build_profile(self, case: dict[str, Any]) -> ObjectiveProfile:
        """Build an objective profile from a routing case."""
        profile = self._require_mapping(case.get("objective_profile"))
        prompt = self._require_str(case, "prompt")
        return ObjectiveProfile(
            objective_id=self._require_str(profile, "objective_id"),
            objective_text=str(profile.get("objective_text") or prompt),
            domain=self._require_str(profile, "domain"),
            phase=self._require_str(profile, "phase"),
            output_type=self._require_str(profile, "output_type"),
            complexity=cast(Complexity, self._require_str(profile, "complexity")),
            risk_level=cast(RiskLevel, self._require_str(profile, "risk_level")),
            verifiability=cast(
                SignalLevel, self._require_str(profile, "verifiability")
            ),
            requires_write=self._require_bool(profile, "requires_write"),
            requires_fresh_context=self._require_bool(
                profile, "requires_fresh_context"
            ),
            requires_memory=self._require_bool(profile, "requires_memory"),
            requires_mcp=self._require_bool(profile, "requires_mcp"),
            requires_review=self._require_bool(profile, "requires_review"),
            requires_recovery=self._require_bool(profile, "requires_recovery"),
        )

    @staticmethod
    def _require_mapping(value: object) -> dict[str, Any]:
        """Return value as mapping or fail."""
        if not isinstance(value, dict):
            raise ValueError("routing case entry must be a mapping")
        return value

    @staticmethod
    def _require_str(data: dict[str, Any], key: str) -> str:
        """Return a required string field."""
        value = data.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"routing case missing required string field: {key}")
        return value

    @staticmethod
    def _require_bool(data: dict[str, Any], key: str) -> bool:
        """Return a required boolean field."""
        value = data.get(key)
        if not isinstance(value, bool):
            raise ValueError(f"routing case missing required boolean field: {key}")
        return value

    @staticmethod
    def _str_tuple(value: object) -> tuple[str, ...]:
        """Normalize optional list/string case field to tuple."""
        if value is None:
            return ()
        if isinstance(value, str):
            return (value,)
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return tuple(value)
        if isinstance(value, tuple) and all(isinstance(item, str) for item in value):
            return value
        raise ValueError("routing case field must be a string or list of strings")
