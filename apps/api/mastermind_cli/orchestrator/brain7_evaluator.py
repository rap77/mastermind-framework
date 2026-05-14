"""Brain #7 Post-Session Evaluator — Growth/Data brain quality scoring.

Evaluates the output of executed brains and returns a quality score plus
actionable insights. Called as a post-session hook in task_runner.py after
each brain flow completes.

Design decisions:
- Brain #7 is stateless: no DB access here, just scoring logic
- quality_score range: 0.0 (poor) – 1.0 (excellent)
- high_value flag: duration > 5 min OR quality_score >= 0.75
- POST to Rust /internal/brain-event for WS fan-out is handled by caller

Architecture:
    task_runner.run_brain_task()
        └─ evaluate_session(brain_id, output, duration_ms)
               └─ Brain7Evaluator.evaluate()
                      └─ returns Brain7EvalResult(quality_score, insights)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

# Duration threshold for high_value flag (5 minutes in milliseconds)
HIGH_VALUE_DURATION_MS = 5 * 60 * 1000

# Quality score threshold for high_value flag
HIGH_VALUE_SCORE_THRESHOLD = 0.75

# Minimum output keys that indicate a substantive response
_SUBSTANTIVE_OUTPUT_KEYS = {
    "recommendation",
    "analysis",
    "strategy",
    "roadmap",
    "user_stories",
    "pain_points",
    "design",
    "insights",
    "features",
    "acceptance_criteria",
}


@dataclass
class Brain7EvalResult:
    """Result of a Brain #7 evaluation.

    Attributes:
        quality_score: Float in [0.0, 1.0]. Higher is better.
        insights: List of actionable insight strings from Brain #7.
        high_value: True if this execution is worth deep-learning from.
    """

    quality_score: float
    insights: list[str] = field(default_factory=list)
    high_value: bool = False

    def __post_init__(self) -> None:
        # Clamp to [0.0, 1.0]
        self.quality_score = max(0.0, min(1.0, self.quality_score))


class Brain7Evaluator:
    """Stateless evaluator implementing Brain #7 (Growth/Data) scoring.

    Scores brain output based on:
    1. Output completeness (has substantive keys)
    2. Output size (non-empty, not a stub)
    3. Status of the execution (success > failure)
    4. Duration (reasonable execution time signals real work)

    This is a heuristic evaluator — a future version can delegate to a
    real Claude API call for semantic quality assessment.
    """

    def evaluate(
        self,
        brain_id: str,
        output_json: dict[str, Any],
        duration_ms: int,
        status: str = "success",
    ) -> Brain7EvalResult:
        """Evaluate a brain execution and return quality score + insights.

        Args:
            brain_id: ID of the executed brain (e.g. "brain-01-product")
            output_json: The brain's output dictionary
            duration_ms: Execution time in milliseconds
            status: Execution status ("success", "failure", "timeout")

        Returns:
            Brain7EvalResult with quality_score, insights, and high_value flag
        """
        insights: list[str] = []
        score = 0.0

        # Base score from status
        if status == "success":
            score += 0.4
        elif status == "timeout":
            score += 0.1
            insights.append(f"Brain {brain_id} timed out — consider increasing timeout")
        else:
            insights.append(f"Brain {brain_id} failed — review error logs")
            return Brain7EvalResult(
                quality_score=0.1,
                insights=insights,
                high_value=False,
            )

        # Score from output completeness
        output_score, output_insights = self._score_output(brain_id, output_json)
        score += output_score
        insights.extend(output_insights)

        # Score from duration (too fast may be stub, too slow may be timeout)
        duration_score, duration_insights = self._score_duration(brain_id, duration_ms)
        score += duration_score
        insights.extend(duration_insights)

        # Determine high_value flag
        high_value = (
            duration_ms >= HIGH_VALUE_DURATION_MS or score >= HIGH_VALUE_SCORE_THRESHOLD
        )

        if high_value:
            insights.append(
                f"Brain {brain_id} marked high_value "
                f"(score={score:.2f}, duration={duration_ms}ms)"
            )

        return Brain7EvalResult(
            quality_score=score,
            insights=insights,
            high_value=high_value,
        )

    def _score_output(
        self, brain_id: str, output_json: dict[str, Any]
    ) -> tuple[float, list[str]]:
        """Score output based on completeness and substance.

        Returns:
            (score_delta, insights) tuple where score_delta is in [0.0, 0.4]
        """
        insights: list[str] = []

        if not output_json:
            insights.append(f"Brain {brain_id} returned empty output")
            return 0.0, insights

        # Check for substantive keys
        output_keys = set(output_json.keys())
        substantive_matches = output_keys & _SUBSTANTIVE_OUTPUT_KEYS
        if substantive_matches:
            insights.append(
                f"Brain {brain_id} produced substantive output: "
                f"{sorted(substantive_matches)}"
            )
            score = min(0.4, 0.1 * len(substantive_matches))
        else:
            # Has some output but not standard keys — partial credit
            output_size = len(json.dumps(output_json))
            if output_size > 100:
                score = 0.2
            else:
                score = 0.1
                insights.append(
                    f"Brain {brain_id} output is minimal ({output_size} chars)"
                )

        return score, insights

    def _score_duration(
        self, brain_id: str, duration_ms: int
    ) -> tuple[float, list[str]]:
        """Score execution duration.

        Too fast (< 100ms) may indicate a stub/mock.
        Reasonable range (100ms – 5min) scores 0.2.
        Very slow (> 5min) may indicate latency issues but not penalized.

        Returns:
            (score_delta, insights) tuple where score_delta is in [0.0, 0.2]
        """
        insights: list[str] = []

        if duration_ms < 100:
            insights.append(
                f"Brain {brain_id} completed in {duration_ms}ms — may be a stub"
            )
            return 0.0, insights

        if duration_ms > HIGH_VALUE_DURATION_MS:
            insights.append(
                f"Brain {brain_id} took {duration_ms / 60000:.1f}min — "
                "consider caching or optimizing"
            )

        return 0.2, insights


def evaluate_session(
    brain_id: str,
    output_json: dict[str, Any],
    duration_ms: int,
    status: str = "success",
) -> Brain7EvalResult:
    """Convenience function for evaluating a single brain session.

    Args:
        brain_id: ID of the executed brain
        output_json: Brain's output dictionary
        duration_ms: Execution time in milliseconds
        status: Execution status ("success", "failure", "timeout")

    Returns:
        Brain7EvalResult with quality_score, insights, high_value
    """
    evaluator = Brain7Evaluator()
    return evaluator.evaluate(
        brain_id=brain_id,
        output_json=output_json,
        duration_ms=duration_ms,
        status=status,
    )
