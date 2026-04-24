#!/usr/bin/env python3
"""
MasterMind Review Handler

Generates code review payload for changes detection.
Supports multiple modes: uncommitted, staged, branch, files, last-commit.
"""

import argparse
import json
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for review-handler.

    Returns:
        Parsed arguments including mode flags and target files.
    """
    parser = argparse.ArgumentParser(
        description="Code review: generate diff payload for review agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 review-handler.py\n"
            "  python3 review-handler.py --staged\n"
            "  python3 review-handler.py --branch main\n"
            "  python3 review-handler.py --files path/to/file.ts path/to/other.py\n"
            "  python3 review-handler.py --last-commit\n"
        ),
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Review staged changes (git diff --staged)",
    )
    parser.add_argument(
        "--branch",
        metavar="NAME",
        help="Review changes from branch (git diff <branch>...HEAD)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        metavar="PATH",
        help="Review specific files (read directly)",
    )
    parser.add_argument(
        "--last-commit",
        action="store_true",
        help="Review last commit (git diff HEAD~1..HEAD)",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=500,
        help="Maximum diff lines to include (default: 500, 0 = unlimited)",
    )
    return parser.parse_args()


def detect_language(file_path: str) -> str:
    """Detect programming language from file extension.

    Args:
        file_path: Path to the file.

    Returns:
        Language identifier (e.g., "typescript", "python", "unknown").
    """
    ext = Path(file_path).suffix.lower()
    lang_map = {
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".py": "python",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".kt": "kotlin",
        ".swift": "swift",
        ".sh": "shell",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".md": "markdown",
        ".sql": "sql",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".xml": "xml",
    }
    return lang_map.get(ext, "unknown")


def get_git_diff(scope: str, max_lines: int = 500) -> tuple[str, list[str], int]:
    """Generate git diff for specified scope.

    Args:
        scope: Diff scope ("uncommitted", "staged", "branch", "last-commit").
        max_lines: Maximum lines to include in diff (0 = unlimited).

    Returns:
        Tuple of (diff output, list of changed files, line count).
    """
    if scope == "uncommitted":
        cmd = ["git", "diff"]
    elif scope == "staged":
        cmd = ["git", "diff", "--staged"]
    elif scope == "last-commit":
        cmd = ["git", "diff", "HEAD~1..HEAD"]
    else:
        # Branch mode handled separately
        cmd = ["git", "diff"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"ERROR: git diff failed: {result.stderr}")
            return "", [], 0

        diff_output = result.stdout

        # Extract changed files from diff
        files = []
        for line in diff_output.split("\n"):
            if line.startswith("diff --git"):
                parts = line.split()
                if len(parts) >= 4:
                    # File path is after b/ prefix
                    file_path = parts[3][2:] if parts[3].startswith("b/") else parts[3]
                    files.append(file_path)

        # Truncate diff if needed
        if max_lines > 0:
            lines = diff_output.split("\n")
            if len(lines) > max_lines:
                diff_output = "\n".join(lines[:max_lines])
                diff_output += (
                    f"\n... (truncated, showing {max_lines}/{len(lines)} lines)"
                )

        return diff_output, files, len(diff_output.split("\n"))

    except subprocess.TimeoutExpired:
        print("ERROR: git diff timed out after 30 seconds")
        return "", [], 0
    except Exception as e:
        print(f"ERROR: Failed to run git diff: {e}")
        return "", [], 0


def branch_exists(branch: str) -> bool:
    """Check if a git branch exists.

    Args:
        branch: Branch name to verify.

    Returns:
        True if branch exists, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", branch],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def get_branch_diff(branch: str, max_lines: int = 500) -> tuple[str, list[str], int]:
    """Generate git diff for branch comparison.

    Args:
        branch: Branch name to compare against.
        max_lines: Maximum lines to include in diff (0 = unlimited).

    Returns:
        Tuple of (diff output, list of changed files, line count).
    """
    # Early validation: check if branch exists
    if not branch_exists(branch):
        print(f"ERROR: Branch '{branch}' does not exist")
        print("ERROR: Available branches can be listed with: git branch -a")
        return "", [], 0

    try:
        result = subprocess.run(
            ["git", "diff", f"{branch}...HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"ERROR: git diff {branch}...HEAD failed: {result.stderr}")
            return "", [], 0

        diff_output = result.stdout

        # Extract changed files
        files = []
        for line in diff_output.split("\n"):
            if line.startswith("diff --git"):
                parts = line.split()
                if len(parts) >= 4:
                    file_path = parts[3][2:] if parts[3].startswith("b/") else parts[3]
                    files.append(file_path)

        # Truncate diff if needed
        if max_lines > 0:
            lines = diff_output.split("\n")
            if len(lines) > max_lines:
                diff_output = "\n".join(lines[:max_lines])
                diff_output += (
                    f"\n... (truncated, showing {max_lines}/{len(lines)} lines)"
                )

        return diff_output, files, len(diff_output.split("\n"))

    except subprocess.TimeoutExpired:
        print("ERROR: git diff timed out after 30 seconds")
        return "", [], 0
    except Exception as e:
        print(f"ERROR: Failed to run git diff: {e}")
        return "", [], 0


def read_files_directly(file_paths: list[str]) -> tuple[str, dict[str, str], int]:
    """Read file contents directly.

    Args:
        file_paths: List of file paths to read.

    Returns:
        Tuple of (combined content, dict of {file_path: content}, total lines).
    """
    contents = {}
    total_lines = 0

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            print(f"WARNING: File not found: {file_path}")
            continue

        try:
            content = path.read_text()
            contents[file_path] = content
            total_lines += len(content.split("\n"))
        except Exception as e:
            print(f"WARNING: Failed to read {file_path}: {e}")

    # Combine contents for display
    combined = []
    for file_path, content in contents.items():
        combined.append(f"=== {file_path} ===")
        combined.append(content)
        combined.append("")  # Blank line separator

    return "\n".join(combined), contents, total_lines


def main() -> None:
    """Generate code review payload.

    This function:
    1. Parses command-line arguments to determine review scope
    2. Generates diff or reads files based on mode
    3. Detects languages of changed files
    4. Outputs structured payload for code-reviewer agent

    Output format:
        MODE: review
        SCOPE: <scope>
        FILES: [list of files]
        LINES: <line count>
        LANGUAGES: [detected languages]
        LAUNCH: code-reviewer
        PAYLOAD: <json>
    """
    args = parse_args()

    # Determine scope
    if args.last_commit:
        scope = "last-commit"
        diff, files, line_count = get_git_diff(scope, args.max_lines)
    elif args.staged:
        scope = "staged"
        diff, files, line_count = get_git_diff(scope, args.max_lines)
    elif args.branch:
        scope = "branch"
        diff, files, line_count = get_branch_diff(args.branch, args.max_lines)
    elif args.files:
        scope = "files"
        diff, _, line_count = read_files_directly(args.files)
        files = args.files
    else:
        scope = "uncommitted"
        diff, files, line_count = get_git_diff(scope, args.max_lines)

    # Detect languages
    languages = set()
    for file_path in files:
        lang = detect_language(file_path)
        if lang != "unknown":
            languages.add(lang)

    # Build payload
    payload = {
        "scope": scope,
        "files": files,
        "diff": diff if args.files else diff,
        "line_count": line_count,
        "languages": sorted(list(languages)),
        "branch": args.branch if args.branch else None,
        "max_lines": args.max_lines,
    }

    # Output
    print("MODE: review")
    print(f"SCOPE: {scope}")
    print(f"FILES: {json.dumps(files, indent=2)}")
    print(f"LINES: {line_count}")
    print(f"LANGUAGES: {json.dumps(sorted(list(languages)), indent=2)}")
    print("LAUNCH: code-reviewer")
    print(f"PAYLOAD: {json.dumps(payload, indent=2)}")
    print()
    print(f"INFO: Reviewing {len(files)} file(s)")
    print(
        f"INFO: Languages detected: {', '.join(sorted(languages)) if languages else 'none'}"
    )


if __name__ == "__main__":
    main()
