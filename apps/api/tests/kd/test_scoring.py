"""Tests for quality score calculation module (Hormozi value equation)."""

from mastermind_cli.experience.scoring import (
    calculate_quality_score,
    _has_structure,
    _can_invert,
)


class TestQualityScoreCalculation:
    """Test quality score calculation with various scenarios."""

    def test_high_quality_output_provides_template_score(self):
        """Test 1: High-quality output produces score >= 3.0 (template candidate).

        Scenario: precision=0.95, success=0.90, T1=85s, tokens=1200
        Expected: score >= 3.0 (eligible for template storage)
        """
        score = calculate_quality_score(
            precision=0.95,
            success_probability=0.90,
            t1_ms=85000,  # 85 seconds
            tokens=1200,
            output_text="## High quality output\n- Clear insights\n- Avoid mistakes\n1. First step\n2. Second step",
        )

        assert (
            score >= 3.0
        ), f"Expected score >= 3.0 for high-quality output, got {score}"

    def test_medium_quality_output_provides_record_score(self):
        """Test 2: Medium-quality output produces score >= 1.0 (experience record).

        Scenario: precision=0.70, success=0.60, T1=120s, tokens=800
        Expected: score >= 1.0 (eligible for experience record storage)
        """
        score = calculate_quality_score(
            precision=0.70,
            success_probability=0.60,
            t1_ms=120000,  # 120 seconds
            tokens=800,
            output_text="## Decent output\n- Some insights\n- Avoid pitfalls",
        )

        assert (
            score >= 1.0
        ), f"Expected score >= 1.0 for medium-quality output, got {score}"
        assert (
            score < 3.0
        ), f"Expected score < 3.0 for medium-quality output, got {score}"

    def test_low_quality_output_provides_discard_score(self):
        """Test 3: Low-quality output produces score < 1.0 (discard).

        Scenario: precision=0.30, success=0.20, T1=300s, tokens=2000
        Expected: score < 1.0 (should be discarded as "dead offer")
        """
        score = calculate_quality_score(
            precision=0.30,
            success_probability=0.20,
            t1_ms=300000,  # 300 seconds
            tokens=2000,
            output_text="Poor quality output",
        )

        assert score < 1.0, f"Expected score < 1.0 for low-quality output, got {score}"

    def test_twaddle_penalty_reduces_score_by_50_percent(self):
        """Test 4: Twaddle penalty (>2000 words without structure) reduces score by 50%.

        Scenario: Output > 2000 words without structural markers
        Expected: Score reduced by 50% compared to structured equivalent
        """
        # Create a long text without structure (>2000 words)
        unstructured_text = " ".join(["word"] * 2500)  # 2500 words, no structure

        # Create equivalent structured text
        structured_text = "## Section\n" + " ".join(["word"] * 2500)

        unstructured_score = calculate_quality_score(
            precision=0.80,
            success_probability=0.80,
            t1_ms=60000,
            tokens=1500,
            output_text=unstructured_text,
        )

        structured_score = calculate_quality_score(
            precision=0.80,
            success_probability=0.80,
            t1_ms=60000,
            tokens=1500,
            output_text=structured_text,
        )

        # Unstructured should be 50% of structured (twaddle penalty)
        # Use approximate comparison due to rounding
        expected_unstructured = structured_score * 0.5
        assert abs(unstructured_score - expected_unstructured) < 0.01, (
            f"Expected unstructured score to be ~50% of structured score. "
            f"Got {unstructured_score} vs {expected_unstructured:.2f}"
        )

    def test_inversion_check_penalty_reduces_score_by_30_percent(self):
        """Test 5: Inversion check penalty (cannot state 'what to avoid') reduces score by 30%.

        Scenario: Output without inversion phrases (avoid, don't, never, etc.)
        Expected: Score reduced by 30% compared to output with inversion
        """
        # Output without inversion phrases
        without_inversion = "Here is what you should do: follow these steps"

        # Output with inversion phrases
        with_inversion = (
            "Here is what you should do: follow these steps. "
            "Avoid these common pitfalls. Never skip this step."
        )

        without_score = calculate_quality_score(
            precision=0.80,
            success_probability=0.80,
            t1_ms=60000,
            tokens=1500,
            output_text=without_inversion,
        )

        with_score = calculate_quality_score(
            precision=0.80,
            success_probability=0.80,
            t1_ms=60000,
            tokens=1500,
            output_text=with_inversion,
        )

        # Without inversion should be 70% of with inversion (30% penalty)
        # Use approximate comparison due to rounding
        expected_without = with_score * 0.7
        assert abs(without_score - expected_without) < 0.01, (
            f"Expected score without inversion to be ~70% of score with inversion. "
            f"Got {without_score} vs {expected_without:.2f}"
        )


class TestStructureDetection:
    """Test _has_structure helper function."""

    def test_detects_headings(self):
        """Test that ## and ### markers are detected as structure."""
        assert _has_structure("## Main Heading") is True
        assert _has_structure("### Sub Heading") is True
        assert _has_structure("No heading here") is False

    def test_detects_bullets(self):
        """Test that bullet points (- and *) are detected as structure."""
        assert _has_structure("- Item one") is True
        assert _has_structure("* Item two") is True
        assert _has_structure("Item without bullet") is False

    def test_detects_numbered_lists(self):
        """Test that numbered lists (1., 2., 3.) are detected as structure."""
        assert _has_structure("1. First item") is True
        assert _has_structure("2. Second item") is True
        assert _has_structure("3. Third item") is True
        assert _has_structure("Item without number") is False


class TestInversionDetection:
    """Test _can_invert helper function."""

    def test_detects_avoid(self):
        """Test that 'avoid' is detected as inversion phrase."""
        assert _can_invert("You should avoid this mistake") is True
        assert _can_invert("Do not make errors") is True

    def test_detects_dont(self):
        """Test that 'don't' is detected as inversion phrase."""
        assert _can_invert("Don't skip this step") is True

    def test_detects_never(self):
        """Test that 'never' is detected as inversion phrase."""
        assert _can_invert("Never use this approach") is True

    def test_detects_warning(self):
        """Test that 'warning' is detected as inversion phrase."""
        assert _can_invert("Warning: this may cause issues") is True

    def test_no_inversion_phrases(self):
        """Test that text without inversion phrases returns False."""
        assert _can_invert("Follow these steps to succeed") is False
        assert _can_invert("Here is the best approach") is False
