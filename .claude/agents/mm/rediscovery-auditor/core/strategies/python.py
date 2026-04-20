import subprocess
import re
from pathlib import Path
from typing import Optional
from .base import ProjectStrategy


class PythonStrategy(ProjectStrategy):
    """Analysis strategy for Python projects."""

    def validate(self) -> tuple[bool, Optional[str]]:
        """Check if Python tooling is available.

        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        pkg_manager = self.structure.get("package_manager", "pip")

        try:
            result = subprocess.run(
                [pkg_manager, "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False, f"{pkg_manager} not available"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, f"{pkg_manager} not found"

        test_dirs = self.structure.get("tests", [])
        if not test_dirs:
            return False, "No test directory found"

        has_tests = any((self.root / d).exists() for d in test_dirs)
        if not has_tests:
            return False, f"Test directories not found: {test_dirs}"

        return True, None

    def run_tests(self) -> dict:
        """Run pytest and parse results.

        Returns:
            dict: Test results with status, passing, failing, skipped counts
        """
        pkg_manager = self.structure.get("package_manager", "pip")

        if pkg_manager == "uv":
            cmd = ["uv", "run", "pytest"]
        else:
            cmd = ["python", "-m", "pytest"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120, cwd=self.root
            )

            output = result.stdout + result.stderr

            passing = re.search(r"(\d+) passed", output)
            failing = re.search(r"(\d+) failed", output)
            skipped = re.search(r"(\d+) skipped", output)

            return {
                "status": "success" if result.returncode == 0 else "error",
                "passing": int(passing.group(1)) if passing else 0,
                "failing": int(failing.group(1)) if failing else 0,
                "skipped": int(skipped.group(1)) if skipped else 0,
                "output": output[-1000:],
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": "Tests timed out after 120s",
                "passing": 0,
                "failing": 0,
                "skipped": 0,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "passing": 0,
                "failing": 0,
                "skipped": 0,
            }

    def analyze_deps(self) -> dict:
        """Check for outdated dependencies.

        Returns:
            dict: Dependency status with outdated count
        """
        pkg_manager = self.structure.get("package_manager", "pip")

        if pkg_manager == "uv":
            cmd = ["uv", "pip", "list", "--outdated"]
        else:
            cmd = ["pip", "list", "--outdated"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, cwd=self.root
            )

            lines = result.stdout.split("\n")
            outdated_count = len(
                [
                    line
                    for line in lines
                    if line.strip() and not line.startswith("Package")
                ]
            )

            return {
                "status": "success",
                "outdated": outdated_count,
                "vulnerable": 0,
                "details": result.stdout[-500:] if outdated_count > 0 else "Up to date",
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "outdated": 0, "vulnerable": 0}

    def analyze_code(self) -> dict:
        """Analyze Python code structure using fd + rg.

        Returns:
            dict: Code metrics with file count, lines of code, modules
        """
        try:
            result = subprocess.run(
                ["fd", "-e", "py", ".", str(self.root)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            files = [f for f in result.stdout.strip().split("\n") if f]

            total_lines = 0
            for file_path in files:
                try:
                    wc_result = subprocess.run(
                        ["wc", "-l", str(self.root / file_path)],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if wc_result.returncode == 0:
                        total_lines += int(wc_result.stdout.split()[0])
                except Exception:
                    pass

            modules = list(
                set(
                    Path(f).parent.as_posix().replace("/", ".")
                    for f in files
                    if Path(f).parent.as_posix() != "."
                )
            )

            return {
                "files": len(files),
                "lines_of_code": total_lines,
                "modules": modules[:20],
            }

        except Exception as e:
            return {"files": 0, "lines_of_code": 0, "modules": [], "error": str(e)}

    def get_coverage(self) -> Optional[float]:
        """Parse coverage from pytest output.

        Returns:
            Optional[float]: Coverage percentage or None if unavailable
        """
        result = self.run_tests()

        if result["status"] == "error":
            return None

        output = result.get("output", "")

        coverage_match = re.search(r"Coverage:\s+(\d+\.?\d*)%", output)

        if coverage_match:
            return float(coverage_match.group(1))

        return None
