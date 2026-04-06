"""Quality score calculation using Hormozi value equation.

This module implements the quality score calculation for Brain #7 to evaluate
brain outputs. The formula is:

    Quality Score = (Precision × Success_Probability) / (T1 × Tokens)

Thresholds:
    - >= 3.0: Store as template candidate
    - >= 1.0: Store as experience record
    - < 1.0: Discard ("dead offer")

Penalties:
    - Twaddle: Output > 2000 words without structure → 50% penalty
    - Inversion: Cannot state "what to avoid" → 30% penalty
"""

from typing import Optional


def calculate_quality_score(
    precision: float,
    success_probability: float,
    t1_ms: int,
    tokens: int,
    output_text: Optional[str] = None,
) -> float:
    """Calculate quality score using Hormozi value equation.

    Args:
        precision: Precision metric (0.0 to 1.0)
        success_probability: Success probability (0.0 to 1.0)
        t1_ms: Time to first token in milliseconds
        tokens: Total token count
        output_text: Optional output text for penalty checks

    Returns:
        Quality score (higher is better)

    Thresholds:
        - >= 3.0: Store as template candidate
        - >= 1.0: Store as experience record
        - < 1.0: Discard ("dead offer")

    Penalties (if output_text provided):
        - Twaddle: >2000 words without structure → 50% penalty
        - Inversion: Cannot state "what to avoid" → 30% penalty
    """
    # Convert to seconds (minimum 1 second to avoid division by zero)
    t1_sec = max(t1_ms / 1000, 1.0)
    token_count = max(tokens, 1)

    # Base score: (Precision × Success_Probability × 400000) / (T1 × Tokens)
    # Scaled to produce scores in range: >= 3.0 (template), >= 1.0 (record), < 1.0 (discard)
    base_score = (precision * success_probability * 400000) / (t1_sec * token_count)

    # Apply penalties if output text provided
    if output_text:
        word_count = len(output_text.split())
        if word_count > 2000 and not _has_structure(output_text):
            base_score *= 0.5  # Twaddle penalty (50% reduction)
        if not _can_invert(output_text):
            base_score *= 0.7  # Inversion check penalty (30% reduction)

    return round(base_score, 2)


def _has_structure(text: str) -> bool:
    """Check if text has structured elements (headings, bullets, numbered lists).

    Args:
        text: Text to check for structure

    Returns:
        True if text contains structural markers, False otherwise
    """
    structure_markers = ["##", "###", "- ", "* ", "1.", "2.", "3."]
    return any(marker in text for marker in structure_markers)


def _can_invert(text: str) -> bool:
    """Check if text can state 'what to avoid' (inversion test).

    This checks for phrases that indicate the output can state what to avoid,
    which is a sign of comprehensive understanding.

    Args:
        text: Text to check for inversion capability

    Returns:
        True if text contains inversion phrases, False otherwise
    """
    inversion_phrases = [
        "avoid",
        "don't",
        "do not",
        "never",
        "warning",
        "pitfall",
        "anti-pattern",
    ]
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in inversion_phrases)
