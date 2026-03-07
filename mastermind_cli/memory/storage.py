"""YAML Storage for evaluation persistence."""

from pathlib import Path
import yaml
from datetime import datetime
from typing import List, Optional
import logging

from .models import EvaluationEntry

logger = logging.getLogger(__name__)


class YamlStorage:
    """YAML-based storage for evaluations."""

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize YAML storage.

        Args:
            base_path: Base path for storage. Defaults to logs/evaluations/hot
        """
        if base_path is None:
            base_path = Path("logs/evaluations/hot")

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create month subdirectory
        month_dir = datetime.utcnow().strftime("%Y-%m")
        self.current_path = self.base_path / month_dir
        self.current_path.mkdir(exist_ok=True)

    def save(self, entry: EvaluationEntry) -> str:
        """
        Save evaluation entry to YAML file.

        Args:
            entry: EvaluationEntry to save

        Returns:
            evaluation_id: The ID of the saved evaluation
        """
        # Generate ID if not exists
        if not entry.evaluation_id:
            eval_id = f"EVAL-{entry.timestamp.strftime('%Y-%m-%d-%H%M%S')}"
            entry.evaluation_id = eval_id
        else:
            eval_id = entry.evaluation_id

        # Save to file
        filepath = self.current_path / f"{eval_id}.yaml"
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(entry.to_dict(), f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        logger.info(f"Saved evaluation {eval_id} to {filepath}")

        # Update index
        self._update_index(entry)

        return eval_id

    def find_by_project(self, project: str) -> List[EvaluationEntry]:
        """
        Find all evaluations for a specific project.

        Args:
            project: Project name to search for

        Returns:
            List of EvaluationEntry objects
        """
        evaluations = []
        for yaml_file in self._all_yaml_files():
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and data.get("project") == project:
                        evaluations.append(EvaluationEntry.from_dict(data))
            except (yaml.YAMLError, KeyError) as e:
                logger.warning(f"Failed to load {yaml_file}: {e}")

        # Sort by timestamp descending
        evaluations.sort(key=lambda e: e.timestamp, reverse=True)
        return evaluations

    def find_by_verdict(self, verdict: str) -> List[EvaluationEntry]:
        """
        Find evaluations by verdict.

        Args:
            verdict: Verdict to filter by (APPROVE, CONDITIONAL, REJECT, ESCALATE)

        Returns:
            List of EvaluationEntry objects
        """
        evaluations = []
        for yaml_file in self._all_yaml_files():
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and data.get("verdict") == verdict:
                        evaluations.append(EvaluationEntry.from_dict(data))
            except (yaml.YAMLError, KeyError) as e:
                logger.warning(f"Failed to load {yaml_file}: {e}")

        evaluations.sort(key=lambda e: e.timestamp, reverse=True)
        return evaluations

    def find_recent(self, limit: int = 10) -> List[EvaluationEntry]:
        """
        Find most recent evaluations.

        Args:
            limit: Maximum number of evaluations to return

        Returns:
            List of EvaluationEntry objects
        """
        all_evaluations = []

        for yaml_file in self._all_yaml_files():
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        all_evaluations.append(EvaluationEntry.from_dict(data))
            except (yaml.YAMLError, KeyError) as e:
                logger.warning(f"Failed to load {yaml_file}: {e}")

        # Sort by timestamp descending and limit
        all_evaluations.sort(key=lambda e: e.timestamp, reverse=True)
        return all_evaluations[:limit]

    def find_by_id(self, evaluation_id: str) -> Optional[EvaluationEntry]:
        """
        Find evaluation by ID.

        Args:
            evaluation_id: ID to search for

        Returns:
            EvaluationEntry if found, None otherwise
        """
        for yaml_file in self._all_yaml_files():
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and data.get("evaluation_id") == evaluation_id:
                        return EvaluationEntry.from_dict(data)
            except (yaml.YAMLError, KeyError):
                continue

        return None

    def search(self, query: str) -> List[EvaluationEntry]:
        """
        Search evaluations by keyword in brief or output.

        Args:
            query: Keyword to search for

        Returns:
            List of matching EvaluationEntry objects
        """
        results = []
        query_lower = query.lower()

        for yaml_file in self._all_yaml_files():
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        brief = data.get("brief", "").lower()
                        output = data.get("full_output", "").lower()

                        if query_lower in brief or query_lower in output:
                            results.append(EvaluationEntry.from_dict(data))
            except (yaml.YAMLError, KeyError):
                continue

        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results

    def _all_yaml_files(self) -> List[Path]:
        """Get all YAML files in storage."""
        return list(self.base_path.glob("**/*.yaml"))

    def _update_index(self, entry: EvaluationEntry):
        """Update index file for fast lookups."""
        index_file = self.current_path / "index.yaml"

        # Load existing index with error handling
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    index = yaml.safe_load(f) or {}
            except (yaml.YAMLError, IOError):
                index = {}
        else:
            index = {}

        # Add/update entry
        index[entry.evaluation_id] = {
            "timestamp": entry.timestamp.isoformat(),
            "project": entry.project,
            "verdict": entry.verdict.value,
            "score": entry.score.total,
            "tags": entry.tags,
            "brief": entry.brief[:100] + "..." if len(entry.brief) > 100 else entry.brief,
        }

        # Save index
        with open(index_file, "w", encoding="utf-8") as f:
            yaml.dump(index, f, default_flow_style=False, sort_keys=True)

        logger.debug(f"Updated index with {entry.evaluation_id}")

    def get_stats(self) -> dict:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage stats
        """
        all_evals = self.find_recent(limit=10000)  # Get all

        verdict_counts = {}
        project_counts = {}

        for eval in all_evals:
            # Count verdicts
            verdict = eval.verdict.value
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

            # Count projects
            project = eval.project
            project_counts[project] = project_counts.get(project, 0) + 1

        return {
            "total_evaluations": len(all_evals),
            "verdict_breakdown": verdict_counts,
            "top_projects": dict(sorted(project_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "storage_path": str(self.base_path),
        }
