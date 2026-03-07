"""
Interview Logger for Brain #8 learning system.
Integrates with PRP-009 Evaluation Logger patterns.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import json


class InterviewLogger:
    """
    Log interviews for learning and improvement.

    Follows same patterns as EvaluationLogger (PRP-009):
    - YAML storage in logs/interviews/hot/YYYY-MM/
    - Index file for quick lookups
    - Multi-format output (JSON + YAML + Markdown)
    """

    def __init__(self, enabled: bool = True, log_dir: Optional[Path] = None):
        """
        Initialize interview logger.

        Args:
            enabled: Whether logging is enabled
            log_dir: Base directory for logs (default: logs/interviews/)
        """
        self.enabled = enabled
        self.log_dir = log_dir or Path("logs/interviews")

    def log_interview(
        self, session_id: str, brief_original: str, interview_doc: Dict, outcome: Dict
    ) -> Optional[str]:
        """
        Log an interview session.

        Args:
            session_id: Unique session identifier
            brief_original: Original user input
            interview_doc: Complete Q&A document (JSON format)
            outcome: Interview outcome metrics

        Returns:
            Path to logged interview file, or None if disabled
        """
        if not self.enabled:
            return None

        # Generate interview ID
        timestamp = datetime.now().strftime("%Y-%m-%d")
        interview_id = f"INTERVIEW-{timestamp}-{self._next_sequence()}"

        # Create log entry
        log_entry = {
            "interview_id": interview_id,
            "timestamp": datetime.now().isoformat(),
            "brain": "brain-08",
            "session_id": session_id,
            "context": {
                "brief_original": brief_original,
                "context_type": self._detect_context_type(brief_original),
                "industry": self._detect_industry(interview_doc),
            },
            "interview": {
                "questions_asked": self._count_questions(interview_doc),
                "duration_minutes": outcome.get("duration_minutes", 0),
                "categories_covered": len(
                    interview_doc.get("document", {}).get("categories", [])
                ),
                "questions_with_followup": self._count_followups(interview_doc),
                "gaps_identified": len(
                    interview_doc.get("document", {}).get("gaps_detected", [])
                ),
            },
            "outcome": {
                "user_satisfaction": outcome.get("user_satisfaction", "medium"),
                "useful_questions": outcome.get("useful_questions", []),
                "failed_questions": outcome.get("failed_questions", []),
                "final_output_quality": outcome.get("final_output_quality", "approved"),
            },
            "qa_document": {
                "json_path": self._save_json(interview_id, interview_doc),
                "summary": self._generate_summary(interview_doc),
            },
            "learning_metrics": self._calculate_metrics(interview_doc, outcome),
        }

        # Save to hot storage
        hot_dir = self.log_dir / "hot" / datetime.now().strftime("%Y-%m")
        hot_dir.mkdir(parents=True, exist_ok=True)

        log_path = hot_dir / f"{interview_id}.yaml"
        with open(log_path, "w") as f:
            yaml.dump(log_entry, f, default_flow_style=False)

        # Update index
        self._update_index(log_entry)

        return str(log_path)

    def find_similar_interviews(self, brief: str, limit: int = 5) -> List[Dict]:
        """
        Find similar past interviews for learning.

        Args:
            brief: Current brief to match against
            limit: Maximum number of similar interviews to return

        Returns:
            List of similar interview summaries with similarity scores
        """
        if not self.enabled:
            return []

        index_path = self.log_dir / "hot" / "index.yaml"
        if not index_path.exists():
            return []

        with open(index_path) as f:
            index = yaml.safe_load(f) or {"interviews": []}

        # Simple keyword matching (can be improved with embeddings in future)
        keywords = self._extract_keywords(brief)

        matches = []
        for entry in index.get("interviews", []):
            entry_keywords = entry.get("keywords", [])
            overlap = len(set(keywords) & set(entry_keywords))
            if overlap > 0:
                matches.append(
                    {
                        "interview_id": entry["interview_id"],
                        "similarity_score": overlap,
                        "summary": entry.get("summary"),
                        "useful_questions": entry.get("useful_questions", []),
                        "timestamp": entry.get("timestamp"),
                    }
                )

        # Sort by similarity and return top N
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:limit]

    # ========== Private Helper Methods ==========

    def _detect_context_type(self, brief: str) -> str:
        """Detect type of interview context from brief."""
        keywords = {
            "feature_spec": ["feature", "funcionalidad", "característica"],
            "technical_design": ["architecture", "arquitectura", "api", "integration"],
            "client_onboarding": ["client", "cliente", "onboarding", "agency"],
            "gap_analysis": ["gap", "falta", "necesito expertise"],
        }

        brief_lower = brief.lower()
        for context_type, kw_list in keywords.items():
            if any(kw in brief_lower for kw in kw_list):
                return context_type

        return "general"

    def _detect_industry(self, interview_doc: Dict) -> str:
        """Detect industry from interview document."""
        metadata = interview_doc.get("metadata", {})
        return metadata.get("industry", "general")

    def _count_questions(self, interview_doc: Dict) -> int:
        """Count total questions in interview."""
        return len(interview_doc.get("document", {}).get("qa", []))

    def _count_followups(self, interview_doc: Dict) -> int:
        """Count questions that had follow-ups."""
        qa = interview_doc.get("document", {}).get("qa", [])
        return sum(1 for q in qa if q.get("follow_up_questions"))

    def _extract_keywords(self, brief: str) -> List[str]:
        """Extract keywords from brief for matching."""
        stop_words = {"el", "la", "de", "que", "y", "a", "en", "un", "es", "con"}
        words = brief.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 3]

    def _calculate_metrics(self, interview_doc: Dict, outcome: Dict) -> Dict:
        """Calculate learning metrics from interview."""
        qa = interview_doc.get("document", {}).get("qa", [])

        # Question effectiveness rate
        useful_questions = set(outcome.get("useful_questions", []))
        effectiveness_rate = len(useful_questions) / len(qa) if qa else 0

        # Average confidence
        confidence_scores = {"high": 3, "medium": 2, "low": 1}
        avg_confidence = (
            sum(confidence_scores.get(q.get("confidence", "medium"), 2) for q in qa)
            / len(qa)
            if qa
            else 2
        )

        # Follow-up rate
        followup_rate = self._count_followups(interview_doc) / len(qa) if qa else 0

        return {
            "question_effectiveness_rate": round(effectiveness_rate, 2),
            "user_satisfaction_score": self._satisfaction_to_score(
                outcome.get("user_satisfaction")
            ),
            "avg_confidence_score": self._confidence_to_label(avg_confidence),
            "followup_rate": round(followup_rate, 2),
        }

    def _satisfaction_to_score(self, satisfaction: str) -> int:
        """Convert satisfaction label to numeric score."""
        mapping = {"low": 1, "medium": 3, "high": 5}
        return mapping.get(satisfaction, 3)

    def _confidence_to_label(self, score: float) -> str:
        """Convert numeric confidence to label."""
        if score >= 2.5:
            return "high"
        elif score >= 1.5:
            return "medium"
        else:
            return "low"

    def _next_sequence(self) -> int:
        """Get next sequence number for interview ID."""
        # Simple implementation - can be improved with atomic counter
        index_path = self.log_dir / "hot" / "index.yaml"
        if index_path.exists():
            with open(index_path) as f:
                index = yaml.safe_load(f) or {"interviews": []}
            return len(index.get("interviews", [])) + 1
        return 1

    def _save_json(self, interview_id: str, doc: Dict) -> str:
        """Save JSON document and return path."""
        json_dir = self.log_dir / "json" / datetime.now().strftime("%Y-%m")
        json_dir.mkdir(parents=True, exist_ok=True)

        json_path = json_dir / f"{interview_id}.json"
        with open(json_path, "w") as f:
            json.dump(doc, f, indent=2)

        return str(json_path)

    def _generate_summary(self, interview_doc: Dict) -> str:
        """Generate human-readable summary for log."""
        qa = interview_doc.get("document", {}).get("qa", [])
        gaps = interview_doc.get("document", {}).get("gaps_detected", [])

        summary_lines = [
            f"Interview for {interview_doc.get('metadata', {}).get('context_type', 'general')}",
            f"- Questions asked: {len(qa)}",
            f"- Gaps identified: {len(gaps)}",
        ]

        if gaps:
            summary_lines.append("\nGaps:")
            for gap in gaps[:3]:  # Limit to first 3
                summary_lines.append(
                    f"- {gap.get('missing_expertise', 'Unknown domain')}"
                )

        return "\n".join(summary_lines)

    def _update_index(self, log_entry: Dict):
        """Update interview index for quick lookup."""
        index_path = self.log_dir / "hot" / "index.yaml"

        if index_path.exists():
            with open(index_path) as f:
                index = yaml.safe_load(f) or {"interviews": []}
        else:
            index = {"interviews": []}

        index["interviews"].append(
            {
                "interview_id": log_entry["interview_id"],
                "timestamp": log_entry["timestamp"],
                "context_type": log_entry["context"]["context_type"],
                "brief_original": log_entry["context"]["brief_original"],
                "keywords": self._extract_keywords(
                    log_entry["context"]["brief_original"]
                ),
                "summary": log_entry["qa_document"]["summary"],
                "useful_questions": log_entry["outcome"]["useful_questions"],
                "learning_metrics": log_entry["learning_metrics"],
            }
        )

        with open(index_path, "w") as f:
            yaml.dump(index, f, default_flow_style=False)
