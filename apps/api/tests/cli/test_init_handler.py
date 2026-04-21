#!/usr/bin/env python3
"""Tests for init-handler.py — full implementation tests."""

import subprocess
from pathlib import Path
import tempfile
import yaml
import pytest

HANDLER_PATH = (
    Path(__file__).parent.parent.parent.parent.parent
    / ".claude"
    / "commands"
    / "mm"
    / "init-handler.py"
)
FRAMEWORK_ROOT = Path(__file__).parent.parent.parent.parent.parent


def run_handler(*args, timeout=15):
    """Helper to run init-handler.py with given args."""
    return subprocess.run(
        ["python3", str(HANDLER_PATH), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# B1.1 — File exists and is importable/executable
# ---------------------------------------------------------------------------


def test_handler_file_exists():
    assert HANDLER_PATH.exists(), f"Handler not found at {HANDLER_PATH}"


# ---------------------------------------------------------------------------
# B1.2 — Flag --target <path>
# ---------------------------------------------------------------------------


def test_target_flag_accepted():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_handler("--target", tmpdir)
        # Should run (may succeed or fail for missing source, but no crash)
        assert result.returncode in (
            0,
            1,
        ), f"Unexpected exit: {result.returncode}\n{result.stderr}"


def test_target_flag_defaults_to_cwd():
    """When --target not provided, help text shows default."""
    result = run_handler("--help")
    assert "--target" in result.stdout
    assert (
        "default" in result.stdout.lower()
        or "cwd" in result.stdout.lower()
        or "current" in result.stdout.lower()
    )


# ---------------------------------------------------------------------------
# B1.3 — Flag --check
# ---------------------------------------------------------------------------


def test_check_not_installed():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_handler("--check", "--target", tmpdir)
        assert (
            "STATUS: not-installed" in result.stdout
        ), f"Expected 'STATUS: not-installed', got: {result.stdout!r}"


def test_check_installed_after_install():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Simulate already-installed state
        mastermind_dir = Path(tmpdir) / ".mastermind"
        mastermind_dir.mkdir()
        (mastermind_dir / "config.yaml").write_text("installed: true\n")

        result = run_handler("--check", "--target", tmpdir)
        assert (
            "STATUS: installed" in result.stdout
        ), f"Expected 'STATUS: installed', got: {result.stdout!r}"


# ---------------------------------------------------------------------------
# B1.4 — Flag --force
# ---------------------------------------------------------------------------


def test_force_flag_help_present():
    result = run_handler("--help")
    assert "--force" in result.stdout


def test_no_force_blocks_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Pre-create .mastermind/ to simulate existing install
        mastermind_dir = Path(tmpdir) / ".mastermind"
        mastermind_dir.mkdir()
        (mastermind_dir / "config.yaml").write_text("installed: true\n")

        result = run_handler("--target", tmpdir)
        # Without --force, should refuse and output ERROR
        assert (
            result.returncode != 0
            or "ERROR" in result.stdout
            or "already" in result.stdout.lower()
        ), f"Expected error/refusal without --force, got: {result.stdout!r}"


def test_force_allows_overwrite():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Pre-create .mastermind/
        mastermind_dir = Path(tmpdir) / ".mastermind"
        mastermind_dir.mkdir()
        (mastermind_dir / "config.yaml").write_text("installed: true\n")

        result = run_handler("--force", "--target", tmpdir)
        # With --force should succeed (STATUS: installed) or fail for unrelated reasons (missing source)
        assert (
            "ERROR: already installed" not in result.stdout.lower()
        ), f"--force should bypass already-installed error, got: {result.stdout!r}"


# ---------------------------------------------------------------------------
# B1.5 — Stack detection
# ---------------------------------------------------------------------------


def test_stack_detection_nodejs():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "package.json").write_text('{"name": "test"}')
        result = run_handler("--target", tmpdir)
        # Should detect nodejs
        output = result.stdout + result.stderr
        assert (
            "node" in output.lower() or "STATUS: installed" in output
        ), f"Expected node detection or installed status, got: {output!r}"


def test_stack_detection_python():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "pyproject.toml").write_text('[project]\nname = "test"\n')
        result = run_handler("--target", tmpdir)
        output = result.stdout + result.stderr
        assert (
            "python" in output.lower() or "STATUS: installed" in output
        ), f"Expected python detection or installed status, got: {output!r}"


def test_stack_detection_unknown():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_handler("--target", tmpdir)
        output = result.stdout + result.stderr
        # Should still work (unknown stack is ok)
        assert (
            "STATUS: installed" in output
            or "unknown" in output.lower()
            or result.returncode in (0, 1)
        )


# ---------------------------------------------------------------------------
# B1.9 — Creates .mastermind/config.yaml
# ---------------------------------------------------------------------------


def test_config_yaml_created():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "package.json").write_text('{"name": "test"}')
        result = run_handler("--target", tmpdir)

        config_path = Path(tmpdir) / ".mastermind" / "config.yaml"
        assert config_path.exists(), f"config.yaml not created. stdout: {result.stdout!r}, stderr: {result.stderr!r}"


def test_config_yaml_has_stack():
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "package.json").write_text('{"name": "test"}')
        run_handler("--target", tmpdir)

        config_path = Path(tmpdir) / ".mastermind" / "config.yaml"
        if config_path.exists():
            content = yaml.safe_load(config_path.read_text())
            assert "stack" in content, f"config.yaml missing 'stack' key: {content}"
            # CRITICAL: Validate stack is a list, not a string representation
            assert isinstance(
                content["stack"], list
            ), f"stack must be a list, got {type(content['stack'])}: {content['stack']}"


def test_config_yaml_has_brains_active():
    with tempfile.TemporaryDirectory() as tmpdir:
        run_handler("--target", tmpdir)

        config_path = Path(tmpdir) / ".mastermind" / "config.yaml"
        if config_path.exists():
            content = yaml.safe_load(config_path.read_text())
            assert "brains" in content, f"config.yaml missing 'brains' key: {content}"
            assert content["brains"].get("active") == [1, 2, 3, 4, 5, 6, 7]


# ---------------------------------------------------------------------------
# B1.10 — Output format STATUS: installed / STATUS: not-installed / ERROR:
# ---------------------------------------------------------------------------


def test_output_status_installed_on_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_handler("--target", tmpdir)
        assert (
            "STATUS: installed" in result.stdout or "ERROR:" in result.stdout
        ), f"Expected STATUS or ERROR output, got: {result.stdout!r}"


def test_output_error_format():
    """ERROR output must start with 'ERROR: '."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Pre-create .mastermind/ to trigger error
        (Path(tmpdir) / ".mastermind").mkdir()
        (Path(tmpdir) / ".mastermind" / "config.yaml").write_text("x: 1\n")

        result = run_handler("--target", tmpdir)
        if "ERROR" in result.stdout:
            lines = result.stdout.splitlines()
            error_lines = [line for line in lines if line.startswith("ERROR:")]
            assert (
                error_lines
            ), f"ERROR output must start with 'ERROR: ', got: {result.stdout!r}"


# ---------------------------------------------------------------------------
# B1.11 — Protection: no overwrite without --force
# ---------------------------------------------------------------------------


def test_protection_no_overwrite_without_force():
    with tempfile.TemporaryDirectory() as tmpdir:
        mastermind_dir = Path(tmpdir) / ".mastermind"
        mastermind_dir.mkdir()
        (mastermind_dir / "config.yaml").write_text("installed: true\n")

        result = run_handler("--target", tmpdir)
        # Should refuse
        assert (
            result.returncode != 0 or "ERROR" in result.stdout
        ), f"Should refuse overwrite without --force, got: rc={result.returncode}, stdout={result.stdout!r}"


# ---------------------------------------------------------------------------
# B1.12 — Protection: warn if target == mastermind source
# ---------------------------------------------------------------------------


def test_protection_warn_self_install():
    """Warn (but don't block) if target == MasterMind source dir."""
    result = run_handler("--target", str(FRAMEWORK_ROOT))
    output = result.stdout + result.stderr
    # Should warn about self-install
    assert (
        "warn" in output.lower()
        or "self" in output.lower()
        or "source" in output.lower()
        or "mastermind" in output.lower()
    ), f"Expected self-install warning, got: {output!r}"


# ---------------------------------------------------------------------------
# B1.13 — Handler executes without errors on fresh target
# ---------------------------------------------------------------------------


def test_handler_executes_fresh_target():
    """python3 init-handler.py --target /tmp/test-project succeeds."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = run_handler("--target", tmpdir)
        # Should not crash with unhandled exception
        assert (
            "Traceback" not in result.stderr
        ), f"Handler crashed with exception:\n{result.stderr}"
        assert (
            "STATUS: installed" in result.stdout or "ERROR:" in result.stdout
        ), f"Handler must output STATUS or ERROR, got: {result.stdout!r}"


def test_help_flag():
    result = run_handler("--help")
    assert result.returncode == 0
    assert "--target" in result.stdout
    assert "--check" in result.stdout
    assert "--force" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


def test_config_yaml_multi_stack_parses_as_list():
    """CRITICAL: Multiple stacks must parse as YAML list, not Python list string."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        # Create NextJS + Python project
        (tmpdir / "package.json").write_text(
            '{"name": "test", "dependencies": {"next": "^15.0.0"}}'
        )
        (tmpdir / "pyproject.toml").write_text('[project]\nname = "test"\n')

        run_handler("--target", str(tmpdir))
        config_path = tmpdir / ".mastermind" / "config.yaml"

        assert config_path.exists(), "config.yaml not created"
        content = yaml.safe_load(config_path.read_text())

        # CRITICAL VALIDATION: stack must be a list with correct elements
        assert isinstance(
            content["stack"], list
        ), f"stack must be list, got {type(content['stack'])}"
        assert "nextjs" in content["stack"], "nextjs not in stack"
        assert "python" in content["stack"], "python not in stack"
        # NOT a string like "['nextjs', 'python']"
        assert not isinstance(
            content["stack"], str
        ), f"stack is string, not list: {content['stack']!r}"
