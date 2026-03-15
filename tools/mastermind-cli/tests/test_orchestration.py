"""
Test orchestration integration.

Tests the evaluator, NotebookLM client, and overall orchestration flow.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from mastermind_cli.orchestrator import (  # noqa: E402
    Evaluator,
    NotebookLMClient,
    MCPWrapper,
    DirectMCPInvoker,
    list_active_brains,
)


def test_list_active_brains():
    """Test listing active brains."""
    print("\n=== Test: List Active Brains ===")
    brains = list_active_brains()

    print(f"Found {len(brains)} active brains:")
    for brain in brains:
        print(f"  Brain #{brain['brain_id']}: {brain['notebook_id']}")

    assert len(brains) == 7, "Should have 7 active brains"
    print("✅ PASS")


def test_notebooklm_client():
    """Test NotebookLM client."""
    print("\n=== Test: NotebookLM Client ===")
    client = NotebookLMClient()

    # Test get notebook ID
    notebook_id = client.get_notebook_id(1)
    print(f"Brain #1 notebook ID: {notebook_id}")
    assert notebook_id == "f276ccb3-0bce-4069-8b55-eae8693dbe75"

    # Test is brain available
    assert client.is_brain_available(1)
    assert not client.is_brain_available(99)

    # Test get available brains
    available = client.get_available_brains()
    print(f"Available brains: {len(available)}")
    assert len(available) == 7

    print("✅ PASS")


def test_evaluator_load_matrix():
    """Test evaluator matrix loading."""
    print("\n=== Test: Evaluator Matrix Loading ===")
    evaluator = Evaluator()

    matrix = evaluator.load_matrix("MATRIX-product-brief")

    assert "error" not in matrix, f"Failed to load matrix: {matrix.get('error')}"
    assert matrix["matrix_id"] == "MATRIX-product-brief"
    assert "checks" in matrix

    print(f"Matrix loaded: {matrix['matrix_id']}")
    print(f"Total possible score: {matrix['scoring']['total_possible']}")

    # Count checks by category
    for category, checks in matrix["checks"].items():
        print(f"  {category}: {len(checks)} checks")

    print("✅ PASS")


def test_evaluator_simple():
    """Test evaluator with a simple output."""
    print("\n=== Test: Evaluator (Simple) ===")
    evaluator = Evaluator()

    # Create a minimal output
    simple_output = {
        "problem": "Users cannot find teammates for hackathons",
        "persona": {
            "name": "Hackathon Organizer",
            "description": "People who organize hackathons need better team matching",
        },
        "value_proposition": "AI-powered team formation based on skills and interests",
        "key_features": [
            "Skill matching algorithm",
            "Interest-based grouping",
            "Team chat",
        ],
        "risks": {
            "value_risk": "Do people care about team matching?",
            "usability_risk": "Can we make it simple enough?",
            "feasibility_risk": "Can we build the matching algorithm?",
            "viability_risk": "Is there a business model?",
        },
        "assumptions": [
            "People want balanced teams",
            "Skill diversity matters",
            "Timing is important",
        ],
        "evidence": {
            "interviews": "Interviewed 5 hackathon organizers",
            "data": "All 5 reported team formation issues",
        },
    }

    result = evaluator.evaluate(
        output=simple_output, matrix_id="MATRIX-product-brief", brain_id=1
    )

    print(f"Veredict: {result['veredict']}")
    print(
        f"Score: {result['score']['points']}/{result['score']['total']} ({result['score']['percentage']}%)"
    )
    print(f"Passed: {len(result['passed_checks'])}")
    print(f"Failed: {len(result['failed_checks'])}")
    print(f"Biases: {len(result['biases_detected'])}")

    assert "veredict" in result
    assert "score" in result
    assert result["veredict"] in ["APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"]

    print("✅ PASS")


def test_evaluator_weak_output():
    """Test evaluator with a weak output (should REJECT)."""
    print("\n=== Test: Evaluator (Weak Output - Expected REJECT) ===")
    evaluator = Evaluator()

    # Create a weak output (no evidence, no specific persona, no metrics)
    weak_output = {
        "idea": "An app for sharing photos",
        "target": "Young people aged 18-35",
        "features": ["Take photos", "Share photos", "Like photos"],
    }

    result = evaluator.evaluate(
        output=weak_output, matrix_id="MATRIX-product-brief", brain_id=1
    )

    print(f"Veredict: {result['veredict']}")
    print(
        f"Score: {result['score']['points']}/{result['score']['total']} ({result['score']['percentage']}%)"
    )
    print(f"Failed checks: {len(result['failed_checks'])}")

    for fail in result["failed_checks"][:3]:
        print(f"  - {fail['check_id']}: {fail['check']}")

    # Weak output should get REJECT or at least CONDITIONAL
    assert result["veredict"] in ["REJECT", "CONDITIONAL"]
    assert result["score"]["percentage"] < 80

    print("✅ PASS")


def test_mcp_wrapper():
    """Test MCP wrapper."""
    print("\n=== Test: MCP Wrapper ===")

    # Test create brain 1 query
    query = DirectMCPInvoker.create_brain_1_query("An app for finding teammates")
    print(f"Brain #1 query length: {len(query)} chars")
    assert "product strategy analysis" in query.lower()

    # Test query spec
    spec = MCPWrapper.create_notebook_query_spec(
        notebook_id="f276ccb3-0bce-4069-8b55-eae8693dbe75", query="Test query"
    )
    assert spec["tool"] == "mcp__notebooklm-mcp__notebook_query"

    print("✅ PASS")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("MasterMind Orchestration Tests")
    print("=" * 50)

    tests = [
        test_list_active_brains,
        test_notebooklm_client,
        test_evaluator_load_matrix,
        test_evaluator_simple,
        test_evaluator_weak_output,
        test_mcp_wrapper,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
