"""Materialize Agent Harness-compliant run bundles from composition plans."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml

from .models import HarnessCompositionPlan, RunBundle, SkillPackage


@dataclass(frozen=True, slots=True)
class RunBundleComposer:
    """Create a filesystem RunBundle for a selected harness composition."""

    output_root: Path | str
    library_root: Path | str | None = None

    def compose(self, plan: HarnessCompositionPlan) -> RunBundle:
        """Materialize the plan into a run bundle directory."""
        bundle_id = plan.plan_id
        bundle_path = Path(self.output_root) / bundle_id
        bundle_path.mkdir(parents=True, exist_ok=True)

        self._write_harness_file(plan, bundle_path)
        self._write_leaf_detectors(bundle_path)
        self._write_skills(plan, bundle_path)
        self._write_references(plan, bundle_path)
        self._write_manifest(plan, bundle_path, bundle_id)

        return RunBundle(
            bundle_id=bundle_id,
            objective_id=plan.objective_profile.objective_id,
            plan_id=plan.plan_id,
            path=str(bundle_path),
            harness_file=str(bundle_path / "HARNESS.md"),
            bundle_manifest=str(bundle_path / "bundle.yaml"),
            primary_harness_id=plan.primary_harness.package_id,
            supporting_harness_ids=tuple(
                harness.package_id for harness in plan.supporting_harnesses
            ),
            selected_skill_ids=tuple(skill.skill_id for skill in plan.selected_skills),
            validation_status="pending",
            created_at=self._now_iso(),
        )

    def _write_harness_file(
        self,
        plan: HarnessCompositionPlan,
        bundle_path: Path,
    ) -> None:
        """Write the composed bundle `HARNESS.md` entrypoint."""
        supporting = (
            "\n".join(
                f"- `{harness.package_id}` — {harness.description}"
                for harness in plan.supporting_harnesses
            )
            or "- none"
        )
        precedence = "\n".join(
            f"{idx}. `{item}`" for idx, item in enumerate(plan.precedence_policy, 1)
        )
        skills = (
            "\n".join(
                f"- `{skill.skill_id}` — {skill.description}"
                for skill in plan.selected_skills
            )
            or "- none"
        )
        content = (
            "---\n"
            f"name: {plan.primary_harness.name} RunBundle\n"
            f"description: Compose {plan.primary_harness.name} with selected support for {plan.objective_profile.output_type}.\n"
            "---\n\n"
            f"Primary harness: `{plan.primary_harness.package_id}`\n\n"
            "Supporting harnesses:\n"
            f"{supporting}\n\n"
            "Selected skills:\n"
            f"{skills}\n\n"
            "Precedence:\n"
            f"{precedence}\n\n"
            "- `skills/` — selected skills for this run.\n"
            "- `references/` — selected references for this objective.\n"
            "- `bundle.yaml` — lineage and composition metadata.\n"
        )
        (bundle_path / "HARNESS.md").write_text(content, encoding="utf-8")

    @staticmethod
    def _write_leaf_detectors(bundle_path: Path) -> None:
        """Write the standard Agent Harness leaf detector file."""
        (bundle_path / ".leaf-detectors").write_text(
            "skill=SKILL.md\n",
            encoding="utf-8",
        )

    def _write_skills(self, plan: HarnessCompositionPlan, bundle_path: Path) -> None:
        """Materialize selected skills into the bundle skills directory."""
        skills_dir = bundle_path / "skills"
        skills_dir.mkdir(exist_ok=True)
        self._write_skills_routing(plan, skills_dir)
        for skill in plan.selected_skills:
            self._materialize_skill(skill, skills_dir)

    @staticmethod
    def _write_skills_routing(plan: HarnessCompositionPlan, skills_dir: Path) -> None:
        """Write `skills/SKILLS.md` routing metadata."""
        lines = [
            "---",
            "description: Selected skills for this composed run bundle.",
            "---",
            "",
            "# Selected Skills",
            "",
        ]
        lines.extend(
            f"- `{skill.skill_id}` — {skill.description}"
            for skill in plan.selected_skills
        )
        lines.append("")
        (skills_dir / "SKILLS.md").write_text("\n".join(lines), encoding="utf-8")

    def _materialize_skill(self, skill: SkillPackage, skills_dir: Path) -> None:
        """Copy a selected skill package or write a minimal skill stub."""
        destination = skills_dir / skill.skill_id
        source = self._skill_source(skill)
        if source is not None and source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
            return
        destination.mkdir(exist_ok=True)
        (destination / "SKILL.md").write_text(
            "---\n"
            f"name: {skill.name}\n"
            f"description: {skill.description}\n"
            "---\n\n"
            f"{skill.description}\n",
            encoding="utf-8",
        )

    def _skill_source(self, skill: SkillPackage) -> Path | None:
        """Return the source directory for a skill when a library root is configured."""
        if self.library_root is None:
            return None
        return Path(self.library_root) / skill.path

    @staticmethod
    def _write_references(plan: HarnessCompositionPlan, bundle_path: Path) -> None:
        """Write selected reference routing metadata."""
        references_dir = bundle_path / "references"
        references_dir.mkdir(exist_ok=True)
        lines = [
            "---",
            "description: Selected references for this composed run bundle.",
            "---",
            "",
            "# Selected References",
            "",
        ]
        lines.extend(f"- `{reference}`" for reference in plan.selected_references)
        lines.append("")
        (references_dir / "REFERENCES.md").write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

    def _write_manifest(
        self,
        plan: HarnessCompositionPlan,
        bundle_path: Path,
        bundle_id: str,
    ) -> None:
        """Write `bundle.yaml` lineage and composition metadata."""
        manifest = {
            "bundle_id": bundle_id,
            "objective_id": plan.objective_profile.objective_id,
            "plan_id": plan.plan_id,
            "primary_harness": plan.primary_harness.package_id,
            "supporting_harnesses": [
                harness.package_id for harness in plan.supporting_harnesses
            ],
            "source_harnesses": [
                {
                    "id": harness.package_id,
                    "path": harness.path,
                }
                for harness in (plan.primary_harness, *plan.supporting_harnesses)
            ],
            "selected_skills": [skill.skill_id for skill in plan.selected_skills],
            "selected_references": list(plan.selected_references),
            "selected_loops": list(plan.selected_loops),
            "precedence": list(plan.precedence_policy),
            "context_budget": plan.context_budget,
            "validation_requirements": list(plan.validation_requirements),
            "created_at": self._now_iso(),
        }
        (bundle_path / "bundle.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
        )

    @staticmethod
    def _now_iso() -> str:
        """Return the current UTC timestamp for bundle lineage."""
        return datetime.now(UTC).isoformat()
