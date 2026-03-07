"""
Unit tests for InterviewLogger.
"""

import pytest
import yaml
from pathlib import Path
import tempfile
from datetime import datetime
from mastermind_cli.memory.interview_logger import InterviewLogger


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for test logs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_log_interview_creates_file(temp_log_dir):
    """Test that logging creates YAML file."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    sample_doc = {
        "metadata": {"context_type": "feature_spec"},
        "document": {
            "qa": [
                {"question": "Q1", "answer": "A1", "confidence": "high"}
            ],
            "categories": [{"id": "ux"}],
            "gaps_detected": []
        }
    }

    log_path = logger.log_interview(
        session_id="test-001",
        brief_original="test brief",
        interview_doc=sample_doc,
        outcome={"user_satisfaction": "high"}
    )

    assert log_path is not None
    assert Path(log_path).exists()
    assert log_path.endswith(".yaml")

    # Verify content
    with open(log_path) as f:
        content = yaml.safe_load(f)

    assert content["session_id"] == "test-001"
    assert content["brain"] == "brain-08"
    assert content["context"]["brief_original"] == "test brief"


def test_log_interview_disabled(temp_log_dir):
    """Test that disabled logger returns None."""
    logger = InterviewLogger(enabled=False, log_dir=temp_log_dir)

    log_path = logger.log_interview(
        session_id="test-002",
        brief_original="test brief",
        interview_doc={},
        outcome={}
    )

    assert log_path is None


def test_find_similar_interviews(temp_log_dir):
    """Test interview similarity matching."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    # Log a reference interview
    sample_doc = {
        "metadata": {"context_type": "feature_spec", "industry": "saas"},
        "document": {
            "qa": [{"question": "delivery app", "answer": "...", "confidence": "high"}],
            "categories": [],
            "gaps_detected": []
        }
    }

    logger.log_interview(
        session_id="ref-001",
        brief_original="app moderna delivery comida",
        interview_doc=sample_doc,
        outcome={"useful_questions": ["q001"]}
    )

    # Find similar
    matches = logger.find_similar_interviews("app delivery")

    assert len(matches) > 0
    assert matches[0]["similarity_score"] > 0


def test_calculate_metrics(temp_log_dir):
    """Test learning metrics calculation."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    sample_doc = {
        "metadata": {},
        "document": {
            "qa": [
                {"question": "Q1", "answer": "A1", "confidence": "high"},
                {"question": "Q2", "answer": "A2", "confidence": "medium"},
                {"question": "Q3", "answer": "A3", "confidence": "low"}
            ],
            "categories": [],
            "gaps_detected": []
        }
    }

    outcome = {
        "useful_questions": ["q001", "q002"],  # 2 out of 3
        "user_satisfaction": "high"
    }

    log_path = logger.log_interview(
        session_id="metrics-test",
        brief_original="test",
        interview_doc=sample_doc,
        outcome=outcome
    )

    # Verify metrics were calculated
    with open(log_path) as f:
        content = yaml.safe_load(f)

    metrics = content["learning_metrics"]
    assert metrics["question_effectiveness_rate"] == pytest.approx(0.67, rel=0.1)
    assert metrics["user_satisfaction_score"] == 5
    assert metrics["avg_confidence_score"] in ["high", "medium", "low"]


def test_context_type_detection():
    """Test context type detection from brief."""
    logger = InterviewLogger(enabled=False)

    assert logger._detect_context_type("necesito feature de login") == "feature_spec"
    assert logger._detect_context_type("arquitectura de microservicios") == "technical_design"
    assert logger._detect_context_type("onboarding de cliente") == "client_onboarding"
    assert logger._detect_context_type("texto general") == "general"


def test_keyword_extraction():
    """Test keyword extraction for similarity matching."""
    logger = InterviewLogger(enabled=False)

    keywords = logger._extract_keywords("app moderna delivery comida rápida")

    # Words with 4+ characters are kept
    assert "moderna" in keywords
    assert "delivery" in keywords
    assert "comida" in keywords
    assert "rápida" in keywords
    # Short words (<4 chars) and stop words are filtered
    assert "app" not in keywords  # Only 3 chars
    assert "que" not in keywords  # Stop word
    assert "la" not in keywords  # Stop word
