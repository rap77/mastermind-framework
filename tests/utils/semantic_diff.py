"""
Semantic similarity utility for regression testing.

Uses sentence-transformers embeddings + cosine similarity to detect
"Silent Changes" in brain outputs that would otherwise break flows.
"""

from typing import Union, Dict, List
import json


def _check_sentence_transformers() -> bool:
    """Check if sentence-transformers is installed."""
    try:
        import sentence_transformers  # noqa: F401
        import scipy  # noqa: F401

        return True
    except ImportError:
        return False


# Lazy-loaded model (module-level singleton)
_model = None


def _get_model():
    """Lazy-load sentence-transformers model."""
    global _model

    if not _check_sentence_transformers():
        raise ImportError(
            "sentence-transformers or scipy not installed. "
            "Install with: uv add sentence-transformers scipy"
        )

    if _model is None:
        from sentence_transformers import SentenceTransformer

        # all-MiniLM-L6-v2: 384 dimensions, fast, good quality
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def semantic_similarity(golden: str, actual: str) -> float:
    """Calculate semantic similarity score (0.0 = different, 1.0 = identical).

    Uses sentence-transformers embeddings + cosine similarity.

    Args:
        golden: Expected output (from snapshot)
        actual: Actual output (from current execution)

    Returns:
        Similarity score between 0.0 and 1.0
    """
    model = _get_model()

    # Encode both strings
    emb1 = model.encode(golden, convert_to_numpy=True)
    emb2 = model.encode(actual, convert_to_numpy=True)

    # Calculate cosine similarity (1 - cosine distance)
    from scipy.spatial.distance import cosine

    similarity = 1 - cosine(emb1, emb2)

    return float(similarity)


def compare_outputs(
    golden: Union[str, Dict, List],
    actual: Union[str, Dict, List],
    threshold: float = 0.90,
) -> Dict[str, any]:
    """Compare outputs and return similarity score + pass/fail.

    Args:
        golden: Expected output (from snapshot)
        actual: Actual output (from current execution)
        threshold: Minimum similarity score to pass (default 0.90)

    Returns:
        Dict with score, passed, and details.
    """
    # Convert to string for comparison
    golden_str = (
        json.dumps(golden, sort_keys=True)
        if isinstance(golden, (dict, list))
        else str(golden)
    )
    actual_str = (
        json.dumps(actual, sort_keys=True)
        if isinstance(actual, (dict, list))
        else str(actual)
    )

    # Calculate similarity
    score = semantic_similarity(golden_str, actual_str)

    return {
        "score": score,
        "passed": score >= threshold,
        "threshold": threshold,
        "diff": "Semantic difference detected"
        if score < threshold
        else "Outputs match",
    }


# Thresholds per brain type (from CONTEXT.md decision)
BRAIN_THRESHOLDS = {
    "product_strategy": 0.90,  # Creative allows variance
    "finance": 0.98,  # Precision required
    "brand": 0.85,  # Highly subjective
    "ux_research": 0.90,
    "growth": 0.90,
    "default": 0.90,
}


def get_brain_threshold(brain_id: str) -> float:
    """Get similarity threshold for a brain type.

    Args:
        brain_id: Brain identifier (e.g., "brain-software-01-product-strategy")

    Returns:
        Similarity threshold for this brain type
    """
    # Extract brain type from brain_id (e.g., "brain-software-01-product-strategy" -> "product_strategy")
    brain_id_lower = brain_id.lower().replace("-", "_")

    for key in BRAIN_THRESHOLDS:
        if key in brain_id_lower:
            return BRAIN_THRESHOLDS[key]
    return BRAIN_THRESHOLDS["default"]
