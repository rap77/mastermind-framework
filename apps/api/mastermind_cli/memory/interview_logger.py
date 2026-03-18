"""
Interview Logger for Brain #8 learning system.
Integrates with PRP-009 Evaluation Logger patterns.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Optional
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
        self,
        session_id: str,
        brief_original: str,
        interview_doc: dict[str, Any],
        outcome: dict[str, Any],
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

    def find_similar_interviews(
        self, brief: str, limit: int = 5, min_similarity: float = 0.1
    ) -> List[dict[str, Any]]:
        """
        Find similar past interviews for learning.

        Uses Jaccard similarity + keyword overlap for matching.

        Args:
            brief: Current brief to match against
            limit: Maximum number of similar interviews to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of similar interview summaries sorted by similarity
        """
        if not self.enabled:
            return []

        index_path = self.log_dir / "hot" / "index.yaml"
        if not index_path.exists():
            return []

        try:
            with open(index_path) as f:
                index = yaml.safe_load(f) or {"interviews": []}
        except (yaml.YAMLError, IOError):
            return []

        # Extract keywords from current brief
        current_keywords = set(self._extract_keywords(brief))

        matches = []

        for entry in index.get("interviews", []):
            # Get keywords from entry
            entry_keywords = set(entry.get("keywords", []))

            # Calculate Jaccard similarity
            if len(current_keywords) == 0 or len(entry_keywords) == 0:
                continue

            intersection = len(current_keywords & entry_keywords)
            union = len(current_keywords | entry_keywords)

            jaccard = intersection / union if union > 0 else 0

            # Also count raw keyword overlap
            overlap = len(current_keywords & entry_keywords)

            # Threshold adjustment: need at least min_similarity * 10 keywords
            if overlap >= max(1, min_similarity * 10):
                matches.append(
                    {
                        "interview_id": entry["interview_id"],
                        "similarity_score": round(jaccard, 3),
                        "keyword_overlap": overlap,
                        "summary": entry.get("summary"),
                        "useful_questions": entry.get("useful_questions", []),
                        "context_type": entry.get("context_type"),
                        "timestamp": entry.get("timestamp"),
                        "brief_original": entry.get("brief_original"),
                    }
                )

        # Sort by Jaccard similarity (higher is better)
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

    def _detect_industry(self, interview_doc: dict[str, Any]) -> str:
        """Detect industry from interview document."""
        metadata: dict[str, Any] = interview_doc.get("metadata", {})
        return str(metadata.get("industry", "general"))

    def _count_questions(self, interview_doc: dict[str, Any]) -> int:
        """Count total questions in interview."""
        return len(interview_doc.get("document", {}).get("qa", []))

    def _count_followups(self, interview_doc: dict[str, Any]) -> int:
        """Count questions that had follow-ups."""
        qa = interview_doc.get("document", {}).get("qa", [])
        return sum(1 for q in qa if q.get("follow_up_questions"))

    def _extract_keywords(self, brief: str) -> List[str]:
        """
        Extract keywords from brief for similarity matching.

        Improved version with extended stop words (Spanish + English).
        """
        # Extended stop words (Spanish + English)
        stop_words = {
            # Spanish
            "el",
            "la",
            "de",
            "que",
            "y",
            "a",
            "en",
            "un",
            "es",
            "con",
            "por",
            "para",
            "una",
            "su",
            "los",
            "se",
            "del",
            "las",
            "todo",
            "esta",
            "entre",
            "cuando",
            "muy",
            "sin",
            "sobre",
            "también",
            "pero",
            "como",
            "estar",
            "tienen",
            "desde",
            "este",
            "hasta",
            "tanto",
            "todos",
            "más",
            "hacer",
            "misma",
            "solo",
            "donde",
            "cada",
            "si",
            "nos",
            "al",
            "lo",
            "le",
            "ha",
            "me",
            "han",
            "fue",
            "son",
            "esta",
            # English
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
            "has",
            "have",
            "from",
            "this",
            "that",
            "with",
            "they",
            "will",
            "would",
            "there",
            "their",
            "what",
            "about",
            "which",
            "when",
            "make",
            "like",
            "into",
            "year",
            "your",
            "just",
            "over",
            "also",
            "such",
            "because",
            "these",
            "first",
            "being",
            "through",
            "most",
            "must",
            "able",
        }

        words = brief.lower().split()

        # Filter: keep words > 3 chars, not stop words
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]

        return keywords

    def _calculate_metrics(
        self, interview_doc: dict[str, Any], outcome: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Calculate learning metrics from interview.

        ENHANCED: Add more sophisticated metrics.
        """
        qa = interview_doc.get("document", {}).get("qa", [])

        # Existing metrics
        useful_questions = set(outcome.get("useful_questions", []))
        effectiveness_rate = len(useful_questions) / len(qa) if qa else 0

        confidence_scores = {"high": 3, "medium": 2, "low": 1}
        avg_confidence = (
            sum(confidence_scores.get(q.get("confidence", "medium"), 2) for q in qa)
            / len(qa)
            if qa
            else 2
        )

        followup_rate = self._count_followups(interview_doc) / len(qa) if qa else 0

        # NEW: Additional metrics

        # 1. Question diversity (how many categories covered)
        categories = set(q.get("category") for q in qa if q.get("category"))
        category_diversity = len(categories)

        # 2. Answer length (longer = more detail)
        avg_answer_length = (
            sum(len(q.get("answer", "").split()) for q in qa) / len(qa) if qa else 0
        )

        # 3. Follow-up effectiveness (did follow-ups add value?)
        follow_ups_with_questions = [q for q in qa if q.get("follow_up_questions")]
        follow_up_count = self._count_followups(interview_doc)
        follow_up_effectiveness = (
            len(follow_ups_with_questions) / follow_up_count
            if follow_up_count > 0
            else 0
        )

        # 4. Gap detection rate
        gaps_detected = len(interview_doc.get("document", {}).get("gaps_detected", []))
        gap_rate = gaps_detected / len(qa) if qa else 0

        return {
            # Existing
            "question_effectiveness_rate": round(effectiveness_rate, 2),
            "user_satisfaction_score": self._satisfaction_to_score(
                outcome.get("user_satisfaction") or "medium"
            ),
            "avg_confidence_score": self._confidence_to_label(avg_confidence),
            "followup_rate": round(followup_rate, 2),
            # NEW
            "category_diversity": category_diversity,
            "avg_answer_length": round(avg_answer_length, 1),
            "follow_up_effectiveness": round(follow_up_effectiveness, 2),
            "gap_detection_rate": round(gap_rate, 2),
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

    def _save_json(self, interview_id: str, doc: dict[str, Any]) -> str:
        """Save JSON document and return path."""
        json_dir = self.log_dir / "json" / datetime.now().strftime("%Y-%m")
        json_dir.mkdir(parents=True, exist_ok=True)

        json_path = json_dir / f"{interview_id}.json"
        with open(json_path, "w") as f:
            json.dump(doc, f, indent=2)

        return str(json_path)

    def _generate_summary(self, interview_doc: dict[str, Any]) -> str:
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

    def get_learning_stats(self, days: int = 30) -> dict[str, Any]:
        """
        Get learning statistics for recent interviews.

        Args:
            days: Number of days to look back (default: 30)

        Returns:
            dict[str, Any]ionary with learning statistics
        """
        from datetime import timedelta

        threshold = datetime.now() - timedelta(days=days)

        # Load index
        index_path = self.log_dir / "hot" / "index.yaml"
        if not index_path.exists():
            return {"error": "No interview history found"}

        try:
            with open(index_path) as f:
                index = yaml.safe_load(f) or {"interviews": []}
        except (yaml.YAMLError, IOError):
            return {"error": "Could not read interview index"}

        # Filter recent interviews
        recent = []
        for entry in index.get("interviews", []):
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time > threshold:
                    recent.append(entry)
            except (ValueError, KeyError):
                continue

        if not recent:
            return {"error": "No recent interviews found"}

        # Calculate stats
        total_questions = sum(
            self._count_questions_from_entry(entry) for entry in recent
        )

        total_gaps = sum(
            entry.get("learning_metrics", {}).get("gap_detection_rate", 0)
            * entry.get("interview", {}).get("questions_asked", 0)
            for entry in recent
        )

        # Context type distribution
        context_types: dict[str, int] = {}
        for entry in recent:
            ctx = entry.get("context_type", "unknown")
            context_types[ctx] = context_types.get(ctx, 0) + 1

        # Average satisfaction
        satisfactions = [
            entry.get("learning_metrics", {}).get("user_satisfaction_score", 3)
            for entry in recent
        ]
        avg_satisfaction = (
            sum(satisfactions) / len(satisfactions) if satisfactions else 3
        )

        return {
            "period_days": days,
            "total_interviews": len(recent),
            "total_questions_asked": total_questions,
            "total_gaps_detected": int(total_gaps),
            "context_type_distribution": context_types,
            "avg_satisfaction": round(avg_satisfaction, 1),
            "most_common_context": (
                max(context_types.items(), key=lambda x: x[1])[0]
                if context_types
                else None
            ),
        }

    def _count_questions_from_entry(self, entry: dict[str, Any]) -> int:
        """Helper to count questions from index entry."""
        questions_asked = entry.get("interview", {}).get("questions_asked", 0)
        return int(questions_asked) if questions_asked is not None else 0

    def _update_index(self, log_entry: dict[str, Any]) -> None:
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

    # ========== Retention Policy Methods ==========

    def apply_retention_policy(
        self, hot_days: int = 30, warm_days: int = 90
    ) -> dict[str, Any]:
        """
        Move old interviews to warm/cold storage.

        Args:
            hot_days: Days to keep in hot storage (default: 30)
            warm_days: Days to keep in warm storage (default: 90)

        Returns:
            Summary of retention actions
        """
        now = datetime.now()
        hot_threshold = now - timedelta(days=hot_days)
        warm_threshold = now - timedelta(days=warm_days)

        results = {
            "hot_to_warm": 0,
            "warm_to_cold": 0,
            "cold_deleted": 0,
        }

        # Move hot → warm
        results["hot_to_warm"] = self._move_hot_to_warm(hot_threshold)

        # Move warm → cold
        results["warm_to_cold"] = self._move_warm_to_cold(warm_threshold)

        return results

    def _move_hot_to_warm(self, threshold: datetime) -> int:
        """
        Move interviews older than threshold from hot to warm.

        Args:
            threshold: DateTime threshold for moving files

        Returns:
            Number of files moved
        """
        import shutil

        hot_dir = self.log_dir / "hot"
        warm_dir = self.log_dir / "warm"

        warm_dir.mkdir(parents=True, exist_ok=True)

        if not hot_dir.exists():
            return 0

        moved_count = 0

        # Iterate through monthly subdirectories
        for month_dir in hot_dir.iterdir():
            if not month_dir.is_dir():
                continue

            for interview_file in month_dir.glob("INTERVIEW-*.yaml"):
                try:
                    # Check file timestamp
                    file_mtime = datetime.fromtimestamp(interview_file.stat().st_mtime)

                    if file_mtime < threshold:
                        # Move to warm
                        rel_path = interview_file.relative_to(hot_dir)
                        target_path = warm_dir / rel_path

                        target_path.parent.mkdir(parents=True, exist_ok=True)

                        # Try rename first, fall back to copy + delete
                        try:
                            interview_file.rename(target_path)
                        except (PermissionError, OSError):
                            shutil.copy2(interview_file, target_path)
                            interview_file.unlink()

                        moved_count += 1
                except (OSError, ValueError) as e:
                    # Log error and continue
                    print(f"Warning: Could not move {interview_file.name}: {e}")
                    continue

        return moved_count

    def _move_warm_to_cold(self, threshold: datetime) -> int:
        """
        Move interviews older than threshold from warm to cold.

        Args:
            threshold: DateTime threshold for moving files

        Returns:
            Number of files compressed and moved
        """
        import gzip
        import shutil

        warm_dir = self.log_dir / "warm"
        cold_dir = self.log_dir / "cold"

        cold_dir.mkdir(parents=True, exist_ok=True)

        if not warm_dir.exists():
            return 0

        moved_count = 0

        for interview_file in warm_dir.rglob("INTERVIEW-*.yaml"):
            try:
                file_mtime = datetime.fromtimestamp(interview_file.stat().st_mtime)

                if file_mtime < threshold:
                    # Move to cold (compress to save space)
                    rel_path = interview_file.relative_to(warm_dir)
                    target_path = cold_dir / rel_path

                    # Change extension to .yaml.gz for compressed
                    target_path = target_path.with_suffix(".yaml.gz")

                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Compress and move
                    with open(interview_file, "rb") as f_in:
                        with gzip.open(target_path, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    # Remove original
                    interview_file.unlink()
                    moved_count += 1
            except (OSError, ValueError, gzip.BadGzipFile) as e:
                print(f"Warning: Could not compress {interview_file.name}: {e}")
                continue

        return moved_count

    def cleanup_old_cold_storage(self, days: int = 365) -> int:
        """
        Delete cold storage interviews older than specified days.

        Args:
            days: Days to retain in cold storage (default: 1 year)

        Returns:
            Number of files deleted
        """
        cold_dir = self.log_dir / "cold"
        threshold = datetime.now() - timedelta(days=days)

        if not cold_dir.exists():
            return 0

        deleted_count = 0

        for interview_file in cold_dir.rglob("INTERVIEW-*.yaml.gz"):
            try:
                file_mtime = datetime.fromtimestamp(interview_file.stat().st_mtime)

                if file_mtime < threshold:
                    interview_file.unlink()
                    deleted_count += 1
            except (OSError, ValueError):
                continue

        return deleted_count
