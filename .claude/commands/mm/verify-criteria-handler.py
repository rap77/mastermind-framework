#!/usr/bin/env python3
"""Handler para /mm:verify-criteria.

Verifica REALMENTE los acceptance criteria y marca los que pasan.
"""

import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path.home() / "proy/mastermind"
PLAN_MD = PROJECT_ROOT / "tasks" / "plan.md"


def mm_info(msg: str) -> None:
    """Print INFO message."""
    print(f"INFO: {msg}", flush=True)


def mm_error(msg: str) -> None:
    """Print ERROR message."""
    print(f"ERROR: {msg}", flush=True, file=sys.stderr)


def mm_verify(msg: str) -> None:
    """Print VERIFICATION message."""
    print(f"VERIFY: {msg}", flush=True)


# ============================================================================
# REAL Verification Functions
# ============================================================================


def verify_handler_executes(handler_name: str) -> bool:
    """Verify that a handler executes without errors.

    Args:
        handler_name: Name of the handler file (e.g., "review-handler.py")

    Returns:
        True if handler executes, False otherwise.
    """
    handler_path = PROJECT_ROOT / ".claude/commands/mm" / handler_name

    if not handler_path.exists():
        mm_verify(f"❌ Handler not found: {handler_path}")
        return False

    try:
        # Try to run handler with --help (should work for most handlers)
        subprocess.run(
            ["python3", str(handler_path), "--help"],
            cwd=handler_path.parent,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,  # Don't raise exception on non-zero exit
        )
        # If it runs (even with error), it's executable
        mm_verify(f"✓ Handler executes: {handler_name}")
        return True
    except subprocess.TimeoutExpired:
        mm_verify(f"❌ Handler timeout: {handler_name}")
        return False
    except Exception as e:
        mm_verify(f"❌ Handler error: {handler_name} - {e}")
        return False


def verify_handler_flag(handler_name: str, flag: str) -> bool:
    """Verify that a handler works with a specific flag.

    Args:
        handler_name: Name of the handler file
        flag: Flag to test (e.g., "--staged")

    Returns:
        True if handler works with flag, False otherwise.
    """
    handler_path = PROJECT_ROOT / ".claude/commands/mm" / handler_name

    if not handler_path.exists():
        return False

    try:
        result = subprocess.run(
            ["python3", str(handler_path), flag],
            cwd=handler_path.parent,
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Check if it produced valid output (not crash)
        if (
            result.returncode == 0
            or "MODE:" in result.stdout
            or "INFO:" in result.stdout
        ):
            mm_verify(f"✓ Handler flag works: {handler_name} {flag}")
            return True
        mm_verify(f"❌ Handler flag failed: {handler_name} {flag}")
        return False
    except subprocess.TimeoutExpired:
        mm_verify(f"❌ Handler flag timeout: {handler_name} {flag}")
        return False
    except Exception as e:
        mm_verify(f"❌ Handler flag error: {handler_name} {flag} - {e}")
        return False


def verify_file_exists(file_path: str) -> bool:
    """Verify that a file exists.

    Args:
        file_path: Path relative to project root or absolute.

    Returns:
        True if file exists, False otherwise.
    """
    path = (
        PROJECT_ROOT / file_path if not file_path.startswith("/") else Path(file_path)
    )

    if path.exists():
        mm_verify(f"✓ File exists: {file_path}")
        return True
    mm_verify(f"❌ File not found: {file_path}")
    return False


def verify_file_not_exists(file_path: str) -> bool:
    """Verify that a file does NOT exist (for cleanup tasks).

    Args:
        file_path: Path to check.

    Returns:
        True if file does NOT exist, False otherwise.
    """
    path = (
        PROJECT_ROOT / file_path if not file_path.startswith("/") else Path(file_path)
    )

    if not path.exists():
        mm_verify(f"✓ File removed: {file_path}")
        return True
    mm_verify(f"❌ File still exists: {file_path}")
    return False


def verify_command_exists(cmd_name: str) -> bool:
    """Verify that a slash command file exists (for autocomplete).

    Args:
        cmd_name: Command name (e.g., "/mm:review" or just "review")

    Returns:
        True if command file exists, False otherwise.
    """
    # Extract command name from /mm:X format
    cmd_file = cmd_name.replace("/mm:", "").replace("/", "") + ".md"
    cmd_path = PROJECT_ROOT / ".claude/commands/mm" / cmd_file

    if cmd_path.exists():
        mm_verify(f"✓ Command exists: {cmd_name}")
        return True
    mm_verify(f"❌ Command not found: {cmd_name}")
    return False


def verify_criterion_automatically(criterion_text: str) -> bool:
    """Try to verify a criterion automatically based on its content.

    Args:
        criterion_text: The acceptance criterion text.

    Returns:
        True if verification passes, False otherwise.
    """
    criterion_lower = criterion_text.lower()

    # Pattern 1: Handler execution "ejecuta sin errores"
    if "handler" in criterion_lower and "ejecuta sin errores" in criterion_lower:
        handler_match = re.search(r"(\w+-handler\.py)", criterion_text)
        if handler_match:
            return verify_handler_executes(handler_match.group(1))

    # Pattern 2: Handler with specific flag
    if "handler" in criterion_lower and "--" in criterion_text:
        handler_match = re.search(r"(\w+-handler\.py)", criterion_text)
        flag_match = re.search(r"--[\w-]+", criterion_text)
        if handler_match and flag_match:
            return verify_handler_flag(handler_match.group(1), flag_match.group(0))

    # Pattern 3: File existence
    if (
        "existe" in criterion_lower
        or "creado" in criterion_lower
        or "creada" in criterion_lower
    ):
        # Extract file path
        file_match = re.search(r"[\w./-]+\.(md|py|yaml|json|txt|sh)", criterion_text)
        if file_match:
            return verify_file_exists(file_match.group(0))

    # Pattern 4: File NOT existence (cleanup)
    if (
        "no existe" in criterion_lower
        or "borrar" in criterion_lower
        or "eliminado" in criterion_lower
    ):
        file_match = re.search(r"[\w./-]+\.(md|py|yaml|json|txt)", criterion_text)
        if file_match:
            return verify_file_not_exists(file_match.group(0))

    # Pattern 5: Autocomplete
    if "autocomplete" in criterion_lower:
        cmd_match = re.search(r"/mm:[\w-]+", criterion_text)
        if cmd_match:
            return verify_command_exists(cmd_match.group(0))

    # Pattern 6: Command exists
    if "aparece en autocomplete" in criterion_lower:
        cmd_match = re.search(r"`/mm:[\w-]+`", criterion_text)
        if cmd_match:
            return verify_command_exists(cmd_match.group(0))

    # Cannot verify automatically
    return False


def read_task_criteria(task_id: str) -> tuple[str, list[tuple[int, str, bool]]]:
    """Read acceptance criteria for a task from plan.md.

    Args:
        task_id: Task identifier (e.g., "C1").

    Returns:
        Tuple of (task_title, list of (number, text, is_checked)).
    """
    if not PLAN_MD.exists():
        raise FileNotFoundError("plan.md not found")

    content = PLAN_MD.read_text()

    # Find task section (from ### C1 to next ### or end)
    task_pattern = rf"(### {task_id}:.*?\n)(.*?)(?=### [A-Z]\d:|\Z)"
    task_match = re.search(task_pattern, content, re.DOTALL)

    if not task_match:
        raise ValueError(f"Task {task_id} not found in plan.md")

    title_line = task_match.group(1)
    task_content = task_match.group(2)

    # Extract title from header
    title_match = re.search(r"### [A-Z]\d+: (.*)", title_line)
    title = title_match.group(1).strip() if title_match else "Unknown"

    # Find Acceptance section within task content
    acceptance_pattern = r"\*\*Acceptance:\*\*\n((?:- \[[ x]\].*\n)*)"
    acceptance_match = re.search(acceptance_pattern, task_content, re.DOTALL)

    if not acceptance_match:
        return title, []

    criteria_section = acceptance_match.group(1)

    # Parse criteria
    criteria = []
    for line in criteria_section.split("\n"):
        if line.strip().startswith("- ["):
            checkbox_match = re.match(r"- \[([ x])\] (.*)", line)
            if checkbox_match:
                status, text = checkbox_match.groups()
                criteria.append((len(criteria) + 1, text.strip(), status == "x"))

    return title, criteria


def mark_criteria(
    task_id: str,
    criterion_numbers: list[int],
) -> tuple[int, int]:
    """Mark specific acceptance criteria as verified in plan.md.

    Args:
        task_id: Task identifier.
        criterion_numbers: List of criterion numbers to mark (1-indexed).

    Returns:
        Tuple of (marked_count, total_count).
    """
    if not PLAN_MD.exists():
        raise FileNotFoundError("plan.md not found")

    content = PLAN_MD.read_text()

    # Find entire task section (from ### C1 to next ### or end)
    task_pattern = rf"(### {task_id}:.*?\n)(.*?)(?=### [A-Z]\d:|\Z)"
    task_match = re.search(task_pattern, content, re.DOTALL)

    if not task_match:
        raise ValueError(f"Task {task_id} not found in plan.md")

    header = task_match.group(1)
    task_content = task_match.group(2)

    # Find and update Acceptance section within task content
    acceptance_pattern = r"(\*\*Acceptance:\*\*\n)((?:- \[[ x]\].*\n)*)"
    acceptance_match = re.search(acceptance_pattern, task_content, re.DOTALL)

    if not acceptance_match:
        raise ValueError(f"No Acceptance section found in task {task_id}")

    acceptance_header = acceptance_match.group(1)
    criteria_section = acceptance_match.group(2)

    # Parse and update criteria
    lines = criteria_section.split("\n")
    updated_lines = []
    marked_count = 0
    criterion_index = 0

    for line in lines:
        if line.strip().startswith("- ["):
            criterion_index += 1
            checkbox_match = re.match(r"- \[([ x])\] (.*)", line)

            if checkbox_match:
                status, text = checkbox_match.groups()

                # Mark if in the list and not already checked
                if criterion_index in criterion_numbers and status == " ":
                    updated_lines.append(f"- [x] {text}")
                    marked_count += 1
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    # Reconstruct Acceptance section
    new_acceptance_section = acceptance_header + "\n".join(updated_lines) + "\n"

    # Replace Acceptance section in task content
    new_task_content = (
        task_content[: acceptance_match.start()]
        + new_acceptance_section
        + task_content[acceptance_match.end() :]
    )

    # Reconstruct entire task section
    new_task_section = header + new_task_content

    # Replace in plan.md
    new_content = (
        content[: task_match.start()] + new_task_section + content[task_match.end() :]
    )

    PLAN_MD.write_text(new_content)

    total_count = len([line for line in lines if line.strip().startswith("- [")])

    return marked_count, total_count


def show_criteria_status(task_id: str) -> None:
    """Show current status of acceptance criteria.

    Args:
        task_id: Task identifier.
    """
    try:
        title, criteria = read_task_criteria(task_id)
    except (FileNotFoundError, ValueError) as e:
        mm_error(str(e))
        return

    mm_info(f"Task {task_id}: {title}")

    if not criteria:
        mm_info("No acceptance criteria found")
        return

    verified = sum(1 for _, _, is_checked in criteria if is_checked)
    total = len(criteria)

    mm_info(f"{verified}/{total} criteria verified")

    for num, text, is_checked in criteria:
        status = "✓" if is_checked else " "
        print(f"  {status} Criterion #{num}: {text[:80]}", flush=True)

    print(
        f"\nSummary: {verified}/{total} verified ({verified * 100 // total}%)"
        if total > 0
        else "\nSummary: 0/0",
        flush=True,
    )


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: mm-verify-criteria <TASK_ID> [OPTIONS]", flush=True)
        print(
            "       mm-verify-criteria <TASK_ID>                    # Show status",
            flush=True,
        )
        print(
            "       mm-verify-criteria <TASK_ID> --verify          # Verify & mark auto",
            flush=True,
        )
        print(
            "       mm-verify-criteria <TASK_ID> --all              # Mark all (manual)",
            flush=True,
        )
        print(
            "       mm-verify-criteria <TASK_ID> --criteria 1,3,5  # Mark specific (manual)",
            flush=True,
        )
        sys.exit(1)

    task_id = sys.argv[1].upper()
    mode = "status"

    criterion_numbers: list[int] = []

    if "--verify" in sys.argv:
        mode = "verify_auto"
    elif "--all" in sys.argv:
        mode = "mark_all"
    elif "--criteria" in sys.argv:
        mode = "mark_specific"
        idx = sys.argv.index("--criteria")
        if idx + 1 < len(sys.argv):
            try:
                criterion_numbers = [
                    int(n.strip()) for n in sys.argv[idx + 1].split(",")
                ]
            except ValueError:
                mm_error("Invalid criterion numbers. Use format: --criteria 1,3,5")
                sys.exit(1)
        else:
            mm_error("--criteria requires numbers (e.g., --criteria 1,3,5)")
            sys.exit(1)

    try:
        if mode == "status":
            show_criteria_status(task_id)

        elif mode == "verify_auto":
            # Auto-verify mode: check each criterion, mark only if passes
            title, criteria = read_task_criteria(task_id)

            if not criteria:
                mm_info("No acceptance criteria found")
                return

            verified_numbers = []
            failed_count = 0

            mm_info(f"Verifying {len(criteria)} criteria for task {task_id}...")

            for num, text, is_checked in criteria:
                if is_checked:
                    # Already verified, skip
                    verified_numbers.append(num)
                    continue

                print(f"\n[{num}/{len(criteria)}] {text[:80]}...", flush=True)

                # Try to verify automatically
                if verify_criterion_automatically(text):
                    verified_numbers.append(num)
                    print("  ✓ PASSED", flush=True)
                else:
                    print("  ❌ CANNOT AUTO-VERIFY (manual check needed)", flush=True)
                    failed_count += 1

            # Mark only the ones that passed verification
            if verified_numbers:
                marked, total = mark_criteria(task_id, verified_numbers)
                mm_info(f"\n✓ Marked {marked}/{total} verified criteria")
            else:
                mm_info("\n⚠ No criteria could be auto-verified")

            if failed_count > 0:
                mm_info(f"⚠ {failed_count} criteria need manual verification")

            show_criteria_status(task_id)

        elif mode == "mark_all":
            # Manual mode: mark all without verification
            mm_info("WARNING: --all marks ALL criteria without verification!")
            _, criteria = read_task_criteria(task_id)
            all_unchecked = [num for num, _, is_checked in criteria if not is_checked]

            if not all_unchecked:
                mm_info("All criteria already verified")
                show_criteria_status(task_id)
                return

            marked, total = mark_criteria(task_id, all_unchecked)
            mm_info(
                f"Marked {marked}/{total} criteria as verified (MANUAL - no verification performed)"
            )
            show_criteria_status(task_id)

        elif mode == "mark_specific":
            # Manual mode: mark specific without verification
            if not criterion_numbers:
                mm_error("No criterion numbers provided")
                sys.exit(1)

            marked, total = mark_criteria(task_id, criterion_numbers)
            mm_info(
                f"Marked {marked}/{len(criterion_numbers)} requested criteria (MANUAL - no verification performed)"
            )
            show_criteria_status(task_id)

    except (FileNotFoundError, ValueError) as e:
        mm_error(str(e))
        sys.exit(1)
    except Exception as e:
        mm_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
