"""Rust project analysis strategy."""

import subprocess
import re
from typing import Optional
from .base import ProjectStrategy


class RustStrategy(ProjectStrategy):
    """Analysis strategy for Rust projects."""

    def validate(self) -> tuple[bool, Optional[str]]:
        """Check if cargo is available.

        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        try:
            result = subprocess.run(
                ["cargo", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0:
                return False, "cargo not available"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, "cargo not found"

        return True, None

    def run_tests(self) -> dict:
        """Run cargo test and parse results.

        Returns:
            dict: Test results with status, passing, failing counts
        """
        try:
            result = subprocess.run(
                ["cargo", "test"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.root,
            )

            output = result.stdout + result.stderr

            # Parse test results
            passing = re.search(r"test result: ok\. (\d+) passed", output)
            failing = re.search(r"test result: FAILED\. (\d+) failed", output)

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
        try:
            result = subprocess.run(
                ["cargo", "outdated"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.root,
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

        except Exception:
            # cargo outdated might not be installed
            return {
                "status": "skipped",
                "reason": "cargo outdated not installed",
                "outdated": 0,
            }

    def analyze_code(self) -> dict:
        """Analyze Rust code structure.

        Returns:
            dict: Code metrics with file count, lines of code
        """
        try:
            result = subprocess.run(
                ["fd", "-e", "rs", ".", str(self.root)],
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
        """Rust coverage requires tarpaulin - return None for now.

        Returns:
            Optional[float]: None (coverage not implemented)
        """
        return None
