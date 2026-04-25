"""
Tests for verify-criteria-handler.py — acceptance criteria verification.

These tests use TDD methodology:
1. Test TODO parsing and verification
2. Test handler execution verification
3. Test skill existence checking
4. Test integration flow (TODOs first, then functional verification)
5. Test error handling and edge cases
"""

import importlib.util
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add handler to path (go up to repo root)
handler_file = (
    Path(__file__).resolve().parents[4]
    / ".claude"
    / "commands"
    / "mm"
    / "verify-criteria-handler.py"
)

# Load module from file (filename has hyphens, can't use normal import)
try:
    spec = importlib.util.spec_from_file_location(
        "verify_criteria_handler", handler_file
    )
    verify_criteria_handler = importlib.util.module_from_spec(spec)
    sys.modules["verify_criteria_handler"] = verify_criteria_handler
    spec.loader.exec_module(verify_criteria_handler)

    # Extract functions for easier access
    get_todos_for_task = verify_criteria_handler.get_todos_for_task
    verify_todos_completed = verify_criteria_handler.verify_todos_completed
    verify_handler_executes = verify_criteria_handler.verify_handler_executes
    verify_skill_exists = verify_criteria_handler.verify_skill_exists
    mm_info = verify_criteria_handler.mm_info
    mm_verify = verify_criteria_handler.mm_verify
    mm_error = verify_criteria_handler.mm_error
    mm_warn = verify_criteria_handler.mm_warn
    PROJECT_ROOT = verify_criteria_handler.PROJECT_ROOT
    PLAN_MD = verify_criteria_handler.PLAN_MD
    TODO_MD = verify_criteria_handler.TODO_MD
except (FileNotFoundError, ImportError):
    pytest.skip(
        "verify-criteria-handler.py not found or not implemented yet",
        allow_module_level=True,
    )


class TestTODOParsing:
    """Test TODO parsing from todo.md."""

    def test_get_todos_for_empty_task(self):
        """Empty task section should return empty list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## C1\n\n## C2\n")
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                todos = get_todos_for_task("C1")
                assert todos == []
        finally:
            temp_path.unlink()

    def test_get_todos_parse_checkboxes(self):
        """Should parse checkbox status correctly."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                "## C1\n"
                "- [x] First completed task\n"
                "- [ ] Second pending task\n"
                "- [x] Third completed task\n"
            )
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                todos = get_todos_for_task("C1")
                assert len(todos) == 3
                assert todos[0] == (1, "First completed task", True)
                assert todos[1] == (2, "Second pending task", False)
                assert todos[2] == (3, "Third completed task", True)
        finally:
            temp_path.unlink()

    def test_get_todos_with_task_name(self):
        """Should parse task with name after ID."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## C1: Crear handler\n" "- [ ] Task one\n" "- [x] Task two\n")
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                todos = get_todos_for_task("C1")
                assert len(todos) == 2
                assert todos[0][1] == "Task one"
                assert todos[1][1] == "Task two"
        finally:
            temp_path.unlink()

    def test_get_todos_stops_at_next_task(self):
        """Should not include TODOs from next task section."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## C1\n" "- [x] C1 task\n" "## C2\n" "- [ ] C2 task\n")
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                todos = get_todos_for_task("C1")
                assert len(todos) == 1
                assert todos[0][1] == "C1 task"
        finally:
            temp_path.unlink()


class TestTODOVerification:
    """Test TODO completion verification."""

    def test_verify_all_todos_completed_returns_true(self):
        """All TODOs completed should return True."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## C1\n" "- [x] Task 1\n" "- [x] Task 2\n")
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                result = verify_todos_completed("C1")
                assert result is True
        finally:
            temp_path.unlink()

    def test_verify_incomplete_todos_returns_false(self):
        """Incomplete TODOs should return False."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## C1\n" "- [x] Task 1\n" "- [ ] Task 2\n")
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                result = verify_todos_completed("C1")
                assert result is False
        finally:
            temp_path.unlink()

    def test_verify_no_todos_returns_true(self):
        """Task with no TODOs should return True (not an error)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## C1\n\n")
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                result = verify_todos_completed("C1")
                assert result is True
        finally:
            temp_path.unlink()

    def test_verify_missing_file_returns_true(self):
        """Missing todo.md should return True (graceful degradation)."""
        with patch.object(
            verify_criteria_handler, "TODO_MD", Path("/nonexistent/file.md")
        ):
            result = verify_todos_completed("C1")
            assert result is True


class TestHandlerExecution:
    """Test handler execution verification."""

    @patch("subprocess.run")
    def test_verify_handler_executes_success(self, mock_run):
        """Handler that executes should return True."""
        mock_run.return_value = Mock(returncode=0, stdout="MODE: test", stderr="")

        result = verify_handler_executes("review-handler.py")
        assert result is True

    @patch("subprocess.run")
    def test_verify_handler_timeout_returns_false(self, mock_run):
        """Handler timeout should return False."""
        from subprocess import TimeoutExpired

        mock_run.side_effect = TimeoutExpired("python3", 5)

        result = verify_handler_executes("review-handler.py")
        assert result is False

    @patch("subprocess.run")
    def test_verify_handler_produces_valid_output(self, mock_run):
        """Handler with MODE in output should pass even with non-zero exit."""
        mock_run.return_value = Mock(
            returncode=1, stdout="MODE: uncommitted\nSCOPE: test", stderr=""
        )

        result = verify_handler_executes("review-handler.py")
        assert result is True


class TestSkillExistence:
    """Test skill file existence checking."""

    def test_verify_skill_exists_returns_true(self):
        """Existing skill should return True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create skill directory structure
            skill_path = Path(tmpdir) / ".claude" / "skills" / "mm" / "review"
            skill_path.mkdir(parents=True)
            (skill_path / "SKILL.md").touch()

            with patch.object(verify_criteria_handler, "PROJECT_ROOT", Path(tmpdir)):
                result = verify_skill_exists("review")
                assert result is True

    def test_verify_skill_missing_returns_false(self):
        """Missing skill should return False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Don't create the skill file
            with patch.object(verify_criteria_handler, "PROJECT_ROOT", Path(tmpdir)):
                result = verify_skill_exists("nonexistent")
                assert result is False


class TestHelperFunctions:
    """Test helper and utility functions."""

    def test_mm_info_prints_message(self, capsys):
        """mm_info should print formatted info message."""
        mm_info("Test info message")
        captured = capsys.readouterr()
        assert "INFO:" in captured.out
        assert "Test info message" in captured.out

    def test_mm_verify_prints_message(self, capsys):
        """mm_verify should print formatted verify message."""
        mm_verify("Test verify message")
        captured = capsys.readouterr()
        assert "VERIFY:" in captured.out
        assert "Test verify message" in captured.out

    def test_mm_error_prints_message(self, capsys):
        """mm_error should print formatted error message to stderr."""
        mm_error("Test error message")
        captured = capsys.readouterr()
        assert "ERROR:" in captured.err
        assert "Test error message" in captured.err

    def test_mm_warn_prints_message(self, capsys):
        """mm_warn should print formatted warning message."""
        mm_warn("Test warning message")
        captured = capsys.readouterr()
        assert "WARN:" in captured.out
        assert "Test warning message" in captured.out


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_todo_file(self):
        """Empty todo.md should not crash."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("")
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                todos = get_todos_for_task("C1")
                assert todos == []
        finally:
            temp_path.unlink()

    def test_malformed_checkbox_ignored(self):
        """Malformed checkboxes should be ignored."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                "## C1\n"
                "- [x] Valid task\n"
                "- malformed task\n"
                "- [ ] Another valid task\n"
            )
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                todos = get_todos_for_task("C1")
                assert len(todos) == 2
        finally:
            temp_path.unlink()

    def test_trailing_whitespace_in_todos(self):
        """TODOs with trailing whitespace should be trimmed."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## C1\n" "- [x] Task with spaces   \n")
            temp_path = Path(f.name)

        try:
            with patch.object(verify_criteria_handler, "TODO_MD", temp_path):
                todos = get_todos_for_task("C1")
                assert todos[0][1] == "Task with spaces"
        finally:
            temp_path.unlink()
