#!/usr/bin/env python3
"""Compatibility wrapper for runtimes expecting a dashed safe-commit handler name."""

from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    target = Path(__file__).with_name("safe_commit_handler.py")
    runpy.run_path(str(target), run_name="__main__")
