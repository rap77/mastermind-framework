"""Node.js project analysis strategy."""

import subprocess
import re
from typing import Optional
from .base import ProjectStrategy


class NodeStrategy(ProjectStrategy):
    """Analysis strategy for Node.js projects."""

    def validate(self) -> tuple[bool, Optional[str]]:
        """Check if Node tooling is available.

        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        pkg_manager = self.structure.get("package_manager", "npm")

        try:
            result = subprocess.run(
                [pkg_manager, "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False, f"{pkg_manager} not available"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, f"{pkg_manager} not found"

        return True, None

    def run_tests(self) -> dict:
        """Run tests and parse results.

        Returns:
            dict: Test results with status, passing, failing, skipped counts
        """
        pkg_manager = self.structure.get("package_manager", "npm")

        # Try common test scripts
        if pkg_manager == "pnpm":
            cmd = [pkg_manager, "test", "--", "--run"]
        else:
            cmd = [pkg_manager, "test"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.root,
                shell=True,
            )

            output = result.stdout + result.stderr

            # Parse test results (works for vitest, jest)
            passing = re.search(r"(\d+) pass", output) or re.search(
                r"✓\s+(\d+)", output
            )
            failing = re.search(r"(\d+) fail", output) or re.search(
                r"✗\s+(\d+)", output
            )

            return {
                "status": "success" if result.returncode == 0 else "error",
                "passing": int(passing.group(1)) if passing else 0,
                "failing": int(failing.group(1)) if failing else 0,
                "skipped": 0,
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
        pkg_manager = self.structure.get("package_manager", "npm")

        cmd = [pkg_manager, "outdated"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.root,
                shell=True,
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
        """Analyze TypeScript/JavaScript code structure.

        Returns:
            dict: Code metrics with file count, lines of code
        """
        try:
            # Find TS/JS files
            result = subprocess.run(
                [
                    "fd",
                    "-e",
                    "ts",
                    "-e",
                    "tsx",
                    "-e",
                    "js",
                    "-e",
                    "jsx",
                    ".",
                    str(self.root),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            files = [f for f in result.stdout.strip().split("\n") if f]

            # Count lines
            total_lines = 0
            for file_path in files[:50]:  # Limit to 50 files for speed
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

            return {"files": len(files), "lines_of_code": total_lines, "modules": []}

        except Exception as e:
            return {"files": 0, "lines_of_code": 0, "modules": [], "error": str(e)}

    def get_coverage(self) -> Optional[float]:
        """Parse coverage from test output.

        Returns:
            Optional[float]: Coverage percentage or None if unavailable
        """
        result = self.run_tests()
        output = result.get("output", "")

        # Look for coverage in output
        coverage_match = re.search(r"(\d+\.?\d*)%\s*coverage", output)

        if coverage_match:
            return float(coverage_match.group(1))

        return None
