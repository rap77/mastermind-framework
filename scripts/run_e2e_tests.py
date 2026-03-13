#!/usr/bin/env python3
"""
E2E Test Runner for MasterMind Framework.

Executes test briefs against the orchestrator and validates results.
"""

import re
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def extract_brief_from_test_file(test_file: Path) -> str:
    """Extract the user brief from a test markdown file."""
    content = test_file.read_text()

    # Find the brief section - look for "## El Brief (Usuario)" or similar
    # Then extract everything until the next "##" heading
    patterns = [
        r'## El Brief \(Usuario\)\s*---\s*\n(.+?)\s*(?=##\s+\w|\Z)',
        r'## El Brief \(Usuario\)\s*\n---\s*\n(.+?)\s*(?=##|\Z)',
        r'## Brief \(Usuario\)\s*\n---\s*\n(.+?)\s*(?=##|\Z)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            brief = match.group(1).strip()
            # Remove any trailing "---" or empty lines
            brief = re.sub(r'\n---$', '', brief).strip()
            return brief

    # Fallback: extract everything after "## El Brief (Usuario)" until next "##"
    match = re.search(r'## El Brief \(Usuario\)\s*\n(.+?)\s*##\s+\w', content, re.DOTALL)
    if match:
        return match.group(1).strip()

    return ""


def extract_expected_results(test_file: Path) -> Dict[str, Any]:
    """Extract expected results metadata from test file."""
    content = test_file.read_text()
    metadata = {}

    # Extract frontmatter metadata
    tipo_match = re.search(r'\*\*Tipo de Test:\*\*\s*(.+)', content)
    if tipo_match:
        metadata['tipo'] = tipo_match.group(1).strip()

    veredicto_match = re.search(r'\*\*Veredicto Esperado:\*\*\s*(.+)', content)
    if veredicto_match:
        metadata['veredicto'] = veredicto_match.group(1).strip()

    cerebros_match = re.search(r'\*\*Cerebros Involucrados:\*\*\s*(.+)', content)
    if cerebros_match:
        metadata['cerebros'] = cerebros_match.group(1).strip()

    complejidad_match = re.search(r'\*\*Complejidad:\*\*\s*(.+)', content)
    if complejidad_match:
        metadata['complejidad'] = complejidad_match.group(1).strip()

    return metadata


def run_orchestration(brief: str, use_mcp: bool = True) -> Dict[str, Any]:
    """Run the orchestrator with the given brief."""
    project_root = Path(__file__).parent.parent

    cmd = [
        sys.executable, "-m", "mastermind_cli.commands.orchestrate",
        "run", brief,
        "--use-mcp" if use_mcp else "",
    ]

    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes max per test
    )

    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def print_header(text: str, char: str = "="):
    """Print a formatted header."""
    print(f"\n{char * 70}")
    print(f"  {text}")
    print(f"{char * 70}\n")


def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with color."""
    icon = "✅" if passed else "❌"
    status = "PASS" if passed else "FAIL"
    print(f"{icon} {test_name}: {status}")
    if details:
        print(f"   {details}")


def main():
    """Run E2E tests."""
    print_header("MasterMind E2E Test Runner", "=")

    # Find all marketing test files
    tests_dir = Path(__file__).parent.parent / "tests" / "test-briefs"
    test_files = sorted(tests_dir.glob("test-marketing-*.md"))

    if not test_files:
        print("❌ No test files found in tests/test-briefs/")
        sys.exit(1)

    print(f"Found {len(test_files)} test files\n")

    results = []
    summary = {
        "total": len(test_files),
        "passed": 0,
        "failed": 0,
        "skipped": 0,
    }

    for test_file in test_files:
        test_name = test_file.stem
        print_header(f"Running: {test_name}", "-")

        # Extract brief and expected results
        brief = extract_brief_from_test_file(test_file)
        expected = extract_expected_results(test_file)

        if not brief:
            print_test_result(test_name, False, "No brief found in test file")
            summary["failed"] += 1
            results.append({
                "test": test_name,
                "status": "FAIL",
                "error": "No brief found"
            })
            continue

        print(f"📋 Brief Preview: {brief[:100]}...")
        print(f"   Expected: {expected.get('veredicto', 'N/A')}")
        print(f"   Complexity: {expected.get('complejidad', 'N/A')}")
        print()

        # Run orchestration
        print("🔄 Running orchestration...")
        try:
            result = run_orchestration(brief, use_mcp=True)

            if result["exit_code"] == 0:
                print_test_result(test_name, True)
                summary["passed"] += 1
                results.append({
                    "test": test_name,
                    "status": "PASS",
                    "expected": expected,
                })
            else:
                error_msg = result["stderr"][:200] if result["stderr"] else "Unknown error"
                print_test_result(test_name, False, error_msg)
                summary["failed"] += 1
                results.append({
                    "test": test_name,
                    "status": "FAIL",
                    "error": error_msg,
                    "expected": expected,
                })

        except subprocess.TimeoutExpired:
            print_test_result(test_name, False, "Test timed out (5 minutes)")
            summary["failed"] += 1
            results.append({
                "test": test_name,
                "status": "FAIL",
                "error": "Timeout",
                "expected": expected,
            })
        except Exception as e:
            print_test_result(test_name, False, str(e))
            summary["failed"] += 1
            results.append({
                "test": test_name,
                "status": "FAIL",
                "error": str(e),
                "expected": expected,
            })

        print()

    # Print summary
    print_header("Test Summary", "=")
    print(f"Total Tests:  {summary['total']}")
    print(f"✅ Passed:     {summary['passed']}")
    print(f"❌ Failed:     {summary['failed']}")
    print(f"⏭️  Skipped:    {summary['skipped']}")

    if summary["passed"] == summary["total"]:
        print("\n🎉 All tests passed!")
        exit_code = 0
    else:
        print(f"\n❌ {summary['failed']} test(s) failed")
        exit_code = 1

    # Save results to JSON
    results_file = Path(__file__).parent.parent / "logs" / f"e2e-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    results_file.write_text(json.dumps({
        "summary": summary,
        "results": results,
    }, indent=2))
    print(f"\n📄 Results saved to: {results_file}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
