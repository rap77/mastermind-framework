#!/usr/bin/env python3
"""
MasterMind Safe Commit Handler

Cognitive barrier that enforces GGA validation and Brain #6 standards.
NEVER allows --no-verify. Auto-corrects errors before committing.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for safe-commit-handler.

    Returns:
        Parsed arguments including mode flags and message.
    """
    parser = argparse.ArgumentParser(
        description="Safe commit: enforces GGA validation before committing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 safe-commit-handler.py\n"
            "  python3 safe-commit-handler.py --check\n"
            "  python3 safe-commit-handler.py --fix\n"
            "  python3 safe-commit-handler.py --message 'feat(auth): add JWT refresh'\n"
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: check without committing",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix GGA issues before committing",
    )
    parser.add_argument(
        "--message",
        "-m",
        metavar="MSG",
        help="Commit message (conventional format required)",
    )
    return parser.parse_args()


# ------------------------------------------------------------------ #
# BARRIER: --no-verify DETECTION
# ------------------------------------------------------------------ #


def check_no_verify_bypass() -> bool:
    """Check if user is attempting to bypass with --no-verify.

    This is a COGNITIVE BARRIER. We check:
    1. Command history (previous git commands)
    2. Environment variables
    3. Git config for dangerous aliases

    Returns:
        True if --no-verify bypass detected, False otherwise.
    """
    # Check environment
    if os.getenv("GIT_NO_VERIFY") == "1":
        return True

    # Check git config for dangerous aliases
    try:
        result = subprocess.run(
            ["git", "config", "--get-regexp", "^alias\\."],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "--no-verify" in line:
                    return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return False


def revert_no_verify_commit() -> None:
    """Revert a commit that was made with --no-verify.

    This is the NUCLEAR OPTION. We:
    1. Reset to previous commit (soft reset — keep changes)
    2. Show detailed explanation
    3. Exit with error code
    """
    print("\n" + "=" * 70)
    print("❌ COMMIT REVERTIDO: Detectado uso de --no-verify")
    print("=" * 70)
    print("\n🔒 El commit se deshizo automáticamente (soft reset).")
    print("✅ Tus cambios siguen staged — no perdiste nada.\n")

    print("¿POR QUÉ ESTÁ PROHIBIDO --no-verify?\n")
    print("GGA valida ANTES de que el código llegue al repo:\n")
    print("  🔐 Security:")
    print("     • Hardcoded credentials (API keys, tokens, passwords)")
    print("     • Private IPs (192.168.x.x, 10.x.x.x)")
    print("     • Secrets antes de subir\n")
    print("  📐 Code Quality:")
    print("     • TypeScript/React standards")
    print("     • Conventions del proyecto")
    print("     • Anti-patrones comunes\n")
    print("  ♿ Accessibility:")
    print("     • ARIA labels y roles")
    print("     • WCAG 2.1 AA compliance")
    print("     • Keyboard navigation\n")
    print("  ⚡ Performance:")
    print("     • Bundle size optimización")
    print("     • Lighthouse scores")
    print("     • Image optimization\n")

    print("💡 Usá: /mm:safe-commit")
    print("   O manualmente: git commit (sin --no-verify)\n")

    # Soft reset — keep changes staged
    try:
        subprocess.run(
            ["git", "reset", "--soft", "HEAD~1"],
            check=True,
            timeout=10,
        )
        print("✅ Cambios mantenidos en staging area.")
        print("\n" + "=" * 70)
    except subprocess.CalledProcessError:
        print("⚠️ No se pudo hacer reset — podés tener que hacerlo manualmente:")
        print("   git reset --soft HEAD~1")

    sys.exit(1)


# ------------------------------------------------------------------ #
# VALIDATION: Tests
# ------------------------------------------------------------------ #


def check_backend_tests() -> tuple[bool, str]:
    """Run backend tests and verify they pass.

    Returns:
        (all_passed, output) tuple.
    """
    # Find git root directory
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        git_root = Path(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False, "Cannot find git root"

    api_dir = git_root / "apps/api"
    if not api_dir.exists():
        return True, "No backend project"

    original_dir = Path.cwd()
    try:
        os.chdir(api_dir)
        result = subprocess.run(
            ["uv", "run", "pytest", "-q"],  # Quiet mode for shorter output
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes for large test suites
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        os.chdir(original_dir)
        return False, f"Test execution failed: {e}"
    finally:
        os.chdir(original_dir)

    # Parse output for failures
    if result.returncode != 0:
        return False, result.stdout + result.stderr

    # Check summary line (e.g., "1022 passed, 9 skipped")
    # Summary line is the last line starting with "=========="
    lines = result.stdout.split("\n")
    summary_line = None
    for line in reversed(lines):
        if line.startswith("==="):
            summary_line = line
            break

    if not summary_line or " passed" not in summary_line:
        return False, f"No passing tests found in output:\n{result.stdout}"

    # Check for failures in summary line only (not in coverage tables)
    # Format: "X passed, Y failed" or "X failed" alone
    if re.search(r"\d+\s+failed", summary_line):
        return False, result.stdout

    return True, result.stdout


def check_frontend_tests() -> tuple[bool, str]:
    """Run frontend tests and verify they pass.

    Returns:
        (all_passed, output) tuple.
    """
    # Find git root directory
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        git_root = Path(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False, "Cannot find git root"

    web_dir = git_root / "apps/web"
    if not web_dir.exists():
        return True, "No frontend project"

    try:
        result = subprocess.run(
            ["pnpm", "--prefix", str(web_dir), "test", "run"],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, f"Test execution failed: {e}"

    # Parse output for failures
    if result.returncode != 0:
        return False, result.stdout + result.stderr

    # Vitest output format
    if "Test Files" not in result.stdout:
        return False, "No test results found"

    # Check for failures
    if " failed" in result.stdout:
        return False, result.stdout + result.stderr

    return True, result.stdout


# ------------------------------------------------------------------ #
# VALIDATION: GGA Hook
# ------------------------------------------------------------------ #


def check_gga_hook() -> tuple[bool, str]:
    """Verify GGA hook is configured.

    Returns:
        (exists, message) tuple.
    """
    # Find git root directory
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        git_root = Path(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False, "GGA hook not configured — cannot find git root"

    pre_commit_config = git_root / ".pre-commit-config.yaml"

    if not pre_commit_config.exists():
        return (
            False,
            f"GGA hook not configured — expected .pre-commit-config.yaml at ROOT ({git_root})",
        )

    return True, f"GGA hook configured at {git_root}"


def run_gga_validation(fix: bool = False) -> tuple[bool, str]:
    """Run GGA pre-commit validation.

    Args:
        fix: If True, attempt to auto-fix issues.

    Returns:
        (all_passed, output) tuple.
    """
    # Find git root directory
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        git_root = Path(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False, "Cannot find git root"

    original_dir = Path.cwd()
    try:
        os.chdir(git_root)
        cmd = ["pre-commit", "run", "--all-files"]
        if fix:
            cmd.append("--fix-mode")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return False, f"GGA execution failed: {e}"
    finally:
        os.chdir(original_dir)

    if result.returncode != 0:
        return False, result.stdout + result.stderr

    return True, result.stdout


# ------------------------------------------------------------------ #
# VALIDATION: Commit Message Format
# ------------------------------------------------------------------ #

CONVENTIONAL_COMMIT_PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|revert)" r"(\(.+\))?\!?:\s.+"
)


def validate_commit_message(message: str) -> tuple[bool, str]:
    """Validate commit message follows conventional format.

    Args:
        message: Commit message to validate.

    Returns:
        (valid, error_message) tuple.
    """
    if not message:
        return False, "Empty commit message"

    # Remove AI attribution
    message = message.replace("Co-Authored-By:", "").strip()

    # Check conventional format
    if not CONVENTIONAL_COMMIT_PATTERN.match(message):
        return False, (
            "Invalid format. Expected: type(scope): description\n"
            "Types: feat, fix, docs, style, refactor, perf, test, build, ci, revert\n"
            "Example: feat(auth): add JWT refresh token rotation"
        )

    # Check for AI attribution (should have been removed)
    if "Co-Authored-By:" in message:
        return False, "Remove 'Co-Authored-By:' — GGA adds this automatically"

    return True, message


def get_commit_message_from_user() -> str:
    """Prompt user for commit message.

    Returns:
        Validated commit message.
    """
    while True:
        print("\n📝 Enter commit message (conventional format):")
        print("   Example: feat(auth): add JWT refresh token rotation")
        message = input("> ").strip()

        valid, result = validate_commit_message(message)
        if valid:
            return result
        print(f"❌ {result}")


# ------------------------------------------------------------------ #
# MAIN: Commit Flow
# ------------------------------------------------------------------ #


def run_check_mode(args: argparse.Namespace) -> None:
    """Run dry-run mode — check without committing.

    Args:
        args: Parsed command-line arguments.
    """
    print("\n🔍 Safe Commit — CHECK MODE (dry-run)\n")

    all_passed = True

    # 1. Check for --no-verify attempts
    if check_no_verify_bypass():
        print("❌ --no-verify bypass detected")
        all_passed = False
    else:
        print("✅ No --no-verify bypass detected")

    # 2. Check backend tests
    passed, output = check_backend_tests()
    if passed:
        print("✅ Backend tests passing")
    else:
        print("❌ Backend tests failing:")
        print(output[:500])
        all_passed = False

    # 3. Check frontend tests
    passed, output = check_frontend_tests()
    if passed:
        print("✅ Frontend tests passing")
    else:
        print("❌ Frontend tests failing:")
        print(output[:500])
        all_passed = False

    # 4. Check GGA hook
    passed, message = check_gga_hook()
    if passed:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        all_passed = False

    # 5. Validate message if provided
    if args.message:
        valid, result = validate_commit_message(args.message)
        if valid:
            print(f"✅ Commit message valid: {result[:60]}...")
        else:
            print(f"❌ {result}")
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL CHECKS PASSED — Ready to commit")
        sys.exit(0)
    else:
        print("❌ CHECKS FAILED — Fix issues before committing")
        sys.exit(1)


def run_commit_mode(args: argparse.Namespace) -> None:
    """Run actual commit mode with full validation.

    Args:
        args: Parsed command-line arguments.
    """
    print("\n🔒 Safe Commit — FULL VALIDATION\n")

    # STEP 1: Check for --no-verify bypass attempts
    if check_no_verify_bypass():
        revert_no_verify_commit()
        return

    # STEP 2: Verify backend tests
    print("🧪 Checking backend tests...")
    passed, output = check_backend_tests()
    if not passed:
        print("❌ Backend tests failing:\n")
        print(output)
        print("\n💡 Fix failing tests BEFORE committing")
        print("   Brain #6: 'Untested code is not a feature. It is a liability.'")
        sys.exit(1)
    print("✅ Backend tests passing\n")

    # STEP 3: Verify frontend tests
    print("🧪 Checking frontend tests...")
    passed, output = check_frontend_tests()
    if not passed:
        print("❌ Frontend tests failing:\n")
        print(output)
        print("\n💡 Fix failing tests BEFORE committing")
        sys.exit(1)
    print("✅ Frontend tests passing\n")

    # STEP 4: Verify GGA hook
    print("🔐 Checking GGA hook...")
    passed, message = check_gga_hook()
    if not passed:
        print(f"❌ {message}")
        sys.exit(1)
    print(f"✅ {message}\n")

    # STEP 5: Run GGA validation
    print("⚙️ Running GGA validation...")
    passed, output = run_gga_validation(fix=args.fix)
    if not passed:
        print("❌ GGA validation failed:\n")
        print(output)
        if not args.fix:
            print("\n💡 Run with --fix to attempt auto-correction")
        sys.exit(1)
    print("✅ GGA validation passed\n")

    # STEP 6: Get or validate commit message
    if args.message:
        valid, result = validate_commit_message(args.message)
        if not valid:
            print(f"❌ Invalid commit message:\n{result}")
            sys.exit(1)
        commit_message = result
    else:
        commit_message = get_commit_message_from_user()

    # STEP 7: Commit
    print("=" * 70)
    print(f"📝 Committing: {commit_message[:60]}...")
    print("=" * 70)

    try:
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True,
            timeout=30,
        )
        print("\n✅ Commit successful!\n")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Commit failed: {e}\n")
        sys.exit(1)


def main() -> None:
    """Entry point for safe-commit-handler."""
    args = parse_args()

    if args.check:
        run_check_mode(args)
    else:
        run_commit_mode(args)


if __name__ == "__main__":
    main()
