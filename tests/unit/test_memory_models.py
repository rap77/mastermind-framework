"""
Tests for memory/models.py Pydantic v2 migration.

TDD Approach: RED phase - write failing tests first.
"""

import pytest
from datetime import datetime
from mastermind_cli.memory.models import (
    EvaluationVerdict,
    EvaluationScore,
    Issue,
    EvaluationEntry,
)


class TestEvaluationVerdict:
    """Test EvaluationVerdict enum."""

    def test_verdict_values(self):
        """Test that all verdict values are present."""
        assert EvaluationVerdict.APPROVE.value == "APPROVE"
        assert EvaluationVerdict.CONDITIONAL.value == "CONDITIONAL"
        assert EvaluationVerdict.REJECT.value == "REJECT"
        assert EvaluationVerdict.ESCALATE.value == "ESCALATE"


class TestEvaluationScore:
    """Test EvaluationScore model."""

    def test_score_creation(self):
        """Test creating an EvaluationScore."""
        score = EvaluationScore(total=100, max=156, percentage=64.1)
        assert score.total == 100
        assert score.max == 156
        assert score.percentage == 64.1

    def test_score_string_representation(self):
        """Test score __str__ method."""
        score = EvaluationScore(total=100, max=156, percentage=64.1)
        assert str(score) == "100/156 (64%)"


class TestIssue:
    """Test Issue model."""

    def test_issue_creation(self):
        """Test creating an Issue."""
        issue = Issue(
            type="cold-start",
            severity="high",
            description="No data available",
            recommendation="Conduct user interviews"
        )
        assert issue.type == "cold-start"
        assert issue.severity == "high"
        assert issue.description == "No data available"
        assert issue.recommendation == "Conduct user interviews"


class TestEvaluationEntry:
    """Test EvaluationEntry model - backward compatibility."""

    def test_entry_creation_with_all_fields(self):
        """Test creating an EvaluationEntry with all fields."""
        score = EvaluationScore(total=100, max=156, percentage=64.1)
        entry = EvaluationEntry(
            evaluation_id="eval-123",
            timestamp=datetime.utcnow(),
            project="test-project",
            brief="Test brief",
            flow_type="validation_only",
            brains_involved=[1, 7],
            score=score,
            verdict=EvaluationVerdict.CONDITIONAL,
            issues_found=[
                Issue(
                    type="cold-start",
                    severity="high",
                    description="No data",
                    recommendation="Interview users"
                )
            ],
            strengths_found=["Clear value proposition"],
            full_output="Full output text",
            tags=["validation", "product-strategy"]
        )

        assert entry.evaluation_id == "eval-123"
        assert entry.project == "test-project"
        assert entry.brief == "Test brief"
        assert entry.flow_type == "validation_only"
        assert entry.brains_involved == [1, 7]
        assert entry.score.total == 100
        assert entry.verdict == EvaluationVerdict.CONDITIONAL
        assert len(entry.issues_found) == 1
        assert len(entry.strengths_found) == 1
        assert entry.full_output == "Full output text"
        assert entry.tags == ["validation", "product-strategy"]

    def test_to_dict_method(self):
        """Test to_dict() method for YAML serialization."""
        score = EvaluationScore(total=100, max=156, percentage=64.1)
        entry = EvaluationEntry(
            evaluation_id="eval-123",
            timestamp=datetime(2026, 3, 13, 14, 0, 0),
            project="test-project",
            brief="Test brief",
            flow_type="validation_only",
            brains_involved=[1, 7],
            score=score,
            verdict=EvaluationVerdict.CONDITIONAL,
            issues_found=[
                Issue(
                    type="cold-start",
                    severity="high",
                    description="No data",
                    recommendation="Interview users"
                )
            ],
            strengths_found=["Clear value proposition"],
            full_output="Full output text",
            tags=["validation"]
        )

        result = entry.to_dict()

        assert result["evaluation_id"] == "eval-123"
        assert result["timestamp"] == "2026-03-13T14:00:00"
        assert result["project"] == "test-project"
        assert result["brief"] == "Test brief"
        assert result["flow_type"] == "validation_only"
        assert result["brains_involved"] == [1, 7]
        assert result["score"]["total"] == 100
        assert result["score"]["max"] == 156
        assert result["score"]["percentage"] == 64.1
        assert result["verdict"] == "CONDITIONAL"
        assert len(result["issues_found"]) == 1
        assert result["issues_found"][0]["type"] == "cold-start"
        assert result["issues_found"][0]["severity"] == "high"
        assert result["strengths_found"] == ["Clear value proposition"]
        assert result["full_output"] == "Full output text"
        assert result["tags"] == ["validation"]

    def test_from_dict_method(self):
        """Test from_dict() class method for deserialization."""
        data = {
            "evaluation_id": "eval-123",
            "timestamp": "2026-03-13T14:00:00",
            "project": "test-project",
            "brief": "Test brief",
            "flow_type": "validation_only",
            "brains_involved": [1, 7],
            "score": {
                "total": 100,
                "max": 156,
                "percentage": 64.1
            },
            "verdict": "CONDITIONAL",
            "issues_found": [
                {
                    "type": "cold-start",
                    "severity": "high",
                    "description": "No data",
                    "recommendation": "Interview users"
                }
            ],
            "strengths_found": ["Clear value proposition"],
            "full_output": "Full output text",
            "tags": ["validation"]
        }

        entry = EvaluationEntry.from_dict(data)

        assert entry.evaluation_id == "eval-123"
        assert entry.project == "test-project"
        assert entry.brief == "Test brief"
        assert entry.flow_type == "validation_only"
        assert entry.brains_involved == [1, 7]
        assert entry.score.total == 100
        assert entry.score.max == 156
        assert entry.score.percentage == 64.1
        assert entry.verdict == EvaluationVerdict.CONDITIONAL
        assert len(entry.issues_found) == 1
        assert entry.issues_found[0].type == "cold-start"
        assert entry.strengths_found == ["Clear value proposition"]
        assert entry.full_output == "Full output text"
        assert entry.tags == ["validation"]

    def test_round_trip_serialization(self):
        """Test that to_dict -> from_dict preserves data."""
        original = EvaluationEntry(
            evaluation_id="eval-123",
            timestamp=datetime(2026, 3, 13, 14, 0, 0),
            project="test-project",
            brief="Test brief",
            flow_type="validation_only",
            brains_involved=[1, 7],
            score=EvaluationScore(total=100, max=156, percentage=64.1),
            verdict=EvaluationVerdict.CONDITIONAL,
            issues_found=[
                Issue(
                    type="cold-start",
                    severity="high",
                    description="No data",
                    recommendation="Interview users"
                )
            ],
            strengths_found=["Clear value proposition"],
            full_output="Full output text",
            tags=["validation"]
        )

        # Serialize and deserialize
        serialized = original.to_dict()
        restored = EvaluationEntry.from_dict(serialized)

        # Verify all fields match
        assert restored.evaluation_id == original.evaluation_id
        assert restored.project == original.project
        assert restored.brief == original.brief
        assert restored.flow_type == original.flow_type
        assert restored.brains_involved == original.brains_involved
        assert restored.score.total == original.score.total
        assert restored.score.max == original.score.max
        assert restored.score.percentage == original.score.percentage
        assert restored.verdict == original.verdict
        assert len(restored.issues_found) == len(original.issues_found)
        assert restored.issues_found[0].type == original.issues_found[0].type
        assert restored.strengths_found == original.strengths_found
        assert restored.full_output == original.full_output
        assert restored.tags == original.tags

    def test_optional_fields_default_values(self):
        """Test that optional fields have correct defaults."""
        score = EvaluationScore(total=100, max=156, percentage=64.1)
        entry = EvaluationEntry(
            project="test-project",
            brief="Test brief",
            flow_type="validation_only",
            score=score,
            verdict=EvaluationVerdict.APPROVE,
            full_output="Output"
        )

        assert entry.evaluation_id is None
        assert entry.brains_involved == []
        assert entry.issues_found == []
        assert entry.strengths_found == []
        assert entry.tags == []
