#!/usr/bin/env python3
"""
Cleanup old interviews according to retention policy.

Run this script periodically (cron) to manage storage.

Usage:
    python scripts/cleanup_interviews.py
    Or with mm CLI: mm cleanup interviews
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mastermind_cli.memory.interview_logger import InterviewLogger


def main():
    """Apply retention policy to interview logs."""
    logger = InterviewLogger(enabled=True)

    print("=" * 50)
    print("Interview Cleanup - Retention Policy")
    print("=" * 50)
    print()

    # Apply retention policy with defaults
    # - hot storage: 30 days
    # - warm storage: 90 days
    results = logger.apply_retention_policy(hot_days=30, warm_days=90)

    print("Retention Policy Applied:")
    print(f"  📦 Hot → Warm: {results['hot_to_warm']} file(s) moved")
    print(f"  📦 Warm → Cold: {results['warm_to_cold']} file(s) compressed")
    print()

    # Optional: Clean up cold storage older than 1 year
    cold_deleted = logger.cleanup_old_cold_storage(days=365)
    if cold_deleted > 0:
        print(f"  🗑️  Cold Storage: {cold_deleted} old file(s) deleted")
    print()

    print("✓ Cleanup complete!")


if __name__ == "__main__":
    main()
