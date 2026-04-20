"""Fingerprint-based project detector for rediscovery auditor."""

import subprocess
from pathlib import Path
from typing import Any, Dict, List


class ProjectDetector:
    """Detects project structure and available stacks using file fingerprints."""

    # File fingerprints for different stacks
    FINGERPRINTS: Dict[str, List[str]] = {
        "python": [
            "pyproject.toml",
            "requirements.txt",
            "setup.py",
            "Pipfile",
            "poetry.lock",
            "uv.lock",
        ],
        "node": [
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "tsconfig.json",
        ],
        "rust": [
            "Cargo.toml",
            "Cargo.lock",
        ],
        "go": [
            "go.mod",
            "go.sum",
            "main.go",
        ],
    }

    # Monorepo pattern indicators
    MONOREPO_PATTERNS = [
        "apps/",
        "packages/",
        "services/",
        "modules/",
        "packages/*",
    ]

    def __init__(self, project_path: Path):
        """Initialize detector with project path.

        Args:
            project_path: Root directory of the project to analyze
        """
        self.project_path = Path(project_path)

    def detect(self) -> Dict[str, Any]:
        """Detect project type, stacks, and structure.

        Returns:
            Dict with keys:
                - type: "monolito" | "monorepo" | "unknown"
                - stacks: list of detected stack names
                - structure: dict with per-stack details
        """
        if not self.project_path.exists():
            return {
                "type": "unknown",
                "stacks": [],
                "structure": {},
            }

        stacks = self._detect_stacks()
        project_type = self._detect_project_type(stacks)
        structure = self._analyze_stacks(stacks)

        return {
            "type": project_type,
            "stacks": stacks,
            "structure": structure,
        }

    def _detect_stacks(self) -> List[str]:
        """Detect which stacks are present in the project.

        Returns:
            List of stack names (e.g., ["python", "node"])
        """
        detected = []

        for stack, fingerprints in self.FINGERPRINTS.items():
            if any((self.project_path / fp).exists() for fp in fingerprints):
                detected.append(stack)

        return detected

    def _detect_project_type(self, stacks: List[str]) -> str:
        """Detect if project is monolito or monorepo.

        Args:
            stacks: List of detected stacks

        Returns:
            "monolito" | "monorepo" | "unknown"
        """
        if not stacks:
            return "unknown"

        # Check for monorepo patterns
        for pattern in self.MONOREPO_PATTERNS:
            pattern_path = self.project_path / pattern.replace("*/", "")
            if pattern_path.exists() and pattern_path.is_dir():
                # Check if it contains subdirectories (apps or packages)
                if any(pattern_path.iterdir()):
                    return "monorepo"

        # Multi-stack projects are often monorepos
        if len(stacks) > 1:
            return "monorepo"

        return "monolito"

    def _analyze_stacks(self, stacks: List[str]) -> Dict[str, Any]:
        """Analyze each detected stack for details.

        Args:
            stacks: List of detected stack names

        Returns:
            Dict with per-stack analysis (package_manager, version, tools)
        """
        structure = {}

        for stack in stacks:
            analyzer = getattr(self, f"_analyze_{stack}", None)
            if analyzer:
                structure[stack] = analyzer()
            else:
                structure[stack] = {}

        return structure

    def _analyze_python(self) -> Dict[str, Any]:
        """Analyze Python project details.

        Returns:
            Dict with package_manager, edition, tools
        """
        result = {
            "package_manager": "unknown",
            "tools": {},
        }

        # Detect package manager
        if (self.project_path / "uv.lock").exists():
            result["package_manager"] = "uv"
        elif (self.project_path / "poetry.lock").exists():
            result["package_manager"] = "poetry"
        elif (self.project_path / "Pipfile").exists():
            result["package_manager"] = "pipenv"
        elif (self.project_path / "pyproject.toml").exists():
            result["package_manager"] = "uv"  # Default to uv for modern projects
        elif (self.project_path / "requirements.txt").exists():
            result["package_manager"] = "pip"

        # Detect tool availability with timeout
        for tool in ["python", "uv", "pytest", "ruff"]:
            result["tools"][tool] = self._check_tool_available(tool)

        return result

    def _analyze_node(self) -> Dict[str, Any]:
        """Analyze Node.js project details.

        Returns:
            Dict with package_manager, version, tools
        """
        result = {
            "package_manager": "unknown",
            "tools": {},
        }

        # Detect package manager
        if (self.project_path / "pnpm-lock.yaml").exists():
            result["package_manager"] = "pnpm"
        elif (self.project_path / "yarn.lock").exists():
            result["package_manager"] = "yarn"
        elif (self.project_path / "package-lock.json").exists():
            result["package_manager"] = "npm"
        elif (self.project_path / "package.json").exists():
            result["package_manager"] = "npm"  # Default to npm

        # Detect tool availability
        for tool in ["node", "npm", "pnpm", "yarn", "npx"]:
            result["tools"][tool] = self._check_tool_available(tool)

        return result

    def _analyze_rust(self) -> Dict[str, Any]:
        """Analyze Rust project details.

        Returns:
            Dict with edition, tools
        """
        result = {
            "edition": "2021",  # Default to modern edition
            "tools": {},
        }

        # Try to read edition from Cargo.toml
        cargo_toml = self.project_path / "Cargo.toml"
        if cargo_toml.exists():
            try:
                content = cargo_toml.read_text()
                if 'edition = "2018"' in content:
                    result["edition"] = "2018"
            except Exception:
                pass

        # Detect tool availability
        for tool in ["rustc", "cargo"]:
            result["tools"][tool] = self._check_tool_available(tool)

        return result

    def _analyze_go(self) -> Dict[str, Any]:
        """Analyze Go project details.

        Returns:
            Dict with version, tools
        """
        result = {
            "version": "unknown",
            "tools": {},
        }

        # Try to read version from go.mod
        go_mod = self.project_path / "go.mod"
        if go_mod.exists():
            try:
                content = go_mod.read_text()
                for line in content.split("\n"):
                    if line.strip().startswith("go "):
                        result["version"] = line.strip()
                        break
            except Exception:
                pass

        # Detect tool availability
        for tool in ["go", "gofmt"]:
            result["tools"][tool] = self._check_tool_available(tool)

        return result

    def _check_tool_available(self, tool: str) -> bool:
        """Check if a CLI tool is available using subprocess with timeout.

        Args:
            tool: Tool command name (e.g., "python", "node")

        Returns:
            True if tool is available, False otherwise
        """
        try:
            subprocess.run(
                [tool, "--version"],
                capture_output=True,
                timeout=2,
                check=False,
            )
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        except Exception:
            return False
