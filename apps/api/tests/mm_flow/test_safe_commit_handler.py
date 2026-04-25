"""Tests for safe-commit-handler.py — cognitive barrier against --no-verify.

Tests are organized by functional area:
- BARRIER: --no-verify detection and prevention
- VALIDATION: Tests, GGA hook, commit message format
- INTEGRATION: End-to-end flow
"""

import subprocess
import sys
import pytest

from pathlib import Path
from unittest.mock import MagicMock, patch

# Add handler directory to path for imports BEFORE importing handler
# Path: from apps/api/tests/mm_flow/ -> go up 5 levels to project root, then .claude/commands/mm
HANDLER_DIR = (
    Path(__file__).parent.parent.parent.parent.parent / ".claude" / "commands" / "mm"
)
sys.path.insert(0, str(HANDLER_DIR))

try:
    import safe_commit_handler
except ImportError:
    pytest.skip("safe_commit_handler.py not found", allow_module_level=True)


# ------------------------------------------------------------------ #
# FIXTURES
# ------------------------------------------------------------------ #


@pytest.fixture
def git_root_dir(tmp_path: Path) -> Path:
    """Create a temporary git repository."""
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(
        ["git", "init"],
        cwd=repo_dir,
        capture_output=True,
        check=True,
    )

    # Create .pre-commit-config.yaml
    (repo_dir / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: local\n"
        "    hooks:\n"
        "      - id: test-hook\n"
        "        name: Test Hook\n"
        "        entry: echo 'test'\n"
        "        language: system\n"
    )

    return repo_dir


# ------------------------------------------------------------------ #
# BARRIER: --no-verify Detection
# ------------------------------------------------------------------ #


class TestNoVerifyBarrier:
    """Tests for --no-verify bypass detection."""

    def test_no_env_variable_bypass(self):
        """Should detect GIT_NO_VERIFY environment variable."""
        with patch.dict("os.environ", {"GIT_NO_VERIFY": "1"}):
            assert safe_commit_handler.check_no_verify_bypass() is True

    def test_no_normal_env(self):
        """Should not detect bypass without env variable."""
        with patch.dict("os.environ", {}, clear=True):
            assert safe_commit_handler.check_no_verify_bypass() is False

    @patch("safe_commit_handler.subprocess.run")
    def test_detects_dangerous_git_alias(self, mock_run: MagicMock):
        """Should detect git aliases with --no-verify."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "alias.ci commit --no-verify\n"
        mock_run.return_value = mock_result

        assert safe_commit_handler.check_no_verify_bypass() is True

    @patch("safe_commit_handler.subprocess.run")
    def test_ignores_safe_git_alias(self, mock_run: MagicMock):
        """Should ignore git aliases without --no-verify."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "alias.ci commit -m\n"
        mock_run.return_value = mock_result

        assert safe_commit_handler.check_no_verify_bypass() is False

    @patch("subprocess.run")
    @patch("sys.exit")
    def test_reverts_commit_on_bypass(self, mock_exit: MagicMock, mock_run: MagicMock):
        """Should revert commit if --no-verify detected."""
        mock_run.return_value = MagicMock(returncode=0)

        safe_commit_handler.revert_no_verify_commit()

        # Verify reset command was called
        reset_calls = [
            call
            for call in mock_run.call_args_list
            if "--soft" in str(call) and "HEAD~1" in str(call)
        ]
        assert len(reset_calls) > 0, "Expected git reset --soft HEAD~1"
        mock_exit.assert_called_with(1)


# ------------------------------------------------------------------ #
# VALIDATION: Commit Message Format
# ------------------------------------------------------------------ #


class TestCommitMessageValidation:
    """Tests for conventional commit format validation."""

    def test_valid_simple_commit(self):
        """Should accept valid simple commit."""
        valid, _ = safe_commit_handler.validate_commit_message("feat(auth): add login")
        assert valid is True

    def test_valid_commit_with_scope(self):
        """Should accept valid commit with scope."""
        valid, _ = safe_commit_handler.validate_commit_message(
            "fix(api): resolve race condition"
        )
        assert valid is True

    def test_valid_commit_with_breaking_change(self):
        """Should accept breaking change indicator."""
        valid, _ = safe_commit_handler.validate_commit_message(
            "feat!: breaking API change"
        )
        assert valid is True

    def test_rejects_empty_message(self):
        """Should reject empty commit message."""
        valid, error = safe_commit_handler.validate_commit_message("")
        assert valid is False
        assert "Empty" in error

    def test_rejects_missing_type(self):
        """Should reject message without type prefix."""
        valid, error = safe_commit_handler.validate_commit_message("Add new feature")
        assert valid is False
        assert "Invalid format" in error

    def test_rejects_invalid_type(self):
        """Should reject message with invalid type."""
        valid, error = safe_commit_handler.validate_commit_message(
            "invalid(type): message"
        )
        assert valid is False
        assert "Invalid format" in error

    def test_removes_ai_attribution(self):
        """Should remove Co-Authored-By from message."""
        message = "feat(auth): add login\n\nCo-Authored-By: AI <ai@example.com>"
        valid, cleaned = safe_commit_handler.validate_commit_message(message)
        assert valid is True
        assert "Co-Authored-By:" not in cleaned

    def test_rejects_ai_attribution_after_removal(self):
        """Should reject message with only AI attribution (invalid format)."""
        # Edge case: message is only Co-Authored-By, no conventional commit
        message = "Co-Authored-By: AI <ai@example.com>"
        valid, error = safe_commit_handler.validate_commit_message(message)
        assert valid is False
        # After removal, message is "AI <ai@example.com>" which is not valid conventional format
        assert "Invalid format" in error


# ------------------------------------------------------------------ #
# VALIDATION: GGA Hook
# ------------------------------------------------------------------ #


class TestGGAHookValidation:
    """Tests for GGA (Gentleman Guardian Angel) hook validation."""

    @patch("subprocess.run")
    def test_finds_hook_at_git_root(self, mock_run: MagicMock, tmp_path: Path):
        """Should find .pre-commit-config.yaml at git root."""
        # Mock git rev-parse
        mock_run.return_value.stdout = str(tmp_path)

        # Create the hook file
        (tmp_path / ".pre-commit-config.yaml").touch()

        valid, message = safe_commit_handler.check_gga_hook()
        assert valid is True
        assert "configured" in message.lower()

    @patch("subprocess.run")
    def test_rejects_missing_hook(self, mock_run: MagicMock, tmp_path: Path):
        """Should reject when .pre-commit-config.yaml missing."""
        mock_run.return_value.stdout = str(tmp_path)

        # Don't create the hook file

        valid, message = safe_commit_handler.check_gga_hook()
        assert valid is False
        assert "not configured" in message.lower()

    @patch("subprocess.run")
    def test_handles_git_root_failure(self, mock_run: MagicMock):
        """Should handle git rev-parse failure gracefully."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        valid, message = safe_commit_handler.check_gga_hook()
        assert valid is False
        assert "git root" in message.lower()


# ------------------------------------------------------------------ #
# VALIDATION: Tests (Mocked)
# ------------------------------------------------------------------ #


class TestBackendTests:
    """Tests for backend test validation."""

    @patch("safe_commit_handler.subprocess.run")
    def test_backend_tests_passing(
        self,
        mock_run: MagicMock,
        tmp_path: Path,
    ):
        """Should accept when all backend tests pass."""
        # First call: git rev-parse, Second call: pytest
        git_result = MagicMock()
        git_result.stdout = str(tmp_path)
        git_result.returncode = 0

        pytest_result = MagicMock()
        pytest_result.stdout = "=========== 100 passed in 5s ==========="
        pytest_result.stderr = ""
        pytest_result.returncode = 0

        mock_run.side_effect = [git_result, pytest_result]

        # Create apps/api directory
        (tmp_path / "apps" / "api").mkdir(parents=True)

        passed, _ = safe_commit_handler.check_backend_tests()
        assert passed is True

    @patch("safe_commit_handler.subprocess.run")
    def test_backend_tests_failing(
        self,
        mock_run: MagicMock,
        tmp_path: Path,
    ):
        """Should reject when backend tests fail."""
        # First call: git rev-parse, Second call: pytest
        git_result = MagicMock()
        git_result.stdout = str(tmp_path)
        git_result.returncode = 0

        pytest_result = MagicMock()
        pytest_result.stdout = "====== 98 passed, 2 failed in 5s ======"
        pytest_result.stderr = ""
        pytest_result.returncode = 0

        mock_run.side_effect = [git_result, pytest_result]

        (tmp_path / "apps" / "api").mkdir(parents=True)

        passed, output = safe_commit_handler.check_backend_tests()
        assert passed is False
        assert "failed" in output

    def test_no_backend_project(self, tmp_path: Path):
        """Should pass when no backend project exists."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = str(tmp_path)

            passed, message = safe_commit_handler.check_backend_tests()
            assert passed is True
            assert "No backend" in message


class TestFrontendTests:
    """Tests for frontend test validation."""

    @patch("subprocess.run")
    def test_frontend_tests_passing(
        self,
        mock_run: MagicMock,
        tmp_path: Path,
    ):
        """Should accept when all frontend tests pass."""
        # Mock git rev-parse
        mock_run.return_value.stdout = str(tmp_path)

        # Mock pnpm test run
        pnpm_result = MagicMock()
        pnpm_result.stdout = "Test Files  50 passed (50)"
        pnpm_result.returncode = 0

        with patch.object(
            safe_commit_handler.subprocess,
            "run",
            return_value=pnpm_result,
        ):
            (tmp_path / "apps" / "web").mkdir(parents=True)
            passed, _ = safe_commit_handler.check_frontend_tests()
            assert passed is True

    def test_no_frontend_project(self, tmp_path: Path):
        """Should pass when no frontend project exists."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = str(tmp_path)

            passed, message = safe_commit_handler.check_frontend_tests()
            assert passed is True
            assert "No frontend" in message


# ------------------------------------------------------------------ #
# INTEGRATION: Check Mode
# ------------------------------------------------------------------ #


class TestCheckMode:
    """Tests for --check mode (dry-run)."""

    @patch("safe_commit_handler.check_frontend_tests")
    @patch("safe_commit_handler.check_backend_tests")
    @patch("safe_commit_handler.check_gga_hook")
    @patch("safe_commit_handler.check_no_verify_bypass")
    @patch("sys.exit")
    def test_check_mode_all_pass(
        self,
        mock_exit: MagicMock,
        mock_no_verify: MagicMock,
        mock_gga: MagicMock,
        mock_backend: MagicMock,
        mock_frontend: MagicMock,
    ):
        """Should exit 0 when all checks pass."""
        mock_no_verify.return_value = False
        mock_backend.return_value = (True, "OK")
        mock_frontend.return_value = (True, "OK")
        mock_gga.return_value = (True, "OK")

        args = MagicMock(check=True, fix=False, message=None)
        safe_commit_handler.run_check_mode(args)

        mock_exit.assert_called_with(0)

    @patch("safe_commit_handler.check_frontend_tests")
    @patch("safe_commit_handler.check_backend_tests")
    @patch("safe_commit_handler.check_gga_hook")
    @patch("safe_commit_handler.check_no_verify_bypass")
    @patch("sys.exit")
    def test_check_mode_backend_fails(
        self,
        mock_exit: MagicMock,
        mock_no_verify: MagicMock,
        mock_gga: MagicMock,
        mock_backend: MagicMock,
        mock_frontend: MagicMock,
    ):
        """Should exit 1 when backend tests fail."""
        mock_no_verify.return_value = False
        mock_backend.return_value = (False, "Tests failed")
        mock_frontend.return_value = (True, "OK")
        mock_gga.return_value = (True, "OK")

        args = MagicMock(check=True, fix=False, message=None)
        safe_commit_handler.run_check_mode(args)

        mock_exit.assert_called_with(1)


# ------------------------------------------------------------------ #
# INTEGRATION: Commit Mode
# ------------------------------------------------------------------ #


class TestCommitMode:
    """Tests for actual commit mode."""

    @patch("safe_commit_handler.run_gga_validation")
    @patch("safe_commit_handler.validate_commit_message")
    @patch("safe_commit_handler.check_gga_hook")
    @patch("safe_commit_handler.check_frontend_tests")
    @patch("safe_commit_handler.check_backend_tests")
    @patch("safe_commit_handler.check_no_verify_bypass")
    @patch("subprocess.run")
    @patch("sys.exit")
    def test_commit_mode_success(
        self,
        mock_exit: MagicMock,
        mock_git: MagicMock,
        mock_no_verify: MagicMock,
        mock_backend: MagicMock,
        mock_frontend: MagicMock,
        mock_gga: MagicMock,
        mock_validate_msg: MagicMock,
        mock_gga_run: MagicMock,
    ):
        """Should successfully commit when all validations pass."""
        mock_no_verify.return_value = False
        mock_backend.return_value = (True, "OK")
        mock_frontend.return_value = (True, "OK")
        mock_gga.return_value = (True, "OK")
        mock_gga_run.return_value = (True, "OK")
        mock_validate_msg.return_value = (True, "feat(test): add test")
        mock_git.return_value = MagicMock(returncode=0)

        args = MagicMock(check=False, fix=False, message="feat(test): add test")
        safe_commit_handler.run_commit_mode(args)

        # Verify git commit was called
        commit_calls = [
            call
            for call in mock_git.call_args_list
            if len(call[0]) > 0 and "commit" in str(call[0][0])
        ]
        assert len(commit_calls) > 0, "Expected git commit call"
        mock_exit.assert_called_with(0)

    @patch("safe_commit_handler.check_no_verify_bypass")
    @patch("sys.exit")
    def test_commit_mode_reverts_no_verify(
        self,
        mock_exit: MagicMock,
        mock_no_verify: MagicMock,
    ):
        """Should revert commit if --no-verify detected."""
        mock_no_verify.return_value = True

        with patch.object(
            safe_commit_handler,
            "revert_no_verify_commit",
        ) as mock_revert:
            args = MagicMock(check=False, fix=False, message=None)
            safe_commit_handler.run_commit_mode(args)

            mock_revert.assert_called_once()


# ------------------------------------------------------------------ #
# INTEGRATION: GGA Validation
# ------------------------------------------------------------------ #


class TestGGAValidation:
    """Tests for GGA pre-commit validation."""

    @patch("subprocess.run")
    def test_gga_validation_passes(self, mock_run: MagicMock, tmp_path: Path):
        """Should accept when GGA validation passes."""
        # Mock git rev-parse
        mock_run.return_value.stdout = str(tmp_path)
        mock_run.return_value.returncode = 0

        passed, _ = safe_commit_handler.run_gga_validation()
        assert passed is True

    @patch("safe_commit_handler.subprocess.run")
    def test_gga_validation_fails(self, mock_run: MagicMock, tmp_path: Path):
        """Should reject when GGA validation fails."""

        # Mock git rev-parse and pre-commit run
        def side_effect(*args, **kwargs):
            result = MagicMock()
            if "rev-parse" in str(args[0]):
                result.stdout = str(tmp_path)
                result.returncode = 0
            else:
                # pre-commit run failed
                result.stdout = "GGA validation failed"
                result.stderr = "Some checks failed"
                result.returncode = 1
            return result

        mock_run.side_effect = side_effect

        passed, output = safe_commit_handler.run_gga_validation()
        assert passed is False
        # output should be a string, check if "failed" is in it
        assert isinstance(output, str) and "failed" in output.lower()

    @patch("subprocess.run")
    def test_gga_with_fix_flag(self, mock_run: MagicMock, tmp_path: Path):
        """Should include --fix-mode when fix=True."""
        mock_run.return_value.stdout = str(tmp_path)
        mock_run.return_value.returncode = 0

        safe_commit_handler.run_gga_validation(fix=True)

        # Check that --fix-mode was in the command
        for call in mock_run.call_args_list:
            if len(call[0]) > 0 and "pre-commit" in str(call[0][0]):
                assert "--fix-mode" in str(call)
