"""Structural validation for materialized Agent Harness run bundles."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

from .models import RunBundle


class RunBundleValidator:
    """Validate a RunBundle before execution."""

    def validate(self, bundle: RunBundle) -> RunBundle:
        """Return the bundle with validation status and errors populated."""
        errors: list[str] = []
        bundle_path = Path(bundle.path)
        manifest = self._validate_required_files(bundle, bundle_path, errors)
        if manifest is not None:
            self._validate_manifest(bundle, manifest, errors)
        self._validate_selected_skills(bundle, bundle_path, errors)
        return replace(
            bundle,
            validation_status="failed" if errors else "passed",
            validation_errors=tuple(errors),
        )

    def _validate_required_files(
        self,
        bundle: RunBundle,
        bundle_path: Path,
        errors: list[str],
    ) -> dict[str, Any] | None:
        """Validate required bundle files and return manifest data when available."""
        harness_path = Path(bundle.harness_file)
        leaf_path = bundle_path / ".leaf-detectors"
        manifest_path = Path(bundle.bundle_manifest)
        skills_routing = bundle_path / "skills" / "SKILLS.md"
        references_routing = bundle_path / "references" / "REFERENCES.md"

        if not harness_path.is_file():
            errors.append("missing HARNESS.md")
        elif not harness_path.read_text(encoding="utf-8").startswith("---\n"):
            errors.append("HARNESS.md missing YAML frontmatter")

        if not leaf_path.is_file():
            errors.append("missing .leaf-detectors")
        elif "skill=SKILL.md" not in leaf_path.read_text(encoding="utf-8").splitlines():
            errors.append(".leaf-detectors missing skill=SKILL.md")

        if not skills_routing.is_file():
            errors.append("missing skills/SKILLS.md")
        if not references_routing.is_file():
            errors.append("missing references/REFERENCES.md")
        if not manifest_path.is_file():
            errors.append("missing bundle.yaml")
            return None
        return self._read_manifest(manifest_path, errors)

    @staticmethod
    def _read_manifest(
        manifest_path: Path,
        errors: list[str],
    ) -> dict[str, Any] | None:
        """Read bundle manifest YAML, collecting validation errors."""
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            errors.append("bundle.yaml must be a mapping")
            return None
        return raw

    @staticmethod
    def _validate_manifest(
        bundle: RunBundle,
        manifest: dict[str, Any],
        errors: list[str],
    ) -> None:
        """Validate manifest lineage matches the RunBundle contract."""
        if manifest.get("bundle_id") != bundle.bundle_id:
            errors.append("bundle.yaml bundle_id mismatch")
        if manifest.get("objective_id") != bundle.objective_id:
            errors.append("bundle.yaml objective_id mismatch")
        if manifest.get("plan_id") != bundle.plan_id:
            errors.append("bundle.yaml plan_id mismatch")
        if manifest.get("primary_harness") != bundle.primary_harness_id:
            errors.append("bundle.yaml primary_harness mismatch")
        manifest_skills = manifest.get("selected_skills", [])
        if (
            isinstance(manifest_skills, list)
            and tuple(manifest_skills) != bundle.selected_skill_ids
        ):
            errors.append("bundle.yaml selected_skills mismatch")

    @staticmethod
    def _validate_selected_skills(
        bundle: RunBundle,
        bundle_path: Path,
        errors: list[str],
    ) -> None:
        """Validate every selected skill has a leaf `SKILL.md`."""
        for skill_id in bundle.selected_skill_ids:
            skill_path = bundle_path / "skills" / skill_id / "SKILL.md"
            if not skill_path.is_file():
                errors.append(f"missing selected skill leaf: {skill_id}/SKILL.md")
            elif not skill_path.read_text(encoding="utf-8").startswith("---\n"):
                errors.append(f"selected skill missing YAML frontmatter: {skill_id}")
