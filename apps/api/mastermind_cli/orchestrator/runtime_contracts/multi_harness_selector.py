"""Deterministic selector for multi-harness composition plans."""

from __future__ import annotations

from dataclasses import dataclass

from .file_system_catalog import FileSystemHarnessCatalog
from .models import (
    HarnessCompositionPlan,
    HarnessPackage,
    ObjectiveProfile,
    SkillPackage,
)


_DEFAULT_PRECEDENCE = (
    "project_policy",
    "primary_harness",
    "supporting_harnesses",
    "selected_skills",
    "selected_references",
)


@dataclass(frozen=True, slots=True)
class MultiHarnessSelector:
    """Select one primary harness and minimal supporting packages."""

    catalog: FileSystemHarnessCatalog
    context_budget: int = 4_000

    def select(self, profile: ObjectiveProfile) -> HarnessCompositionPlan:
        """Return a deterministic composition plan for the objective profile."""
        harnesses = self.catalog.list_harnesses()
        skills = self.catalog.list_skills()
        primary = self._select_primary(profile, harnesses)
        supporting = self._select_supporting(profile, harnesses, primary)
        selected_skills = self._select_skills(primary, supporting, skills)
        selected_loops = self._selected_loops(primary, supporting)
        rejected = tuple(
            harness.package_id
            for harness in harnesses
            if harness.package_id
            not in {primary.package_id, *(item.package_id for item in supporting)}
        )
        return HarnessCompositionPlan(
            plan_id=f"plan-{profile.objective_id}",
            objective_profile=profile,
            primary_harness=primary,
            supporting_harnesses=supporting,
            selected_skills=selected_skills,
            selected_references=self._selected_references(primary, supporting),
            selected_loops=selected_loops,
            precedence_policy=_DEFAULT_PRECEDENCE,
            context_budget=self.context_budget,
            validation_requirements=("structural", "behavioral"),
            rejected_candidates=rejected,
            rationale=(
                f"domain={profile.domain}",
                f"phase={profile.phase}",
                f"output_type={profile.output_type}",
                f"requires_review={profile.requires_review}",
                f"requires_recovery={profile.requires_recovery}",
            ),
        )

    def _select_primary(
        self,
        profile: ObjectiveProfile,
        harnesses: tuple[HarnessPackage, ...],
    ) -> HarnessPackage:
        """Choose the best role harness for this objective."""
        candidates = [
            harness
            for harness in harnesses
            if harness.package_type == "role" and self._score(profile, harness) > 0
        ]
        if not candidates:
            raise ValueError("No primary harness matches objective profile")
        return sorted(
            candidates,
            key=lambda harness: (-self._score(profile, harness), harness.package_id),
        )[0]

    def _select_supporting(
        self,
        profile: ObjectiveProfile,
        harnesses: tuple[HarnessPackage, ...],
        primary: HarnessPackage,
    ) -> tuple[HarnessPackage, ...]:
        """Choose supporting harnesses that add required verification/recovery."""
        selected: list[HarnessPackage] = []
        for harness in harnesses:
            if harness.package_id == primary.package_id:
                continue
            if harness.package_type == "recovery" and profile.requires_recovery:
                selected.append(harness)
            elif self._score(profile, harness) == 0:
                continue
            elif harness.package_type == "verification" and (
                profile.requires_review or profile.verifiability == "high"
            ):
                selected.append(harness)
            elif (
                harness.package_type == "lifecycle" and profile.phase in harness.phases
            ):
                selected.append(harness)
        return tuple(selected)

    @staticmethod
    def _select_skills(
        primary: HarnessPackage,
        supporting: tuple[HarnessPackage, ...],
        skills: tuple[SkillPackage, ...],
    ) -> tuple[SkillPackage, ...]:
        """Resolve selected skill IDs from primary/supporting harness declarations."""
        selected_ids = list(primary.skills)
        for harness in supporting:
            selected_ids.extend(
                skill for skill in harness.skills if skill not in selected_ids
            )
        skill_by_id = {skill.skill_id: skill for skill in skills}
        return tuple(
            skill_by_id[skill_id]
            for skill_id in selected_ids
            if skill_id in skill_by_id
        )

    @staticmethod
    def _selected_references(
        primary: HarnessPackage,
        supporting: tuple[HarnessPackage, ...],
    ) -> tuple[str, ...]:
        """Return references declared by selected harness packages."""
        references = list(primary.references)
        for harness in supporting:
            references.extend(
                ref for ref in harness.references if ref not in references
            )
        return tuple(references)

    @staticmethod
    def _selected_loops(
        primary: HarnessPackage,
        supporting: tuple[HarnessPackage, ...],
    ) -> tuple[str, ...]:
        """Return loop list preserving primary-first order without duplicates."""
        loops = list(primary.supported_loops)
        for harness in supporting:
            loops.extend(loop for loop in harness.supported_loops if loop not in loops)
        return tuple(loops)

    @staticmethod
    def _score(profile: ObjectiveProfile, harness: HarnessPackage) -> int:
        """Score harness compatibility with the objective profile."""
        score = 0
        if profile.domain in harness.domains:
            score += 3
        if profile.phase in harness.phases:
            score += 2
        if profile.output_type in harness.outputs:
            score += 2
        return score
