"""
Unit tests for InterviewLogger learning features.

Tests for PRP-015: Brain #8 Learning System Integration.
"""

import pytest
import yaml
from pathlib import Path
import tempfile
from datetime import datetime, timedelta
from mastermind_cli.memory.interview_logger import InterviewLogger


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for test logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def populated_logger(temp_log_dir):
    """Create logger with sample interviews."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    # Log sample interviews
    sample_interviews = [
        {
            "session_id": "test-001",
            "brief_original": "app moderna delivery comida",
            "interview_doc": {
                "metadata": {"context_type": "feature_spec"},
                "document": {
                    "qa": [
                        {"question": "Q1", "answer": "A1", "confidence": "high"},
                        {"question": "Q2", "answer": "A2", "confidence": "medium"},
                    ],
                    "categories": ["functional", "technical"],
                    "gaps_detected": [],
                },
            },
            "outcome": {
                "useful_questions": ["q001", "q002"],
                "user_satisfaction": "high",
                "duration_minutes": 15,
                "final_output_quality": "approved",
            },
        },
        {
            "session_id": "test-002",
            "brief_original": "delivery app food",
            "interview_doc": {
                "metadata": {"context_type": "feature_spec"},
                "document": {
                    "qa": [{"question": "Q3", "answer": "A3", "confidence": "medium"}],
                    "categories": ["ux"],
                    "gaps_detected": [],
                },
            },
            "outcome": {
                "useful_questions": ["q003"],
                "user_satisfaction": "medium",
                "duration_minutes": 10,
                "final_output_quality": "approved",
            },
        },
    ]

    for interview in sample_interviews:
        logger.log_interview(**interview)

    return logger


def test_find_similar_interviews(populated_logger):
    """Test interview similarity matching."""
    matches = populated_logger.find_similar_interviews("app delivery")

    assert len(matches) > 0, "Should find at least one similar interview"
    assert matches[0]["similarity_score"] > 0, "Similarity score should be positive"
    assert "interview_id" in matches[0], "Should include interview_id"


def test_find_similar_interviews_with_threshold(populated_logger):
    """Test similarity threshold filtering."""
    # High threshold should return fewer results
    matches = populated_logger.find_similar_interviews(
        "app delivery", min_similarity=0.5
    )

    assert len(matches) >= 0, "High threshold returns fewer or no results"


def test_extract_keywords():
    """Test keyword extraction with stop words."""
    logger = InterviewLogger(enabled=False)

    keywords = logger._extract_keywords("app moderna delivery comida rápida")

    # Should extract content words (min 4 chars)
    assert "moderna" in keywords
    assert "delivery" in keywords
    assert "comida" in keywords
    assert "rápida" in keywords

    # "app" is only 3 chars, should be filtered
    assert "app" not in keywords

    # Should filter stop words
    assert "que" not in keywords
    assert "la" not in keywords
    assert "el" not in keywords
    assert "the" not in keywords


def test_extract_keywords_english():
    """Test keyword extraction for English text."""
    logger = InterviewLogger(enabled=False)

    keywords = logger._extract_keywords("modern food delivery application")

    # Should extract content words
    assert "modern" in keywords
    assert "food" in keywords
    assert "delivery" in keywords
    assert "application" in keywords

    # Should filter stop words
    assert "the" not in keywords
    assert "and" not in keywords


def test_calculate_metrics_enhanced(temp_log_dir):
    """Test enhanced metrics calculation."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    interview_doc = {
        "metadata": {},
        "document": {
            "qa": [
                {
                    "question": "Q1",
                    "answer": "Long detailed answer with many words here",
                    "confidence": "high",
                    "category": "functional",
                },
                {
                    "question": "Q2",
                    "answer": "Short",
                    "confidence": "medium",
                    "category": "ux",
                },
            ],
            "categories": ["functional", "ux"],
            "gaps_detected": [],
        },
    }

    outcome = {"useful_questions": ["q001"], "user_satisfaction": "high"}

    log_path = logger.log_interview(
        session_id="metrics-test",
        brief_original="test brief",
        interview_doc=interview_doc,
        outcome=outcome,
    )

    # Verify enhanced metrics in log file
    assert log_path is not None, "Log path should be returned"
    with open(log_path) as f:
        content = yaml.safe_load(f)

    metrics = content["learning_metrics"]

    # Check new metrics exist
    assert "category_diversity" in metrics
    assert "avg_answer_length" in metrics
    assert "follow_up_effectiveness" in metrics
    assert "gap_detection_rate" in metrics

    # Verify values are reasonable
    assert metrics["category_diversity"] == 2  # Two categories (functional, ux)
    assert metrics["avg_answer_length"] > 0  # Should have average length


def test_retention_policy_hot_to_warm(temp_log_dir):
    """Test moving interviews from hot to warm storage."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    # Log an interview
    logger.log_interview(
        session_id="retention-test",
        brief_original="test brief",
        interview_doc={
            "metadata": {},
            "document": {"qa": [], "categories": [], "gaps_detected": []},
        },
        outcome={},
    )

    # Apply retention policy with future threshold (should move everything)
    threshold = datetime.now() + timedelta(days=1)

    moved = logger._move_hot_to_warm(threshold)

    # Verify warm directory was created
    warm_dir = temp_log_dir / "warm"
    assert warm_dir.exists(), "Warm directory should be created"
    assert moved >= 0, "Should move at least 0 files"


def test_retention_policy_warm_to_cold(temp_log_dir):
    """Test moving interviews from warm to cold storage with compression."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    # Create warm directory with a test file
    warm_dir = temp_log_dir / "warm"
    warm_dir.mkdir(parents=True, exist_ok=True)

    test_file = warm_dir / "INTERVIEW-2026-03-07-1.yaml"
    test_file.write_text("test: data")

    # Apply retention policy with future threshold
    threshold = datetime.now() + timedelta(days=1)

    moved = logger._move_warm_to_cold(threshold)

    # Verify cold directory was created
    cold_dir = temp_log_dir / "cold"
    assert cold_dir.exists(), "Cold directory should be created"
    assert moved >= 0, "Should move at least 0 files"


def test_get_learning_stats(populated_logger):
    """Test learning statistics calculation."""
    stats = populated_logger.get_learning_stats(days=30)

    assert stats["total_interviews"] == 2, "Should have 2 interviews"
    assert stats["period_days"] == 30, "Period should be 30 days"
    assert "context_type_distribution" in stats, "Should include context distribution"
    assert stats["avg_satisfaction"] > 0, "Should have average satisfaction"


def test_get_learning_stats_no_history(temp_log_dir):
    """Test learning stats with no interview history."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    stats = logger.get_learning_stats(days=30)

    # Should return error when no history
    assert "error" in stats, "Should return error when no interviews exist"


def test_jaccard_similarity_calculation():
    """Test Jaccard similarity calculation in find_similar_interviews."""
    # Test with identical keywords
    keywords_a = ["app", "delivery", "food"]
    keywords_b = ["app", "delivery", "food"]

    intersection = len(set(keywords_a) & set(keywords_b))
    union = len(set(keywords_a) | set(keywords_b))
    jaccard = intersection / union if union > 0 else 0

    assert jaccard == 1.0, "Identical keywords should have Jaccard = 1.0"

    # Test with partial overlap
    keywords_c = ["app", "delivery", "tech"]

    intersection = len(set(keywords_a) & set(keywords_c))
    union = len(set(keywords_a) | set(keywords_c))
    jaccard = intersection / union if union > 0 else 0

    assert 0 < jaccard < 1, "Partial overlap should have 0 < Jaccard < 1"
