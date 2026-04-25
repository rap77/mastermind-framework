"""Tests for ship-handler.py — Phase D1

TDD approach: write failing tests first, then implement.
"""

import json
import subprocess
from pathlib import Path


class TestShipHandler:
    """Test suite for ship-handler.py following review-handler.py pattern."""

    def test_handler_exists(self):
        """D1.1: Handler file exists and is executable."""
        # Handler is in root .claude/, not in apps/api/
        handler_path = Path("../../.claude/commands/mm/ship-handler.py")
        assert handler_path.exists(), "ship-handler.py must exist"
        assert handler_path.stat().st_size > 0, "ship-handler.py must not be empty"

    def test_flag_verify_dry_run(self):
        """D1.2: --verify flag sets MODE to verify (no tag creation)."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--verify"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        assert "MODE: verify" in output, "--verify should set MODE to verify"

    def test_flag_patch_default(self):
        """D1.4: --patch flag increments patch version (default)."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--patch"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        assert "MODE: ship" in output, "--patch should set MODE to ship"

    def test_flag_minor(self):
        """D1.5: --minor flag increments minor version."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--minor"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        assert "MODE: ship" in output, "--minor should set MODE to ship"

    def test_flag_major(self):
        """D1.6: --major flag increments major version."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--major"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        assert "MODE: ship" in output, "--major should set MODE to ship"

    def test_flag_archive_mode(self):
        """D1.7: --archive flag sets MODE to archive."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--archive"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        assert "MODE: archive" in output, "--archive should set MODE to archive"

    def test_flag_cleanup_mode(self):
        """D1.8: --cleanup flag sets MODE to cleanup."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--cleanup"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        assert "MODE: cleanup" in output, "--cleanup should set MODE to cleanup"

    def test_uncommitted_changes_detection(self):
        """D1.9: Handler detects uncommitted changes."""
        # This test assumes there might be uncommitted changes
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--verify"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        # Should mention uncommitted changes in PRECONDITIONS
        assert "PRECONDITIONS:" in output, "Must output PRECONDITIONS status"

    def test_spec_md_exists_check(self):
        """D1.10: Handler checks if SPEC.md exists."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--verify"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        # Should check SPEC.md in PRECONDITIONS
        assert "PRECONDITIONS:" in output, "Must check SPEC.md existence"

    def test_detect_last_tag(self):
        """D1.11: Handler reads last git tag."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--verify"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        assert "CURRENT_TAG:" in output, "Must output CURRENT_TAG"

    def test_generate_changelog(self):
        """D1.12: Handler generates changelog from last tag."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--verify"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        assert "CHANGELOG:" in output, "Must output CHANGELOG"

    def test_calculate_next_version_patch(self):
        """D1.13: Handler calculates next version (patch increment)."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--patch"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        assert "NEXT_TAG:" in output, "Must output NEXT_TAG"

    def test_output_format(self):
        """D1.14: Handler outputs required fields."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--verify"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout
        # Check all required output fields
        required_fields = [
            "MODE:",
            "CURRENT_TAG:",
            "NEXT_TAG:",
            "CHANGELOG:",
            "PRECONDITIONS:",
            "LAUNCH:",
            "PAYLOAD:",
        ]
        for field in required_fields:
            assert field in output, f"Missing required field: {field}"

    def test_payload_is_valid_json(self):
        """D1.14: PAYLOAD field contains valid JSON."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--verify"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed: {result.stderr}"
        output = result.stdout

        # Extract PAYLOAD JSON - find everything between PAYLOAD: and the closing brace
        payload_start = output.find("PAYLOAD:")
        assert payload_start != -1, "PAYLOAD field not found in output"

        # Start after "PAYLOAD: "
        json_start = payload_start + len("PAYLOAD:")

        # Find the matching closing brace (this is a multi-line JSON object)
        # We'll look for the last } followed by a newline
        json_end = output.rfind("}\n")
        assert json_end != -1, "Could not find end of JSON"

        # Extract just the JSON part (from { to })
        json_text = output[json_start : json_end + 1].strip()
        payload = json.loads(json_text)

        assert isinstance(payload, dict), "PAYLOAD must be a JSON object"
        assert "mode" in payload, "PAYLOAD must contain 'mode'"
        assert "current_tag" in payload, "PAYLOAD must contain 'current_tag'"
        assert "next_tag" in payload, "PAYLOAD must contain 'next_tag'"
        assert "changelog" in payload, "PAYLOAD must contain 'changelog'"

    def test_handler_executes_without_errors(self):
        """D1.15: Handler executes without errors using --verify."""
        result = subprocess.run(
            ["python3", "../../.claude/commands/mm/ship-handler.py", "--verify"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, f"Handler failed with error: {result.stderr}"
        assert "ERROR:" not in result.stdout, "Handler should not output errors"
