"""
Tests for Legacy Brain Wrapper (backward compatibility).

Tests:
- LegacyBrainAdapter wraps v1.x brains correctly
- State isolation (no cross-talk between calls)
- Brain #1 (Product Strategy) wrapping
- Brain #7 (Evaluator) wrapping
- Output normalization
"""

from unittest.mock import Mock, MagicMock

import pytest

from mastermind_cli.compatibility.legacy_wrapper import (
    LegacyBrainAdapter,
    LegacyExecutionContext,
    wrap_legacy_brain_1,
    wrap_legacy_brain_7,
)
from mastermind_cli.types.interfaces import (
    BrainInput,
    Brief,
    ProductStrategy,
    GrowthDataEvaluation,
)


class TestLegacyBrainAdapter:
    """Test LegacyBrainAdapter generic wrapper."""

    def test_init(self):
        """Test adapter initialization."""
        mock_executor = Mock(return_value={})
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )
        assert adapter.brain_executor == mock_executor
        assert adapter.output_model == ProductStrategy
        assert adapter.brain_id == 1

    def test_call_with_valid_output(self):
        """Test calling wrapped brain returns output model."""
        # Mock legacy brain output
        mock_output = {
            "value_proposition": "Test positioning",
            "persona": {"name": "Test User"},
            "key_features": [
                {"feature": "Feature 1"},
                {"feature": "Feature 2"},
            ],
            "monetization": {"model": "subscription"},
            "success_metrics": [
                {"metric": "Metric 1"},
                {"metric": "Metric 2"},
            ],
        }

        mock_executor = Mock(return_value=mock_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        # Call with BrainInput
        input = BrainInput(
            brief=Brief(problem_statement="Build a comprehensive CRM application")
        )

        result = adapter(input)

        # Verify output model
        assert isinstance(result, ProductStrategy)
        assert result.positioning == "Test positioning"
        assert result.target_audience == "Test User"
        assert len(result.key_features) == 2
        assert len(result.success_metrics) == 2

    def test_call_with_brain_input(self):
        """Test calling with BrainInput model."""
        mock_output = {
            "value_proposition": "Test",
            "persona": {"name": "User"},
            "key_features": [],
            "monetization": {"model": "free"},
            "success_metrics": [],
        }

        mock_executor = Mock(return_value=mock_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        input = BrainInput(
            brief=Brief(problem_statement="Test brief"),
        )

        result = adapter(input)

        assert isinstance(result, ProductStrategy)
        mock_executor.assert_called_once()

    def test_call_uses_local_orchestrator(self):
        """Test that adapter creates local orchestrator (not shared)."""
        mock_executor = Mock(return_value={
            "value_proposition": "Test",
            "persona": {"name": "User"},
            "key_features": [],
            "monetization": {"model": "free"},
            "success_metrics": [],
        })

        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        # Verify executor was called with some orchestrator
        assert mock_executor.called
        call_args = mock_executor.call_args
        # The second argument should be an orchestrator instance
        orchestrator_arg = call_args[1].get("orchestrator")
        assert orchestrator_arg is not None

    def test_call_with_invalid_output_raises_validation_error(self):
        """Test invalid output raises ValueError."""
        # Return output that doesn't match ProductStrategy schema
        mock_output = {"invalid_field": "no_matching_fields"}

        mock_executor = Mock(return_value=mock_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))

        with pytest.raises(ValueError) as exc_info:
            adapter(input)
        assert "ProductStrategy" in str(exc_info.value)

    def test_call_with_executor_error_raises_runtime_error(self):
        """Test executor error raises RuntimeError."""
        # Mock executor that raises exception
        mock_executor = Mock(side_effect=RuntimeError("Brain execution failed"))

        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))

        with pytest.raises(RuntimeError) as exc_info:
            adapter(input)
        assert "Brain #1" in str(exc_info.value)
        assert "execution failed" in str(exc_info.value)


class TestStateIsolation:
    """Test that wrapper isolates state (no cross-talk)."""

    def test_multiple_calls_dont_share_state(self):
        """Test multiple adapter calls don't share state."""
        # Mock executor that returns different results based on brief
        def mock_executor(brief: str, orchestrator: Mock) -> dict:
            # Each call should have its own orchestrator
            return {
                "value_proposition": f"Positioning for {brief}",
                "persona": {"name": f"User for {brief[:10]}"},
                "key_features": [{"feature": f"Feature from {brief[:10]}"}],
                "monetization": {"model": "subscription"},
                "success_metrics": [],
            }

        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        # Call 1
        input1 = BrainInput(brief=Brief(problem_statement="Project brief A for CRM system"))
        result1 = adapter(input1)

        # Call 2 (should NOT affect result1)
        input2 = BrainInput(brief=Brief(problem_statement="Project brief B for CRM system"))
        result2 = adapter(input2)

        # Verify results are independent
        assert "Brief A" in result1.positioning
        assert "Brief B" in result2.positioning
        assert result1.positioning != result2.positioning

    def test_concurrent_calls_dnt_interfere(self):
        """Test concurrent calls don't interfere (simulated)."""
        import asyncio

        # Mock executor that simulates async work
        def mock_executor(brief: str, orchestrator: Mock) -> dict:
            return {
                "value_proposition": f"Result for {brief}",
                "persona": {"name": "User"},
                "key_features": [],
                "monetization": {"model": "free"},
                "success_metrics": [],
            }

        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        # Simulate concurrent calls
        results = []
        for i in range(5):
            input = BrainInput(brief=Brief(problem_statement=f"Brief {i}"))
            result = adapter(input)
            results.append(result)

        # Verify all results are unique
        positionings = [r.positioning for r in results]
        assert len(set(positionings)) == 5  # All unique


class TestBrain1Normalization:
    """Test Brain #1 output normalization."""

    def test_normalize_brain_1_output_complete(self):
        """Test normalization with complete legacy output."""
        legacy_output = {
            "value_proposition": "Best CRM ever",
            "persona": {"name": "Sales Managers"},
            "key_features": [
                {"feature": "Contact Management"},
                {"feature": "Pipeline Tracking"},
            ],
            "monetization": {"model": "subscription", "pricing": "$99/mo"},
            "success_metrics": [
                {"metric": "D7 Retention", "target": ">35%"},
                {"metric": "Activation Rate", "target": ">50%"},
            ],
        }

        mock_executor = Mock(return_value=legacy_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        assert result.positioning == "Best CRM ever"
        assert result.target_audience == "Sales Managers"
        assert result.key_features == ["Contact Management", "Pipeline Tracking"]
        assert result.success_metrics == ["D7 Retention", "Activation Rate"]

    def test_normalize_brain_1_output_partial(self):
        """Test normalization with partial legacy output."""
        legacy_output = {
            "value_proposition": "Test positioning",
            # Missing: persona, key_features, monetization, success_metrics
        }

        mock_executor = Mock(return_value=legacy_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        # Should use defaults for missing fields (with min 1 item)
        assert result.positioning == "Test positioning"
        assert result.target_audience == "Not specified"
        assert len(result.key_features) >= 1  # Has default
        assert len(result.success_metrics) >= 1  # Has default

    def test_normalize_brain_1_output_with_positioning(self):
        """Test normalization when legacy already has positioning field."""
        legacy_output = {
            "positioning": "Already has positioning",
            "target_audience": "Test Audience",
            "key_features": [],
            "monetization_strategy": "freemium",
            "success_metrics": [],
        }

        mock_executor = Mock(return_value=legacy_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        # Should use existing fields directly
        assert result.positioning == "Already has positioning"
        assert result.target_audience == "Test Audience"


class TestBrain7Normalization:
    """Test Brain #7 output normalization."""

    def test_normalize_brain_7_output_complete(self):
        """Test normalization with complete legacy output."""
        legacy_output = {
            "veredict": "approved",
            "score": {
                "percentage": 85,
                "breakdown": {"criteria1": 10, "criteria2": 20},
            },
            "evaluation": "Great work on positioning",
        }

        mock_executor = Mock(return_value=legacy_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=GrowthDataEvaluation,
            brain_id=7,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        # Fix typo: veredict → verdict (uppercase)
        assert result.verdict == "APPROVE"
        assert result.score == 8.5  # 85% → 8.5/10
        assert result.feedback == "Great work on positioning"

    def test_normalize_brain_7_output_with_verdict(self):
        """Test normalization when legacy already has verdict field."""
        legacy_output = {
            "verdict": "approved",
            "score": {"percentage": 90},
            "reasoning": "Well structured",
        }

        mock_executor = Mock(return_value=legacy_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=GrowthDataEvaluation,
            brain_id=7,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        # Should use existing fields directly (verdict uppercase)
        assert result.verdict == "APPROVE"
        assert result.score == 9.0  # 90% → 9.0/10
        assert result.feedback == "Well structured"

    def test_normalize_brain_7_output_partial(self):
        """Test normalization with partial legacy output."""
        legacy_output = {
            "veredict": "needs_work",
            # Missing: score, evaluation
        }

        mock_executor = Mock(return_value=legacy_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=GrowthDataEvaluation,
            brain_id=7,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        # Should use defaults for missing fields
        assert result.verdict == "CONDITIONAL"  # needs_work mapped to CONDITIONAL
        assert result.score == 5.0  # default score
        assert result.feedback == "No feedback provided"

        # Should use existing fields directly
        assert result.verdict == "approved"
        assert result.score_percentage == 90
        assert result.reasoning == "Well structured"

    def test_normalize_brain_7_output_partial(self):
        """Test normalization with partial legacy output."""
        legacy_output = {
            "veredict": "needs_work",
            # Missing: score, evaluation
        }

        mock_executor = Mock(return_value=legacy_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=GrowthDataEvaluation,
            brain_id=7,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        # Should use defaults for missing fields
        assert result.verdict == "CONDITIONAL"  # needs_work mapped to CONDITIONAL
        assert result.score == 5.0  # default score
        assert result.feedback == "No feedback provided"


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""

    def test_wrap_legacy_brain_1(self):
        """Test wrap_legacy_brain_1 returns adapter."""
        adapter = wrap_legacy_brain_1()

        assert isinstance(adapter, LegacyBrainAdapter)
        assert adapter.output_model == ProductStrategy
        assert adapter.brain_id == 1

    def test_wrap_legacy_brain_7(self):
        """Test wrap_legacy_brain_7 returns adapter."""
        adapter = wrap_legacy_brain_7()

        assert isinstance(adapter, LegacyBrainAdapter)
        assert adapter.output_model == GrowthDataEvaluation
        assert adapter.brain_id == 7

    def test_wrap_legacy_brain_1_callable(self):
        """Test wrapped Brain #1 is callable."""
        adapter = wrap_legacy_brain_1()

        input = BrainInput(brief=Brief(problem_statement="Build a comprehensive CRM system"))
        result = adapter(input)

        assert isinstance(result, ProductStrategy)

    def test_wrap_legacy_brain_7_callable(self):
        """Test wrapped Brain #7 is callable."""
        adapter = wrap_legacy_brain_7()

        # Brain #7 requires output_to_evaluate, we'll test with mock
        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        assert isinstance(result, GrowthDataEvaluation)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_brief(self):
        """Test handling of empty brief."""
        mock_executor = Mock(return_value={
            "value_proposition": "",
            "persona": {"name": ""},
            "key_features": [{"feature": "Default feature"}],  # Add at least 1
            "monetization": {"model": ""},
            "success_metrics": [{"metric": "Default metric"}],  # Add at least 1
        })

        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        input = BrainInput(brief=Brief(problem_statement="Empty but valid brief text here"))
        result = adapter(input)

        assert isinstance(result, ProductStrategy)

    def test_brief_extraction_from_plain_string(self):
        """Test brief extraction when input is not BrainInput."""
        # Create a mock input that's not BrainInput
        class SimpleInput:
            problem_statement = "Test problem"

        mock_executor = Mock(return_value={
            "value_proposition": "Test",
            "persona": {"name": "User"},
            "key_features": [{"feature": "Default"}],  # Add at least 1
            "monetization": {"model": "free"},
            "success_metrics": [{"metric": "Default"}],  # Add at least 1
        })

        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        # Should handle gracefully
        input = SimpleInput()
        result = adapter(input)

        assert isinstance(result, ProductStrategy)
        mock_executor.assert_called_once()

    def test_nested_dict_handling(self):
        """Test handling of deeply nested dicts in output."""
        mock_output = {
            "value_proposition": "Test",
            "persona": {
                "name": "User",
                "description": "Test user",
                "nested": {"field": "value"},
            },
            "key_features": [{"feature": "Default feature"}],  # Add at least 1
            "monetization": {"model": "free"},
            "success_metrics": [{"metric": "Default metric"}],  # Add at least 1
        }

        mock_executor = Mock(return_value=mock_output)
        adapter = LegacyBrainAdapter(
            brain_executor=mock_executor,
            output_model=ProductStrategy,
            brain_id=1,
        )

        input = BrainInput(brief=Brief(problem_statement="Test application for CRM system"))
        result = adapter(input)

        # Should extract name from nested persona
        assert result.target_audience == "User"
