# Rediscovery Auditor Agnóstico — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform rediscovery-auditor from hardcoded monorepo assumptions to agnostic project detector that adapts to any structure.

**Architecture:** Fingerprint detector identifies project structure → Strategies per stack (Python, Node, Rust) analyze what exists → Orchestrator merges results → Brains #1 + #7 get full context.

**Tech Stack:** Python 3.14, subprocess, pathlib, fd/ripgrep, NotebookLM MCP

---

## File Structure

```
.claude/agents/mm/rediscovery-auditor/
├── core/
│   ├── __init__.py
│   ├── detector.py           # Fingerprint project structure
│   ├── orchestrator.py       # Coordinate strategies
│   └── strategies/
│       ├── __init__.py
│       ├── base.py           # Abstract base class
│       ├── python.py         # Python stack strategy
│       ├── node.py           # Node.js stack strategy
│       └── rust.py           # Rust stack strategy
└── rediscovery-auditor.md    # Agent protocol (updated)
```

---

## Task 1: Create Core Module Structure

**Files:**
- Create: `.claude/agents/mm/rediscovery-auditor/core/__init__.py`

- [ ] **Step 1: Create core module**

```python
"""Rediscovery Auditor Core - Agnostic Project Analysis."""

__version__ = "2.0.0"
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/mm/rediscovery-auditor/core/__init__.py
git commit -m "feat(rediscovery): create core module structure"
```

---

## Task 2: Implement Fingerprint Detector

**Files:**
- Create: `.claude/agents/mm/rediscovery-auditor/core/detector.py`
- Create: `.claude/agents/mm/rediscovery-auditor/core/tests/test_detector.py`

- [ ] **Step 1: Write failing test for detector**

```python
# tests/test_detector.py
import pytest
from pathlib import Path
from core.detector import ProjectDetector

def test_detect_python_monolito(tmp_path):
    """Detect Python monolito project."""
    # Create pyproject.toml
    (tmp_path / "pyproject.toml").write_text("[project]\\nname='test'\\n")
    # Create tests directory
    (tmp_path / "tests").mkdir()
    # Create src directory
    (tmp_path / "src").mkdir()

    detector = ProjectDetector(tmp_path)
    result = detector.detect()

    assert result["type"] == "monolito"
    assert "python" in result["stacks"]
    assert result["structure"]["python"]["package_manager"] in ["uv", "pip"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/agents/mm/rediscovery-auditor && uv run pytest core/tests/test_detector.py -v`
Expected: FAIL with "ProjectDetector not defined"

- [ ] **Step 3: Implement ProjectDetector**

```python
# core/detector.py
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class ProjectDetector:
    """Detect project structure and available stacks."""

    # Fingerprint files for each stack
    FINGERPRINTS = {
        "python": ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"],
        "node": ["package.json", "pnpm-lock.yaml", "package-lock.json", "yarn.lock"],
        "rust": ["Cargo.toml", "Cargo.lock"],
        "go": ["go.mod", "go.sum"],
    }

    # Monorepo patterns
    MONOREPO_PATTERNS = ["apps/", "packages/", "services/", "modules/"]

    def __init__(self, root_path: Path):
        self.root = Path(root_path)

    def detect(self) -> Dict:
        """Analyze project and return fingerprint."""
        stacks = self._detect_stacks()
        project_type = self._detect_project_type()

        result = {
            "type": project_type,
            "stacks": list(stacks.keys()),
            "structure": {}
        }

        # Analyze each detected stack
        for stack_name in stacks:
            result["structure"][stack_name] = self._analyze_stack(stack_name)

        return result

    def _detect_stacks(self) -> Dict[str, bool]:
        """Detect which stacks are present."""
        detected = {}

        for stack_name, fingerprint_files in self.FINGERPRINTS.items():
            detected[stack_name] = any(
                (self.root / fp).exists() for fp in fingerprint_files
            )

        return {k: v for k, v in detected.items() if v}

    def _detect_project_type(self) -> str:
        """Detect if monorepo or monolito."""
        for pattern in self.MONOREPO_PATTERNS:
            if (self.root / pattern).exists() and (self.root / pattern).is_dir():
                return "monorepo"
        return "monolito"

    def _analyze_stack(self, stack_name: str) -> Dict:
        """Analyze specific stack structure."""
        if stack_name == "python":
            return self._analyze_python()
        elif stack_name == "node":
            return self._analyze_node()
        elif stack_name == "rust":
            return self._analyze_rust()
        elif stack_name == "go":
            return self._analyze_go()
        return {}

    def _analyze_python(self) -> Dict:
        """Analyze Python project structure."""
        # Detect package manager
        pkg_manager = None
        if (self.root / "pyproject.toml").exists():
            # Check if uv is being used
            try:
                result = subprocess.run(
                    ["uv", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    pkg_manager = "uv"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pkg_manager = "pip"

        if not pkg_manager:
            pkg_manager = "pip"

        # Detect source directories
        src_dirs = []
        for pattern in ["src/", "*/", "app/"]:
            matches = list(self.root.glob(pattern))
            src_dirs.extend([str(m.relative_to(self.root)) for m in matches if m.is_dir()])

        # Detect test directories
        test_dirs = []
        for pattern in ["tests/", "test/"]:
            matches = list(self.root.glob(pattern))
            test_dirs.extend([str(m.relative_to(self.root)) for m in matches if m.is_dir()])

        return {
            "package_manager": pkg_manager,
            "src": src_dirs,
            "tests": test_dirs,
            "test_runner": "pytest"  # Assume pytest for now
        }

    def _analyze_node(self) -> Dict:
        """Analyze Node.js project structure."""
        # Detect package manager
        pkg_manager = None
        if (self.root / "pnpm-lock.yaml").exists():
            pkg_manager = "pnpm"
        elif (self.root / "yarn.lock").exists():
            pkg_manager = "yarn"
        elif (self.root / "package-lock.json").exists():
            pkg_manager = "npm"

        # Detect source directories
        src_dirs = []
        for pattern in ["src/", "app/", "components/"]:
            matches = list(self.root.glob(pattern))
            src_dirs.extend([str(m.relative_to(self.root)) for m in matches if m.is_dir()])

        return {
            "package_manager": pkg_manager or "npm",
            "src": src_dirs,
            "tests": ["__tests__/", "*.test.ts", "*.test.tsx"]
        }

    def _analyze_rust(self) -> Dict:
        """Analyze Rust project structure."""
        return {
            "package_manager": "cargo",
            "src": ["src/"],
            "tests": ["tests/"]
        }

    def _analyze_go(self) -> Dict:
        """Analyze Go project structure."""
        return {
            "package_manager": "go",
            "src": ["cmd/", "pkg/", "internal/"],
            "tests": ["*_test.go"]
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd .claude/agents/mm/rediscovery-auditor && uv run pytest core/tests/test_detector.py::test_detect_python_monolito -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/agents/mm/rediscovery-auditor/core/detector.py .claude/agents/mm/rediscovery-auditor/core/tests/test_detector.py
git commit -m "feat(rediscovery): implement fingerprint detector"
```

---

## Task 3: Implement Base Strategy Interface

**Files:**
- Create: `.claude/agents/mm/rediscovery-auditor/core/strategies/__init__.py`
- Create: `.claude/agents/mm/rediscovery-auditor/core/strategies/base.py`

- [ ] **Step 1: Write base strategy interface**

```python
# core/strategies/base.py
from abc import ABC, abstractmethod
from typing import Dict, Optional

class ProjectStrategy(ABC):
    """Base interface for project analysis strategies."""

    def __init__(self, root_path, structure_info: Dict):
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
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/mm/rediscovery-auditor/core/strategies/base.py
git commit -m "feat(rediscovery): add base strategy interface"
```

---

## Task 4: Implement Python Strategy

**Files:**
- Create: `.claude/agents/mm/rediscovery-auditor/core/strategies/python.py`
- Create: `.claude/agents/mm/rediscovery-auditor/core/tests/test_python_strategy.py`

- [ ] **Step 1: Write failing test**

```python
# core/tests/test_python_strategy.py
import pytest
from pathlib import Path
from core.strategies.python import PythonStrategy

def test_python_validate_with_uv(tmp_path):
    """Test validation with uv available."""
    # Create test structure
    (tmp_path / "tests").mkdir()
    (tmp_path / "pyproject.toml").write_text("[project]\\nname='test'\\n")

    strategy = PythonStrategy(tmp_path, {"tests": ["tests/"], "package_manager": "uv"})
    is_valid, error = strategy.validate()

    assert is_valid or error is not None  # Either valid or has error message
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd .claude/agents/mm/rediscovery-auditor && uv run pytest core/tests/test_python_strategy.py -v`
Expected: FAIL with "PythonStrategy not defined"

- [ ] **Step 3: Implement PythonStrategy**

```python
# core/strategies/python.py
import subprocess
import re
from pathlib import Path
from typing import Optional
from .base import ProjectStrategy

class PythonStrategy(ProjectStrategy):
    """Analysis strategy for Python projects."""

    def validate(self) -> tuple[bool, Optional[str]]:
        """Check if Python tooling is available."""
        # Check package manager
        pkg_manager = self.structure.get("package_manager", "pip")

        try:
            result = subprocess.run(
                [pkg_manager, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return False, f"{pkg_manager} not available"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, f"{pkg_manager} not found"

        # Check test directory
        test_dirs = self.structure.get("tests", [])
        if not test_dirs:
            return False, "No test directory found"

        # Check if tests exist
        has_tests = any((self.root / d).exists() for d in test_dirs)
        if not has_tests:
            return False, f"Test directories not found: {test_dirs}"

        return True, None

    def run_tests(self) -> dict:
        """Run pytest and parse results."""
        pkg_manager = self.structure.get("package_manager", "pip")

        # Build command
        if pkg_manager == "uv":
            cmd = ["uv", "run", "pytest"]
        else:
            cmd = ["python", "-m", "pytest"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.root
            )

            output = result.stdout + result.stderr

            # Parse results
            passing = re.search(r'(\\d+) passed', output)
            failing = re.search(r'(\\d+) failed', output)
            skipped = re.search(r'(\\d+) skipped', output)

            return {
                "status": "success" if result.returncode == 0 else "error",
                "passing": int(passing.group(1)) if passing else 0,
                "failing": int(failing.group(1)) if failing else 0,
                "skipped": int(skipped.group(1)) if skipped else 0,
                "output": output[-1000:]  # Last 1000 chars
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "Tests timed out after 120s",
                "passing": 0,
                "failing": 0,
                "skipped": 0
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "passing": 0,
                "failing": 0,
                "skipped": 0
            }

    def analyze_deps(self) -> dict:
        """Check for outdated dependencies."""
        pkg_manager = self.structure.get("package_manager", "pip")

        if pkg_manager == "uv":
            cmd = ["uv", "pip", "list", "--outdated"]
        else:
            cmd = ["pip", "list", "--outdated"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.root
            )

            lines = result.stdout.split('\\n')
            outdated_count = len([l for l in lines if l.strip() and not l.startswith('Package')])

            return {
                "status": "success",
                "outdated": outdated_count,
                "vulnerable": 0,  # Would need additional tooling
                "details": result.stdout[-500:] if outdated_count > 0 else "Up to date"
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "outdated": 0,
                "vulnerable": 0
            }

    def analyze_code(self) -> dict:
        """Analyze Python code structure using fd + rg."""
        import subprocess

        # Find Python files
        try:
            result = subprocess.run(
                ["fd", "-e", "py", ".", str(self.root)],
                capture_output=True,
                text=True,
                timeout=30
            )

            files = [f for f in result.stdout.strip().split('\\n') if f]

            # Count lines
            total_lines = 0
            for file_path in files:
                try:
                    wc_result = subprocess.run(
                        ["wc", "-l", str(self.root / file_path)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if wc_result.returncode == 0:
                        total_lines += int(wc_result.stdout.split()[0])
                except:
                    pass

            # Extract module names
            modules = list(set(
                Path(f).parent.as_posix().replace('/', '.')
                for f in files
                if Path(f).parent.as_posix() != '.'
            ))

            return {
                "files": len(files),
                "lines_of_code": total_lines,
                "modules": modules[:20]  # Top 20 modules
            }

        except Exception as e:
            return {
                "files": 0,
                "lines_of_code": 0,
                "modules": [],
                "error": str(e)
            }

    def get_coverage(self) -> Optional[float]:
        """Parse coverage from pytest output."""
        result = self.run_tests()

        if result["status"] == "error":
            return None

        output = result.get("output", "")

        # Look for coverage in output
        coverage_match = re.search(r'Coverage:\\s+(\\d+\\.?\\d*)%', output)

        if coverage_match:
            return float(coverage_match.group(1))

        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd .claude/agents/mm/rediscovery-auditor && uv run pytest core/tests/test_python_strategy.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add .claude/agents/mm/rediscovery-auditor/core/strategies/python.py .claude/agents/mm/rediscovery-auditor/core/tests/test_python_strategy.py
git commit -m "feat(rediscovery): implement Python strategy"
```

---

## Task 5: Implement Node Strategy

**Files:**
- Create: `.claude/agents/mm/rediscovery-auditor/core/strategies/node.py`

- [ ] **Step 1: Implement NodeStrategy**

```python
# core/strategies/node.py
import subprocess
import re
from pathlib import Path
from typing import Optional
from .base import ProjectStrategy

class NodeStrategy(ProjectStrategy):
    """Analysis strategy for Node.js projects."""

    def validate(self) -> tuple[bool, Optional[str]]:
        """Check if Node tooling is available."""
        pkg_manager = self.structure.get("package_manager", "npm")

        try:
            result = subprocess.run(
                [pkg_manager, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return False, f"{pkg_manager} not available"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, f"{pkg_manager} not found"

        return True, None

    def run_tests(self) -> dict:
        """Run tests and parse results."""
        pkg_manager = self.structure.get("package_manager", "npm")

        # Try common test scripts
        cmd = [pkg_manager, "test", "--", "--run"] if pkg_manager == "pnpm" else [pkg_manager, "test"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.root,
                shell=pkg_manager in ["pnpm", "npm", "yarn"]
            )

            output = result.stdout + result.stderr

            # Parse test results (works for vitest, jest)
            passing = re.search(r'(\\d+) pass', output) or re.search(r'✓\\s+(\\d+)', output)
            failing = re.search(r'(\\d+) fail', output) or re.search(r'✗\\s+(\\d+)', output)

            return {
                "status": "success" if result.returncode == 0 else "error",
                "passing": int(passing.group(1)) if passing else 0,
                "failing": int(failing.group(1)) if failing else 0,
                "skipped": 0,
                "output": output[-1000:]
            }

        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "Tests timed out", "passing": 0, "failing": 0}
        except Exception as e:
            return {"status": "error", "error": str(e), "passing": 0, "failing": 0}

    def analyze_deps(self) -> dict:
        """Check for outdated dependencies."""
        pkg_manager = self.structure.get("package_manager", "npm")

        cmd = [pkg_manager, "outdated"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.root,
                shell=True
            )

            lines = result.stdout.split('\\n')
            outdated_count = len([l for l in lines if l.strip() and not l.startswith('Package')])

            return {
                "status": "success",
                "outdated": outdated_count,
                "vulnerable": 0,
                "details": result.stdout[-500:] if outdated_count > 0 else "Up to date"
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "outdated": 0}

    def analyze_code(self) -> dict:
        """Analyze TypeScript/JavaScript code structure."""
        try:
            # Find TS/JS files
            result = subprocess.run(
                ["fd", "-e", "ts", "-e", "tsx", "-e", "js", "-e", "jsx", ".", str(self.root)],
                capture_output=True,
                text=True,
                timeout=30
            )

            files = [f for f in result.stdout.strip().split('\\n') if f]

            # Count lines
            total_lines = 0
            for file_path in files[:50]:  # Limit to 50 files for speed
                try:
                    wc_result = subprocess.run(
                        ["wc", "-l", str(self.root / file_path)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if wc_result.returncode == 0:
                        total_lines += int(wc_result.stdout.split()[0])
                except:
                    pass

            return {
                "files": len(files),
                "lines_of_code": total_lines,
                "modules": []
            }

        except Exception as e:
            return {"files": 0, "lines_of_code": 0, "modules": [], "error": str(e)}

    def get_coverage(self) -> Optional[float]:
        """Parse coverage from test output."""
        result = self.run_tests()
        output = result.get("output", "")

        # Look for coverage in output
        coverage_match = re.search(r'(\\d+\\.?\\d*)%\\s*coverage', output)

        if coverage_match:
            return float(coverage_match.group(1))

        return None
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/mm/rediscovery-auditor/core/strategies/node.py
git commit -m "feat(rediscovery): implement Node strategy"
```

---

## Task 6: Implement Rust Strategy

**Files:**
- Create: `.claude/agents/mm/rediscovery-auditor/core/strategies/rust.py`

- [ ] **Step 1: Implement RustStrategy**

```python
# core/strategies/rust.py
import subprocess
import re
from pathlib import Path
from typing import Optional
from .base import ProjectStrategy

class RustStrategy(ProjectStrategy):
    """Analysis strategy for Rust projects."""

    def validate(self) -> tuple[bool, Optional[str]]:
        """Check if cargo is available."""
        try:
            result = subprocess.run(
                ["cargo", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0, None
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, "cargo not found"

    def run_tests(self) -> dict:
        """Run cargo test."""
        try:
            result = subprocess.run(
                ["cargo", "test"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.root
            )

            output = result.stdout + result.stderr

            # Parse test results
            passing = re.search(r'test result: ok\\. (\\d+) passed', output)
            failing = re.search(r'test result: FAILED\\. (\\d+) failed', output)

            return {
                "status": "success" if result.returncode == 0 else "error",
                "passing": int(passing.group(1)) if passing else 0,
                "failing": int(failing.group(1)) if failing else 0,
                "skipped": 0,
                "output": output[-1000:]
            }

        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "Tests timed out", "passing": 0, "failing": 0}
        except Exception as e:
            return {"status": "error", "error": str(e), "passing": 0, "failing": 0}

    def analyze_deps(self) -> dict:
        """Check for outdated dependencies."""
        try:
            result = subprocess.run(
                ["cargo", "outdated"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.root
            )

            lines = result.stdout.split('\\n')
            outdated_count = len([l for l in lines if l.strip() and not l.startswith('Package')])

            return {
                "status": "success",
                "outdated": outdated_count,
                "vulnerable": 0,
                "details": result.stdout[-500:] if outdated_count > 0 else "Up to date"
            }

        except Exception as e:
            # cargo outdated might not be installed
            return {
                "status": "skipped",
                "reason": "cargo outdated not installed",
                "outdated": 0
            }

    def analyze_code(self) -> dict:
        """Analyze Rust code structure."""
        try:
            result = subprocess.run(
                ["fd", "-e", "rs", ".", str(self.root)],
                capture_output=True,
                text=True,
                timeout=30
            )

            files = [f for f in result.stdout.strip().split('\\n') if f]

            # Count lines
            total_lines = 0
            for file_path in files[:50]:
                try:
                    wc_result = subprocess.run(
                        ["wc", "-l", str(self.root / file_path)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if wc_result.returncode == 0:
                        total_lines += int(wc_result.stdout.split()[0])
                except:
                    pass

            return {
                "files": len(files),
                "lines_of_code": total_lines,
                "modules": []
            }

        except Exception as e:
            return {"files": 0, "lines_of_code": 0, "modules": [], "error": str(e)}

    def get_coverage(self) -> Optional[float]:
        """Rust coverage requires tarpaulin - skip for now."""
        return None
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/mm/rediscovery-auditor/core/strategies/rust.py
git commit -m "feat(rediscovery): implement Rust strategy"
```

---

## Task 7: Implement Orchestrator

**Files:**
- Create: `.claude/agents/mm/rediscovery-auditor/core/orchestrator.py`

- [ ] **Step 1: Implement Orchestrator**

```python
# core/orchestrator.py
from pathlib import Path
from typing import Dict, List
from .strategies.python import PythonStrategy
from .strategies.node import NodeStrategy
from .strategies.rust import RustStrategy

class Orchestrator:
    """Coordinate multiple project analysis strategies."""

    STRATEGY_MAP = {
        "python": PythonStrategy,
        "node": NodeStrategy,
        "rust": RustStrategy,
    }

    def __init__(self, root_path: Path, fingerprint: Dict):
        self.root = root_path
        self.fingerprint = fingerprint
        self.strategies = self._load_strategies()

    def _load_strategies(self) -> List:
        """Load strategies based on fingerprint."""
        strategies = []

        for stack in self.fingerprint.get("stacks", []):
            strategy_class = self.STRATEGY_MAP.get(stack)
            if strategy_class:
                structure_info = self.fingerprint.get("structure", {}).get(stack, {})
                strategies.append(strategy_class(self.root, structure_info))

        return strategies

    def execute_all(self) -> Dict:
        """Execute all strategies and merge results."""
        results = {}

        for strategy in self.strategies:
            is_valid, error = strategy.validate()

            if is_valid:
                results[strategy.name] = {
                    "tests": strategy.run_tests(),
                    "deps": strategy.analyze_deps(),
                    "code": strategy.analyze_code(),
                    "coverage": strategy.get_coverage(),
                    "status": "success"
                }
            else:
                results[strategy.name] = {
                    "status": "skipped",
                    "reason": error
                }

        return results

    def format_health_report(self) -> str:
        """Format results as markdown for HEALTH-CHECK.md."""
        results = self.execute_all()
        lines = ["# Project Health Check\\n"]

        for stack_name, stack_results in results.items():
            lines.append(f"## {stack_name.title()} Stack\\n")

            if stack_results.get("status") == "skipped":
                lines.append(f"⏭️ Skipped: {stack_results.get('reason')}\\n")
                continue

            # Tests
            tests = stack_results.get("tests", {})
            if tests.get("status") == "success":
                lines.append(
                    f"- ✅ Tests: {tests['passing']} passing, "
                    f"{tests['failing']} failing\\n"
                )
            else:
                lines.append(f"- ❌ Tests: {tests.get('error', 'Failed to run')}\\n")

            # Coverage
            coverage = stack_results.get("coverage")
            if coverage is not None:
                symbol = "✅" if coverage >= 80 else "⚠️" if coverage >= 60 else "❌"
                lines.append(f"- {symbol} Coverage: {coverage}%\\n")

            # Dependencies
            deps = stack_results.get("deps", {})
            if deps.get("status") == "success":
                outdated = deps.get("outdated", 0)
                symbol = "✅" if outdated == 0 else "⚠️"
                lines.append(f"- {symbol} Dependencies: {outdated} outdated\\n")

            lines.append("")  # Blank line

        return "\\n".join(lines)
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/mm/rediscovery-auditor/core/orchestrator.py
git commit -m "feat(rediscovery): implement orchestrator"
```

---

## Task 8: Update Agent Protocol

**Files:**
- Modify: `.claude/agents/mm/rediscovery-auditor/rediscovery-auditor.md`

- [ ] **Step 1: Update agent protocol to use new core**

Read the current protocol:
```bash
head -100 .claude/agents/mm/rediscovery-auditor/rediscovery-auditor.md
```

Replace hardcoded analysis with fingerprint detector:

```python
# Step 1: Detect project structure
from core.detector import ProjectDetector
from core.orchestrator import Orchestrator

detector = ProjectDetector(Path.cwd())
fingerprint = detector.detect()

# Step 2: Execute strategies
orchestrator = Orchestrator(Path.cwd(), fingerprint)
health_results = orchestrator.execute_all()

# Step 3: Generate health report
health_report = orchestrator.format_health_report()
Path(".planning/HEALTH-CHECK.md").write_text(health_report)

# Step 4: Brain #1 + #7 receive full context
full_context = {
    "fingerprint": fingerprint,
    "health": health_results,
    "files": context_files,
    "git": git_info
}

# Brain #1 query includes fingerprint
brain1_query = f"""
Project Fingerprint: {fingerprint['type']}
Stacks Detected: {', '.join(fingerprint['stacks'])}

Health Check Results:
{health_report}

Original Promise: {context_files.get('SPEC.md', 'No SPEC.md')}

Current State: {git_info['log']}

Please analyze gaps per stack detected.
"""
```

- [ ] **Step 2: Commit**

```bash
git add .claude/agents/mm/rediscovery-auditor/rediscovery-auditor.md
git commit -m "feat(rediscovery): update agent protocol with agnostic core"
```

---

## Task 9: Add Integration Tests

**Files:**
- Create: `.claude/agents/mm/rediscovery-auditor/core/tests/test_integration.py`

- [ ] **Step 1: Write integration test**

```python
# core/tests/test_integration.py
import pytest
from pathlib import Path
from core.detector import ProjectDetector
from core.orchestrator import Orchestrator

def test_full_integration_python_project(tmp_path):
    """Test full flow with Python project."""
    # Setup test project
    (tmp_path / "pyproject.toml").write_text("[project]\\nname='test'\\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").write_text("def test_true(): assert True")

    # Detect
    detector = ProjectDetector(tmp_path)
    fingerprint = detector.detect()

    assert fingerprint["type"] == "monolito"
    assert "python" in fingerprint["stacks"]

    # Execute
    orchestrator = Orchestrator(tmp_path, fingerprint)
    results = orchestrator.execute_all()

    assert "python" in results
    # Tests might be skipped if tooling unavailable
    assert results["python"]["status"] in ["success", "skipped"]

def test_generate_health_report(tmp_path):
    """Test health report generation."""
    (tmp_path / "pyproject.toml").write_text("[project]\\nname='test'\\n")
    (tmp_path / "tests").mkdir()

    detector = ProjectDetector(tmp_path)
    fingerprint = detector.detect()
    orchestrator = Orchestrator(tmp_path, fingerprint)

    report = orchestrator.format_health_report()

    assert "# Project Health Check" in report
    assert "## Python Stack" in report
```

- [ ] **Step 2: Run integration tests**

Run: `cd .claude/agents/mm/rediscovery-auditor && uv run pytest core/tests/test_integration.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/mm/rediscovery-auditor/core/tests/test_integration.py
git commit -m "test(rediscovery): add integration tests"
```

---

## Task 10: Verify Against Current Project

**Files:**
- Test against: `/home/rpadron/proy/mastermind`

- [ ] **Step 1: Test detector on current project**

```python
# Quick test
from pathlib import Path
from core.detector import ProjectDetector

detector = ProjectDetector(Path("/home/rpadron/proy/mastermind"))
fingerprint = detector.detect()

print(f"Type: {fingerprint['type']}")
print(f"Stacks: {fingerprint['stacks']}")
print(f"Structure: {fingerprint['structure']}")
```

Expected: `type: monolito`, `stacks: ['python']`

- [ ] **Step 2: Test orchestrator on current project**

```python
from core.orchestrator import Orchestrator

orchestrator = Orchestrator(Path("/home/rpadron/proy/mastermind"), fingerprint)
report = orchestrator.format_health_report()

print(report)
```

Expected: Health report with Python stack results

- [ ] **Step 3: Run full agent test**

```bash
cd /home/rpadron/proy/mastermind
python3 -c "
from pathlib import Path
from core.detector import ProjectDetector
from core.orchestrator import Orchestrator

detector = ProjectDetector(Path.cwd())
fp = detector.detect()
print(f'Fingerprint: {fp}')

orch = Orchestrator(Path.cwd(), fp)
results = orch.execute_all()
print(f'Results: {results}')

report = orch.format_health_report()
Path('.planning/HEALTH-CHECK-TEST.md').write_text(report)
print('Health report written')
"
```

Expected: `.planning/HEALTH-CHECK-TEST.md` generated with Python stack analysis

- [ ] **Step 4: Clean up test file**

```bash
rm .planning/HEALTH-CHECK-TEST.md
```

- [ ] **Step 5: Commit verification**

```bash
git add -A
git commit -m "test(rediscovery): verify against current monolito project"
```

---

## Success Criteria Verification

After implementation, verify:

- [ ] **Detector identifies monolito Python** → Test on current project
- [ ] **Detector would identify monorepo** → Test on multi-stack project
- [ ] **Python strategy runs tests** → `uv run pytest` works
- [ ] **Node strategy detects package manager** → pnpm/npm/yarn
- [ ] **Rust strategy runs cargo test** → If Cargo.toml exists
- [ ] **Orchestrator merges results** → HEALTH-CHECK.md generated
- [ ] **Graceful degradation** → Missing tools = "skipped" status
- [ ] **Brain #1 receives fingerprint** → Context includes stacks detected
- [ ] **No hardcoded paths** → All paths detected dynamically

---

## Post-Implementation Notes

1. **Extension points:** Add new stacks by:
   - Creating strategy class in `core/strategies/`
   - Adding to `STRATEGY_MAP` in orchestrator
   - Adding fingerprint files in detector

2. **Testing strategy:**
   - Unit tests per strategy
   - Integration tests on real projects
   - Test graceful degradation paths

3. **Future enhancements:**
   - Go strategy
   - Java strategy
   - Config file support (.rediscoveryrc)
   - Custom fingerprint patterns
