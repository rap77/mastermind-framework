"""Data Models for evaluation memory system.

Migrated to Pydantic v2 syntax with backward compatibility.
"""

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timezone
from typing import Any
from pydantic import TypeAdapter


class EvaluationVerdict(str, Enum):
    """Verdict of evaluation."""
    APPROVE = "APPROVE"
    CONDITIONAL = "CONDITIONAL"
    REJECT = "REJECT"
    ESCALATE = "ESCALATE"


class EvaluationScore(BaseModel):
    """Score of evaluation."""
    total: int
    max: int
    percentage: float

    def __str__(self) -> str:
        return f"{self.total}/{self.max} ({self.percentage:.0f}%)"


class Issue(BaseModel):
    """Problem detected during evaluation."""
    type: str = Field(..., description="Type of issue (e.g., 'cold-start', 'omtm')")
    severity: str = Field(..., description="Severity level: high, medium, low")
    description: str = Field(..., description="Description of the issue")
    recommendation: str = Field(..., description="Recommended action")


class EvaluationEntry(BaseModel):
    """Complete evaluation entry."""

    evaluation_id: str | None = Field(None, description="Unique evaluation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When evaluation was created")
    project: str = Field(..., description="Project name or identifier")
    brief: str = Field(..., description="Original user brief")
    flow_type: str = Field(..., description="Flow type (validation_only, full_product, etc.)")
    brains_involved: list[int] = Field(default_factory=list, description="List of brain IDs involved")
    score: EvaluationScore = Field(..., description="Evaluation score")
    verdict: EvaluationVerdict = Field(..., description="Final verdict")
    issues_found: list[Issue] = Field(default_factory=list, description="List of issues detected")
    strengths_found: list[str] = Field(default_factory=list, description="List of strengths identified")
    full_output: str = Field(..., description="Complete evaluation output text")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for YAML serialization."""
        return {
            "evaluation_id": self.evaluation_id,
            "timestamp": self.timestamp.isoformat(),
            "project": self.project,
            "brief": self.brief,
            "flow_type": self.flow_type,
            "brains_involved": self.brains_involved,
            "score": {
                "total": self.score.total,
                "max": self.score.max,
                "percentage": self.score.percentage,
            },
            "verdict": self.verdict.value,
            "issues_found": [
                {
                    "type": issue.type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "recommendation": issue.recommendation,
                }
                for issue in self.issues_found
            ],
            "strengths_found": self.strengths_found,
            "full_output": self.full_output,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationEntry":
        """Create EvaluationEntry from YAML dictionary.

        Uses model_validate for proper type validation with Pydantic v2.
        """
        # Extract nested objects
        score_data = data["score"]
        if isinstance(score_data, dict):
            score = EvaluationScore.model_validate(score_data)
        else:
            score = EvaluationScore(**score_data)

        issues_data = data.get("issues_found", [])
        issues = [Issue.model_validate(issue) if isinstance(issue, dict) else Issue(**issue)
                  for issue in issues_data]

        return cls(
            evaluation_id=data.get("evaluation_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            project=data["project"],
            brief=data["brief"],
            flow_type=data["flow_type"],
            brains_involved=data.get("brains_involved", []),
            score=score,
            verdict=EvaluationVerdict(data["verdict"]),
            issues_found=issues,
            strengths_found=data.get("strengths_found", []),
            full_output=data["full_output"],
            tags=data.get("tags", []),
        )
