"""
Tests for semantic similarity utility.
"""

import pytest
from tests.utils.semantic_diff import (
    semantic_similarity,
    compare_outputs,
    get_brain_threshold,
    BRAIN_THRESHOLDS,
    _check_sentence_transformers
)


@pytest.mark.skipif(
    not _check_sentence_transformers(),
    reason="sentence-transformers not installed"
)
class TestSemanticSimilarity:
    """Test semantic similarity scoring."""

    def test_identical_strings_return_score_1_0(self):
        """Identical strings should return score 1.0."""
        score = semantic_similarity("hello world", "hello world")
        assert score == 1.0

    def test_semantically_similar_strings_return_score_gt_0_85(self):
        """Semantically similar strings should return score > 0.85."""
        score = semantic_similarity(
            "The product strategy is complete",
            "Product strategy has been completed"
        )
        assert score > 0.85

    def test_different_strings_return_score_lt_0_5(self):
        """Completely different strings should return score < 0.5."""
        score = semantic_similarity(
            "I love programming",
            "The weather is sunny today"
        )
        assert score < 0.5

    def test_score_between_0_and_1(self):
        """All scores should be between 0.0 and 1.0."""
        score = semantic_similarity("some text", "other text")
        assert 0.0 <= score <= 1.0


@pytest.mark.skipif(
    not _check_sentence_transformers(),
    reason="sentence-transformers not installed"
)
class TestCompareOutputs:
    """Test output comparison with threshold checking."""

    def test_compare_outputs_with_strings(self):
        """compare_outputs() should handle string inputs."""
        result = compare_outputs("hello", "hello", threshold=0.90)
        assert result["score"] == 1.0
        assert result["passed"] is True
        assert result["threshold"] == 0.90
        assert "Outputs match" in result["diff"]

    def test_compare_outputs_with_dicts(self):
        """compare_outputs() should handle dict inputs."""
        golden = {"key": "value", "number": 42}
        actual = {"key": "value", "number": 42}
        result = compare_outputs(golden, actual, threshold=0.90)
        assert result["passed"] is True
        assert result["score"] == 1.0

    def test_compare_outputs_with_lists(self):
        """compare_outputs() should handle list inputs."""
        golden = ["item1", "item2"]
        actual = ["item1", "item2"]
        result = compare_outputs(golden, actual, threshold=0.90)
        assert result["passed"] is True

    def test_compare_outputs_fails_below_threshold(self):
        """compare_outputs() should fail when score < threshold."""
        result = compare_outputs(
            "programming is fun",
            "today is sunny",
            threshold=0.95
        )
        assert result["passed"] is False
        assert result["score"] < 0.95
        assert "Semantic difference detected" in result["diff"]


class TestBrainThresholds:
    """Test brain-specific threshold retrieval."""

    def test_get_product_strategy_threshold(self):
        """Product strategy brain should have 0.90 threshold."""
        threshold = get_brain_threshold("brain-software-01-product-strategy")
        assert threshold == 0.90

    def test_get_finance_threshold(self):
        """Finance brain should have 0.98 threshold (higher precision)."""
        threshold = get_brain_threshold("brain-marketing-01-finance")
        assert threshold == 0.98

    def test_get_brand_threshold(self):
        """Brand brain should have 0.85 threshold (more lenient)."""
        threshold = get_brain_threshold("brain-marketing-02-brand")
        assert threshold == 0.85

    def test_get_unknown_brain_threshold(self):
        """Unknown brain should use default 0.90 threshold."""
        threshold = get_brain_threshold("brain-unknown-123-test")
        assert threshold == 0.90

    def test_all_thresholds_defined(self):
        """All thresholds should be between 0.0 and 1.0."""
        for brain_type, threshold in BRAIN_THRESHOLDS.items():
            assert 0.0 <= threshold <= 1.0, f"{brain_type} threshold {threshold} out of range"
