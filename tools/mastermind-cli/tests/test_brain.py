"""Tests for brain commands."""

import pytest


def test_project_root_detection():
    """Test project root detection."""
    from mastermind_cli.commands.brain import get_project_root
    from pathlib import Path

    root = get_project_root()

    # Should find CLAUDE.md or similar markers
    assert isinstance(root, Path)
    assert root.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
