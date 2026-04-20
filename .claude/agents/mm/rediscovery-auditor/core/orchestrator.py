"""Orchestrator for multi-stack project analysis."""

from pathlib import Path
from typing import Any, Dict, List

from .strategies.base import ProjectStrategy
from .strategies.node import NodeStrategy
from .strategies.python import PythonStrategy
from .strategies.rust import RustStrategy


class Orchestrator:
    """Coordinate multiple project analysis strategies."""

    STRATEGY_MAP = {
        "python": PythonStrategy,
        "node": NodeStrategy,
        "rust": RustStrategy,
    }

    def __init__(self, root_path: Path, fingerprint: Dict):
        """Initialize orchestrator with project fingerprint.

        Args:
            root_path: Path to project root
            fingerprint: Fingerprint from ProjectDetector
        """
        self.root = root_path
        self.fingerprint = fingerprint
        self.strategies = self._load_strategies()

    def _load_strategies(self) -> List[ProjectStrategy]:
        """Load strategies based on fingerprint.

        Returns:
            List of instantiated strategy objects
        """
        strategies = []

        for stack in self.fingerprint.get("stacks", []):
            strategy_class = self.STRATEGY_MAP.get(stack)
            if strategy_class:
                structure_info = self.fingerprint.get("structure", {}).get(stack, {})
                strategies.append(strategy_class(self.root, structure_info))

        return strategies

    def execute_all(self) -> Dict[str, Any]:
        """Execute all strategies and merge results.

        Returns:
            Dict mapping stack names to analysis results
        """
        results = {}

        for strategy in self.strategies:
            is_valid, error = strategy.validate()

            if is_valid:
                results[strategy.name] = {
                    "tests": strategy.run_tests(),
                    "deps": strategy.analyze_deps(),
                    "code": strategy.analyze_code(),
                    "coverage": strategy.get_coverage(),
                    "status": "success",
                }
            else:
                results[strategy.name] = {"status": "skipped", "reason": error}

        return results

    def format_health_report(self) -> str:
        """Format results as markdown for HEALTH-CHECK.md.

        Returns:
            Markdown formatted health report
        """
        results = self.execute_all()
        lines = ["# Project Health Check\n"]

        for stack_name, stack_results in results.items():
            lines.append(f"## {stack_name.title()} Stack\n")

            if stack_results.get("status") == "skipped":
                lines.append(f"⏭️ Skipped: {stack_results.get('reason')}\n")
                continue

            # Tests
            tests = stack_results.get("tests", {})
            if tests.get("status") == "success":
                lines.append(
                    f"- ✅ Tests: {tests['passing']} passing, "
                    f"{tests['failing']} failing\n"
                )
            else:
                lines.append(f"- ❌ Tests: {tests.get('error', 'Failed to run')}\n")

            # Coverage
            coverage = stack_results.get("coverage")
            if coverage is not None:
                symbol = "✅" if coverage >= 80 else "⚠️" if coverage >= 60 else "❌"
                lines.append(f"- {symbol} Coverage: {coverage}%\n")

            # Dependencies
            deps = stack_results.get("deps", {})
            if deps.get("status") == "success":
                outdated = deps.get("outdated", 0)
                symbol = "✅" if outdated == 0 else "⚠️"
                lines.append(f"- {symbol} Dependencies: {outdated} outdated\n")
            elif deps.get("status") == "skipped":
                lines.append(f"- ⏭️ Dependencies: {deps.get('reason', 'Skipped')}\n")

            # Code metrics
            code = stack_results.get("code", {})
            if code.get("files"):
                lines.append(
                    f"- 📊 Code: {code['files']} files, "
                    f"{code['lines_of_code']} lines\n"
                )

            lines.append("")  # Blank line

        return "\n".join(lines)
