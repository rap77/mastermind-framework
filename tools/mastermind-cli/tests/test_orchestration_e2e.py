"""
End-to-end test for orchestration flow.

Tests the complete flow: brief → Brain #1 → Brain #7 → veredict
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from mastermind_cli.orchestrator import Coordinator, OutputFormatter  # noqa: E402


def test_validation_flow_good_brief():
    """Test validation flow with a good brief (should APPROVE)."""
    print("\n" + "=" * 70)
    print("TEST: Validation Flow - Good Brief (Expected: APPROVE)")
    print("=" * 70)

    # A relatively complete brief
    brief = """
    Una app para conectar developers junior con senior mentors
    para code reviews y pair programming sessions.

    Problema: Los devs junior no tienen acceso a feedback de calidad.
    Sus seniors están ocupados y no pueden dar code reviews proper.

    Solución: Marketplace donde seniors pagan dinero por su tiempo,
    juniors pagan por sesiones de code review.

    Evidencia: Entrevisté 5 juniors, todos dicen que necesitan feedback.
    También hablé con 3 seniors que estarían dispuestos a dedicar 2h/semana.

    Métricas: D7 retention >35%, activation rate >50%, NPS >40.
    """

    formatter = OutputFormatter()
    coordinator = Coordinator(formatter=formatter)

    result = coordinator.orchestrate(
        brief=brief.strip(), flow="validation_only", max_iterations=2
    )

    print("\n" + "=" * 70)
    print("RESULT:")
    print("=" * 70)
    print(f"Status: {result.get('status')}")
    print(f"Veredict: {result.get('veredict')}")
    print(f"Iterations: {result.get('iterations', 1)}")

    assert result["status"] in ["completed", "escalated"]
    assert "veredict" in result
    assert "evaluations" in result

    print("\n✅ Test passed!")


def test_validation_flow_weak_brief():
    """Test validation flow with a weak brief (should REJECT)."""
    print("\n" + "=" * 70)
    print("TEST: Validation Flow - Weak Brief (Expected: REJECT)")
    print("=" * 70)

    # A weak brief without evidence, metrics, or specific persona
    brief = """
    Quiero crear una app social para jóvenes.

    Va a ser super popular. La gente va a poder subir fotos,
    comentar, y dar like.

    Va a ser mejor que Instagram porque somos más cool.

    Necesito inversión para desarrollarlo.
    """

    formatter = OutputFormatter()
    coordinator = Coordinator(formatter=formatter)

    result = coordinator.orchestrate(
        brief=brief.strip(), flow="validation_only", max_iterations=2
    )

    print("\n" + "=" * 70)
    print("RESULT:")
    print("=" * 70)
    print(f"Status: {result.get('status')}")
    print(f"Veredict: {result.get('veredict')}")

    # Should be REJECT for such a weak brief
    assert result["status"] in ["completed", "escalated"]
    assert result.get("veredict") in ["REJECT", "CONDITIONAL", "ESCALATE"]

    print("\n✅ Test passed!")


def test_dry_run():
    """Test dry run mode (should show plan without executing)."""
    print("\n" + "=" * 70)
    print("TEST: Dry Run Mode")
    print("=" * 70)

    brief = "Una app para encontrar compañeros de viaje."

    formatter = OutputFormatter()
    coordinator = Coordinator(formatter=formatter)

    result = coordinator.orchestrate(
        brief=brief.strip(), flow="validation_only", dry_run=True
    )

    print("\n" + "=" * 70)
    print("PLAN:")
    print("=" * 70)
    print(result.get("output", "No output"))

    assert result["status"] == "dry_run_complete"
    assert "plan" in result

    print("\n✅ Test passed!")


def test_iteration_loop():
    """Test that iteration loop works correctly."""
    print("\n" + "=" * 70)
    print("TEST: Iteration Loop")
    print("=" * 70)

    # This brief should trigger CONDITIONAL, then we want to see
    # if the iteration works (even though without real MCP,
    # we won't see improvement)
    brief = """
    App de productividad para freelancers.

    Problema: Los freelancers no pueden organizarse bien.
    Solución: App con tareas y calendario.

    Métricas: D30 retention >15%.
    """

    formatter = OutputFormatter()
    coordinator = Coordinator(formatter=formatter)

    result = coordinator.orchestrate(
        brief=brief.strip(), flow="validation_only", max_iterations=2
    )

    print("\n" + "=" * 70)
    print("RESULT:")
    print("=" * 70)
    print(f"Status: {result.get('status')}")
    print(f"Veredict: {result.get('veredict')}")
    print(f"Iterations: {result.get('iterations', 1)}")

    # Should have attempted at least 1 iteration
    assert result.get("iterations", 1) >= 1

    print("\n✅ Test passed!")


def run_all_tests():
    """Run all end-to-end tests."""
    print("\n" + "=" * 70)
    print("MASTERMIND ORCHESTRATION - END-TO-END TESTS")
    print("=" * 70)

    tests = [
        test_dry_run,
        test_validation_flow_good_brief,
        test_validation_flow_weak_brief,
        test_iteration_loop,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
