#!/usr/bin/env python3
"""Legacy compatibility stub for the retired /mm:ship workflow."""

from __future__ import annotations


def main() -> None:
    """Explain that /mm:ship is deprecated for the objective-package workflow."""
    print("STATUS: FAILED")
    print("- `/mm:ship` is deprecated for this repository.")
    print("- Close completed work with: /mm:archive-objective")
    print("- Then continue with:")
    print("  1. /mm:discover --roadmap --existing")
    print("  2. /mm:activate-next-objective")
    print("  3. /mm:discover-contract-check --objective <slug>")
    print("  4. /mm:complete-task <TASK_ID> --brief")


if __name__ == "__main__":
    main()
