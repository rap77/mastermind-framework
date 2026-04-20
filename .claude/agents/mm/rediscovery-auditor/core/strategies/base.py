from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class ProjectStrategy(ABC):
    """Base interface for project analysis strategies."""

    def __init__(self, root_path: Path, structure_info: Dict):
        self.root = root_path
        self.structure = structure_info
        self.name = self.__class__.__name__.replace("Strategy", "").lower()

    @abstractmethod
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate that required tooling exists.

        Returns:
            (is_valid, error_message)
        """
        pass

    @abstractmethod
    def run_tests(self) -> Dict:
        """
        Run tests and return results.

        Returns:
            {
                "status": "success" | "error" | "skipped",
                "passing": int,
                "failing": int,
                "skipped": int,
                "output": str
            }
        """
        pass

    @abstractmethod
    def analyze_deps(self) -> Dict:
        """
        Analyze dependencies for outdated packages.

        Returns:
            {
                "status": "success" | "error" | "skipped",
                "outdated": int,
                "vulnerable": int,
                "details": str
            }
        """
        pass

    @abstractmethod
    def analyze_code(self) -> Dict:
        """
        Analyze code structure using fd + rg.

        Returns:
            {
                "files": int,
                "lines_of_code": int,
                "modules": List[str]
            }
        """
        pass

    @abstractmethod
    def get_coverage(self) -> Optional[float]:
        """
        Get test coverage percentage.

        Returns:
            Coverage as float (0-100) or None if unavailable
        """
        pass
