"""Dependency-aware impact analysis for bounded safe replanning."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ReplanRecord, StageGraph


@dataclass(frozen=True, slots=True)
class ReplanService:
    """Create append-only replan records with downstream-only invalidation."""

    max_replans: int

    def __post_init__(self) -> None:
        if self.max_replans < 1:
            raise ValueError("max_replans must be at least 1")

    def create_record(
        self,
        *,
        graph: StageGraph,
        replan_attempt: int,
        replan_id: str,
        run_id: str,
        changed_stage_ids: tuple[str, ...],
        artifact_refs_by_stage: dict[str, tuple[str, ...]],
        approval_ids_by_stage: dict[str, tuple[str, ...]],
        requested_change: str,
        reason: str,
        new_bundle_id: str,
        new_bundle_version: str,
        confirmation_required: bool,
        requested_at: str,
        evidence_refs_by_stage: dict[str, tuple[str, ...]] | None = None,
        invalidate_acceptance: bool = False,
    ) -> ReplanRecord:
        """Analyze impacted stages and return their invalidation record."""
        if replan_attempt < 1:
            raise ValueError("replan_attempt must be at least 1")
        if replan_attempt > self.max_replans:
            raise ValueError("maximum replan attempts reached; escalate")
        if not changed_stage_ids:
            raise ValueError("changed_stage_ids must not be empty")

        stage_ids = {node.stage.stage_id for node in graph.nodes}
        unknown = sorted(set(changed_stage_ids) - stage_ids)
        if unknown:
            raise ValueError(f"unknown stage: {unknown[0]}")

        impacts = self._downstream_stage_ids(graph, changed_stage_ids)
        return ReplanRecord(
            replan_id=replan_id,
            run_id=run_id,
            requested_change=requested_change,
            reason=reason,
            dependency_impacts=impacts,
            invalidated_artifact_refs=self._refs_for_stages(
                impacts, artifact_refs_by_stage
            ),
            archived_artifact_refs=(),
            invalidated_approval_ids=self._refs_for_stages(
                impacts, approval_ids_by_stage
            ),
            new_bundle_id=new_bundle_id,
            new_bundle_version=new_bundle_version,
            confirmation_required=confirmation_required,
            safe_resume_stage_id=impacts[0],
            requested_at=requested_at,
            invalidated_evidence_refs=self._refs_for_stages(
                impacts, evidence_refs_by_stage or {}
            ),
            invalidated_acceptance=invalidate_acceptance,
        )

    @staticmethod
    def _downstream_stage_ids(
        graph: StageGraph,
        changed_stage_ids: tuple[str, ...],
    ) -> tuple[str, ...]:
        """Return changed stages and descendants in deterministic traversal order."""
        successors: dict[str, list[str]] = {}
        for edge in graph.edges:
            successors.setdefault(edge.from_stage_id, []).append(edge.to_stage_id)

        queue = list(dict.fromkeys(changed_stage_ids))
        impacts: list[str] = []
        while queue:
            stage_id = queue.pop(0)
            if stage_id in impacts:
                continue
            impacts.append(stage_id)
            queue.extend(sorted(successors.get(stage_id, ())))
        return tuple(impacts)

    @staticmethod
    def _refs_for_stages(
        stage_ids: tuple[str, ...],
        refs_by_stage: dict[str, tuple[str, ...]],
    ) -> tuple[str, ...]:
        """Collect unique refs for impacted stages while preserving lineage order."""
        refs: list[str] = []
        for stage_id in stage_ids:
            refs.extend(
                ref for ref in refs_by_stage.get(stage_id, ()) if ref not in refs
            )
        return tuple(refs)
