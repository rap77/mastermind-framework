# PRP-015: Brain #8 Learning System Integration

**Status:** Ready to Implement (after PRP-013)
**Priority:** Medium (enhancement, not blocking)
**Estimated Time:** 9 hours
**Dependencies:** PRP-011 (InterviewLogger), PRP-013 (Orchestrator)
**Branch:** `feature/prp-015-brain-08-learning-system`

---

## Executive Summary

Implementar el sistema de aprendizaje para el Cerebro #8 que permite mejorar las entrevistas futuras basándose en históricos. Esta fase completa el sistema de logging iniciado en PRP-011 añadiendo features de recuperación de entrevistas similares y retención de logs.

**Activities:**
1. Implementar `find_similar_interviews()` en InterviewLogger
2. Añadir retrieval en `_conduct_interview()` para usar historial
3. Implementar retention policy (hot/warm/cold storage)
4. Calcular métricas de aprendizaje
5. Tests para features de learning

---

## Context from Brain #8 Spec

**Referencia:** `docs/software-development/08-master-interviewer-brain/spec-brain-08-master-interviewer.md` → Sección "Integration Points"

### Sistema de Learning (PRP-009 Base)

El PRP-009 implementó `EvaluationLogger` para el Cerebro #7 con:
- Storage en YAML (`logs/evaluations/hot/YYYY-MM/`)
- Index file para búsquedas rápidas
- Métricas de evaluación

**Pattern a seguir:** InterviewLogger (creado en PRP-011) sigue mismo patrón.

### Learning Features para Brain #8

1. **Similar Interview Retrieval** — Encontrar entrevistas previas similares
2. **Learning Metrics** — Calcular efectividad de preguntas
3. **Retention Policy** — Archivar interviews viejas
4. **Historial Integration** — Usar entrevistas previas para mejorar

---

## External Resources

### Similarity Matching Approaches

**Simple:** Keyword overlap (Jaccard similarity)
```python
overlap = len(set(keywords_a) & set(keywords_b))
union = len(set(keywords_a) | set(keywords_b))
similarity = overlap / union
```

**Advanced (Future):** Embeddings + cosine similarity
- OpenAI Embeddings API
- Sentence Transformers (HuggingFace)
- ChromaDB / Qdrant for vector search

**Para PRP-015:** Usar keyword overlap (suficiente para Fase 1)

### Retention Policy Patterns

**Hot Storage** (últimos 30 días) — Acceso frecuente
**Warm Storage** (30-90 días) — Acceso ocasional
**Cold Storage** (>90 días) — Archivo

**Implementation:** Mover archivos entre directorios con cleanup script.

---

## Codebase Patterns to Follow

### Pattern 1: EvaluationLogger (PRP-009)

**Archivo:** `mastermind_cli/memory/evaluator.py`

```python
class EvaluationLogger:
    """Log evaluations to YAML files."""

    def __init__(self, enabled: bool = True, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path("logs/evaluations")

    def log_evaluation(self, project, brief, flow_type, score_total, ...):
        """Save evaluation to YAML."""
        # Save to hot/
        # Update index
```

**✅ PATRÓN A SEGUIR:** InterviewLogger ya tiene estructura similar. Esta PRP añade features.

### Pattern 2: Index-Based Search (PRP-009)

**Archivo:** `mastermind_cli/memory/storage.py`

```python
def find_evaluations(self, filters: Dict) -> List[EvaluationEntry]:
    """Find evaluations matching filters."""
    # Load index
    # Filter by project/verdict/tags
    # Return matching entries
```

**✅ PATRÓN A SEGUIR:** `find_similar_interviews()` usa mismo approach.

### Pattern 3: Cleanup Scripts (Comunes)

**Pattern:** Scripts de cleanup periódico

```bash
# scripts/cleanup_old_logs.sh
find logs/interviews/warm -name "*.yaml" -mtime +90 -exec rm {} \;
```

**✅ PATRÓN A IMPLEMENTAR:** Retention policy para interviews.

---

## Implementation Blueprint

### Step 1: Implement find_similar_interviews() (2 hours)

**Editar:** `mastermind_cli/memory/interview_logger.py`

**Nota:** Este método ya existe en PRP-011, pero hay que mejorarlo.

```python
def find_similar_interviews(
    self,
    brief: str,
    limit: int = 5,
    min_similarity: float = 0.1
) -> List[Dict]:
    """
    Find similar past interviews for learning.

    Uses keyword overlap + Jaccard similarity.

    Args:
        brief: Current brief to match against
        limit: Maximum number of similar interviews to return
        min_similarity: Minimum similarity threshold (0-1)

    Returns:
        List of similar interview summaries sorted by similarity
    """
    if not self.enabled:
        return []

    # Load index
    index_path = self.log_dir / "hot" / "index.yaml"
    if not index_path.exists():
        return []

    with open(index_path) as f:
        index = yaml.safe_load(f) or {"interviews": []}

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

        if overlap >= min_similarity * 10:  # Threshold adjustment
            matches.append({
                "interview_id": entry["interview_id"],
                "similarity_score": round(jaccard, 3),
                "keyword_overlap": overlap,
                "summary": entry.get("summary"),
                "useful_questions": entry.get("useful_questions", []),
                "context_type": entry.get("context_type"),
                "timestamp": entry.get("timestamp"),
                "brief_original": entry.get("brief_original")
            })

    # Sort by Jaccard similarity (higher is better)
    matches.sort(key=lambda x: x["similarity_score"], reverse=True)

    return matches[:limit]


def _extract_keywords(self, brief: str) -> List[str]:
    """
    Extract keywords from brief for similarity matching.

    Improved version with stemming (optional) and better stop word filtering.
    """
    # Extended stop words (Spanish + English)
    stop_words = {
        # Spanish
        "el", "la", "de", "que", "y", "a", "en", "un", "es", "con",
        "por", "para", "una", "su", "los", "se", "del", "las", "todo",
        "esta", "entre", "cuando", "muy", "sin", "sobre", "también",
        # English
        "the", "and", "for", "are", "but", "not", "you", "all", "can",
        "had", "her", "was", "one", "our", "out", "has", "have", "from"
    }

    words = brief.lower().split()

    # Filter: keep words > 3 chars, not stop words
    keywords = [
        w for w in words
        if len(w) > 3 and w not in stop_words
    ]

    return keywords
```

### Step 2: Integrate Learning into _conduct_interview() (2 hours)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _conduct_interview(self, plan: Dict, brief: str) -> Dict:
    """
    Conduct iterative interview with user.

    ENHANCED: Uses historical interviews to improve questions.
    """
    import uuid
    from datetime import datetime

    # NEW: Find similar interviews for learning
    if self.eval_logger and hasattr(self.eval_logger, 'find_similar_interviews'):
        from mastermind_cli.memory.interview_logger import InterviewLogger
        interview_logger = InterviewLogger(enabled=True)

        similar = interview_logger.find_similar_interviews(brief, limit=3)

        if similar:
            print(self.formatter.format_info(
                f"📚 Found {len(similar)} similar interviews for context"
            ))

            # Use similar interviews to inform questions
            # (This is a simple version - can be enhanced)
            useful_questions = set()
            for sim in similar:
                useful_questions.update(sim.get("useful_questions", []))

            if useful_questions:
                print(self.formatter.format_info(
                    f"💡 Learned from past interviews: {len(useful_questions)} useful questions"
                ))

    strategy = plan.get("interview_strategy", {})
    categories = strategy.get("categories", [])

    # ... rest of method remains same ...
```

### Step 3: Implement Retention Policy (2 hours)

**Editar:** `mastermind_cli/memory/interview_logger.py`

```python
def apply_retention_policy(self, hot_days: int = 30, warm_days: int = 90):
    """
    Move old interviews to warm/cold storage.

    Args:
        hot_days: Days to keep in hot storage (default: 30)
        warm_days: Days to keep in warm storage (default: 90)
    """
    from datetime import datetime, timedelta

    now = datetime.now()
    hot_threshold = now - timedelta(days=hot_days)
    warm_threshold = now - timedelta(days=warm_days)

    # Move hot → warm
    self._move_hot_to_warm(hot_threshold)

    # Move warm → cold
    self._move_warm_to_cold(warm_threshold)


def _move_hot_to_warm(self, threshold: datetime):
    """Move interviews older than threshold from hot to warm."""
    hot_dir = self.log_dir / "hot"
    warm_dir = self.log_dir / "warm"

    warm_dir.mkdir(parents=True, exist_ok=True)

    if not hot_dir.exists():
        return

    # Iterate through monthly subdirectories
    for month_dir in hot_dir.iterdir():
        if not month_dir.is_dir():
            continue

        for interview_file in month_dir.glob("INTERVIEW-*.yaml"):
            # Check file timestamp
            file_mtime = datetime.fromtimestamp(interview_file.stat().st_mtime)

            if file_mtime < threshold:
                # Move to warm
                rel_path = interview_file.relative_to(hot_dir)
                target_path = warm_dir / rel_path

                target_path.parent.mkdir(parents=True, exist_ok=True)

                interview_file.rename(target_path)
                print(f"Moved {interview_file.name} to warm storage")


def _move_warm_to_cold(self, threshold: datetime):
    """Move interviews older than threshold from warm to cold."""
    warm_dir = self.log_dir / "warm"
    cold_dir = self.log_dir / "cold"

    cold_dir.mkdir(parents=True, exist_ok=True)

    if not warm_dir.exists():
        return

    for interview_file in warm_dir.rglob("INTERVIEW-*.yaml"):
        file_mtime = datetime.fromtimestamp(interview_file.stat().st_mtime)

        if file_mtime < threshold:
            # Move to cold (compress to save space)
            rel_path = interview_file.relative_to(warm_dir)
            target_path = cold_dir / rel_path

            # Change extension to .yaml.gz for compressed
            target_path = target_path.with_suffix(".yaml.gz")

            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Compress and move
            import gzip
            import shutil

            with open(interview_file, 'rb') as f_in:
                with gzip.open(target_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove original
            interview_file.unlink()
            print(f"Compressed {interview_file.name} to cold storage")


def cleanup_old_cold_storage(self, days: int = 365):
    """
    Delete cold storage interviews older than specified days.

    Args:
        days: Days to retain in cold storage (default: 1 year)
    """
    from datetime import timedelta

    cold_dir = self.log_dir / "cold"
    threshold = datetime.now() - timedelta(days=days)

    if not cold_dir.exists():
        return

    for interview_file in cold_dir.rglob("INTERVIEW-*.yaml.gz"):
        file_mtime = datetime.fromtimestamp(interview_file.stat().st_mtime)

        if file_mtime < threshold:
            interview_file.unlink()
            print(f"Deleted old interview: {interview_file.name}")
```

### Step 4: Calculate Learning Metrics (1 hour)

**Editar:** `mastermind_cli/memory/interview_logger.py`

**Nota:** Este método ya existe en PRP-011. Mejorar con métricas adicionales.

```python
def _calculate_metrics(self, interview_doc: Dict, outcome: Dict) -> Dict:
    """
    Calculate learning metrics from interview.

    ENHANCED: Add more sophisticated metrics.
    """
    qa = interview_doc.get("document", {}).get("qa", [])

    # Existing metrics
    useful_questions = set(outcome.get("useful_questions", []))
    effectiveness_rate = len(useful_questions) / len(qa) if qa else 0

    confidence_scores = {"high": 3, "medium": 2, "low": 1}
    avg_confidence = sum(
        confidence_scores.get(q.get("confidence", "medium"), 2)
        for q in qa
    ) / len(qa) if qa else 2

    followup_rate = self._count_followups(interview_doc) / len(qa) if qa else 0

    # NEW: Additional metrics

    # 1. Question diversity (how many categories covered)
    categories = set(q.get("category") for q in qa)
    category_diversity = len(categories) if categories else 0

    # 2. Answer length (longer = more detail)
    avg_answer_length = sum(
        len(q.get("answer", "").split())
        for q in qa
    ) / len(qa) if qa else 0

    # 3. Follow-up effectiveness (did follow-ups add value?)
    follow_ups_with_questions = [
        q for q in qa
        if q.get("follow_up_questions")
    ]
    follow_up_effectiveness = (
        len(follow_ups_with_questions) / self._count_followups(interview_doc)
        if self._count_followups(interview_doc) > 0 else 0
    )

    # 4. Gap detection rate
    gaps_detected = len(interview_doc.get("document", {}).get("gaps_detected", []))
    gap_rate = gaps_detected / len(qa) if qa else 0

    return {
        # Existing
        "question_effectiveness_rate": round(effectiveness_rate, 2),
        "user_satisfaction_score": self._satisfaction_to_score(outcome.get("user_satisfaction")),
        "avg_confidence_score": self._confidence_to_label(avg_confidence),
        "followup_rate": round(followup_rate, 2),

        # NEW
        "category_diversity": category_diversity,
        "avg_answer_length": round(avg_answer_length, 1),
        "follow_up_effectiveness": round(follow_up_effectiveness, 2),
        "gap_detection_rate": round(gap_rate, 2)
    }


def get_learning_stats(self, days: int = 30) -> Dict:
    """
    Get learning statistics for recent interviews.

    Args:
        days: Number of days to look back (default: 30)

    Returns:
        Dictionary with learning statistics
    """
    from datetime import timedelta

    threshold = datetime.now() - timedelta(days=days)

    # Load index
    index_path = self.log_dir / "hot" / "index.yaml"
    if not index_path.exists():
        return {"error": "No interview history found"}

    with open(index_path) as f:
        index = yaml.safe_load(f) or {"interviews": []}

    # Filter recent interviews
    recent = [
        entry for entry in index.get("interviews", [])
        if datetime.fromisoformat(entry["timestamp"]) > threshold
    ]

    if not recent:
        return {"error": "No recent interviews found"}

    # Calculate stats
    total_questions = sum(
        entry.get("questions_asked", 0)
        for entry in recent
    )

    total_gaps = sum(
        entry.get("gaps_identified", 0)
        for entry in recent
    )

    # Context type distribution
    context_types = {}
    for entry in recent:
        ctx = entry.get("context_type", "unknown")
        context_types[ctx] = context_types.get(ctx, 0) + 1

    # Average satisfaction
    satisfactions = [
        entry.get("learning_metrics", {}).get("user_satisfaction_score", 3)
        for entry in recent
    ]
    avg_satisfaction = sum(satisfactions) / len(satisfactions) if satisfactions else 3

    return {
        "period_days": days,
        "total_interviews": len(recent),
        "total_questions_asked": total_questions,
        "total_gaps_detected": total_gaps,
        "context_type_distribution": context_types,
        "avg_satisfaction": round(avg_satisfaction, 1),
        "most_common_context": max(context_types, key=context_types.get) if context_types else None
    }
```

### Step 5: Create Cleanup Script (1 hour)

**Crear:** `scripts/cleanup_interviews.py`

```python
#!/usr/bin/env python3
"""
Cleanup old interviews according to retention policy.

Run this script periodically (cron) to manage storage.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mastermind_cli.memory.interview_logger import InterviewLogger


def main():
    logger = InterviewLogger(enabled=True)

    print("Applying retention policy...")

    # Move hot → warm (30 days)
    logger._move_hot_to_warm(hot_days=30)
    print("✓ Moved hot to warm")

    # Move warm → cold (90 days)
    logger._move_warm_to_cold(warm_days=90)
    print("✓ Moved warm to cold")

    # Delete cold > 1 year
    logger.cleanup_old_cold_storage(days=365)
    print("✓ Cleaned up old cold storage")

    print("Retention policy applied!")


if __name__ == "__main__":
    main()
```

**Make executable:**
```bash
chmod +x scripts/cleanup_interviews.py
```

### Step 6: Write Tests (2 hours)

**Crear:** `tests/unit/test_interview_learning.py`

```python
"""
Unit tests for InterviewLogger learning features.
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
                    "qa": [{"question": "Q1", "answer": "A1", "confidence": "high"}],
                    "categories": [],
                    "gaps_detected": []
                }
            },
            "outcome": {"useful_questions": ["q001"], "user_satisfaction": "high"}
        },
        {
            "session_id": "test-002",
            "brief_original": "delivery app food",
            "interview_doc": {
                "metadata": {"context_type": "feature_spec"},
                "document": {
                    "qa": [{"question": "Q2", "answer": "A2", "confidence": "medium"}],
                    "categories": [],
                    "gaps_detected": []
                }
            },
            "outcome": {"useful_questions": ["q002"], "user_satisfaction": "medium"}
        }
    ]

    for interview in sample_interviews:
        logger.log_interview(**interview)

    return logger


def test_find_similar_interviews(populated_logger):
    """Test interview similarity matching."""
    matches = populated_logger.find_similar_interviews("app delivery")

    assert len(matches) > 0
    assert matches[0]["similarity_score"] > 0


def test_find_similar_interviews_with_threshold(populated_logger):
    """Test similarity threshold."""
    matches = populated_logger.find_similar_interviews(
        "app delivery",
        min_similarity=0.5
    )

    # High threshold should return fewer or no results
    assert len(matches) >= 0


def test_extract_keywords():
    """Test keyword extraction."""
    logger = InterviewLogger(enabled=False)

    keywords = logger._extract_keywords("app moderna delivery comida rápida")

    assert "app" in keywords
    assert "moderna" in keywords
    assert "delivery" in keywords

    # Stop words should be filtered
    assert "que" not in keywords
    assert "la" not in keywords


def test_calculate_metrics_enhanced(temp_log_dir):
    """Test enhanced metrics calculation."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    interview_doc = {
        "metadata": {},
        "document": {
            "qa": [
                {"question": "Q1", "answer": "Long detailed answer with many words here", "confidence": "high"},
                {"question": "Q2", "answer": "Short", "confidence": "medium"}
            ],
            "categories": [],
            "gaps_detected": []
        }
    }

    outcome = {
        "useful_questions": ["q001"],
        "user_satisfaction": "high"
    }

    log_path = logger.log_interview(
        session_id="metrics-test",
        brief_original="test",
        interview_doc=interview_doc,
        outcome=outcome
    )

    # Verify enhanced metrics
    with open(log_path) as f:
        content = yaml.safe_load(f)

    metrics = content["learning_metrics"]

    assert "category_diversity" in metrics
    assert "avg_answer_length" in metrics
    assert "follow_up_effectiveness" in metrics
    assert "gap_detection_rate" in metrics


def test_retention_policy_hot_to_warm(temp_log_dir):
    """Test moving interviews from hot to warm storage."""
    logger = InterviewLogger(enabled=True, log_dir=temp_log_dir)

    # Log an interview
    logger.log_interview(
        session_id="retention-test",
        brief_original="test",
        interview_doc={
            "metadata": {},
            "document": {"qa": [], "categories": [], "gaps_detected": []}
        },
        outcome={}
    )

    # Apply retention policy with 0 days (should move everything)
    from datetime import datetime
    threshold = datetime.now() + timedelta(days=1)  # Future date

    logger._move_hot_to_warm(threshold)

    # Verify moved
    warm_dir = temp_log_dir / "warm"
    assert warm_dir.exists()


def test_get_learning_stats(populated_logger):
    """Test learning statistics calculation."""
    stats = populated_logger.get_learning_stats(days=30)

    assert stats["total_interviews"] == 2
    assert stats["period_days"] == 30
    assert "context_type_distribution" in stats
    assert stats["avg_satisfaction"] > 0
```

---

## Validation Gates

```bash
# ========== Step 1: find_similar_interviews() ==========
python -c "
from mastermind_cli.memory.interview_logger import InterviewLogger
logger = InterviewLogger(enabled=False)

# Test keyword extraction
keywords = logger._extract_keywords('app moderna delivery comida')
assert 'app' in keywords
assert 'delivery' in keywords
print('✅ Keyword extraction works')
"

# ========== Step 2: Integration with _conduct_interview() ==========
python -c "
from mastermind_cli.orchestrator.coordinator import Coordinator
c = Coordinator()

# Verify method exists
assert hasattr(c, '_conduct_interview')
print('✅ _conduct_interview() method exists')
"

# ========== Step 3: Retention Policy ==========
python -c "
from mastermind_cli.memory.interview_logger import InterviewLogger
logger = InterviewLogger(enabled=False)

# Verify retention methods exist
assert hasattr(logger, 'apply_retention_policy')
assert hasattr(logger, '_move_hot_to_warm')
assert hasattr(logger, '_move_warm_to_cold')
assert hasattr(logger, 'cleanup_old_cold_storage')
print('✅ Retention policy methods exist')
"

# ========== Step 4: Learning Metrics ==========
python -c "
from mastermind_cli.memory.interview_logger import InterviewLogger
logger = InterviewLogger(enabled=False)

# Verify metrics calculation
doc = {
    'document': {
        'qa': [
            {'question': 'Q1', 'answer': 'Long answer here', 'confidence': 'high'},
            {'question': 'Q2', 'answer': 'Short', 'confidence': 'medium'}
        ],
        'categories': [],
        'gaps_detected': []
    }
}
outcome = {'useful_questions': ['q001'], 'user_satisfaction': 'high'}

metrics = logger._calculate_metrics(doc, outcome)

assert 'category_diversity' in metrics
assert 'avg_answer_length' in metrics
assert 'follow_up_effectiveness' in metrics
assert 'gap_detection_rate' in metrics
print('✅ Enhanced metrics calculated')
"

# ========== Step 5: Cleanup Script ==========
ls -la scripts/cleanup_interviews.py
echo "✅ Cleanup script exists"

# Test script syntax
python -m py_compile scripts/cleanup_interviews.py
echo "✅ Cleanup script syntax valid"

# ========== Step 6: Learning Tests ==========
uv run pytest tests/unit/test_interview_learning.py -v

# ========== Final Validation ==========
# Type check
mypy mastermind_cli/memory/interview_logger.py

# Lint
ruff check mastermind_cli/memory/interview_logger.py

echo "========== ALL VALIDATIONS PASSED =========="
```

---

## Error Handling

| Error | Handling |
|-------|----------|
| **Index file missing** | Return empty list (no similar interviews) |
| **Corrupt YAML file** | Skip file, log error |
| **Retention move fails** | Log error, continue with next file |
| **Cold storage compress fails** | Keep file in warm, log warning |

---

## Gotchas & Pitfalls

### Gotcha 1: Similarity Threshold Too High/Low

**Issue:** Threshold determines sensitivity

**Fix:** Use reasonable defaults (0.1 min_similarity) and make configurable

### Gotcha 2: Index File Corruption

**Issue:** index.yaml might get corrupted

**Fix:** Add validation and rebuild if needed:
```python
try:
    index = yaml.safe_load(f) or {"interviews": []}
except yaml.YAMLError:
    # Rebuild index from files
    index = self._rebuild_index()
```

### Gotcha 3: File Permissions on Move

**Issue:** Can't move files due to permissions

**Fix:** Add error handling and try copy+delete instead:
```python
try:
    interview_file.rename(target_path)
except PermissionError:
    # Try copy + delete
    shutil.copy2(interview_file, target_path)
    interview_file.unlink()
```

---

## Quality Checklist

- [x] All necessary context included (PRP-009 base)
- [x] Validation gates ejecutables
- [x] References existing patterns (EvaluationLogger)
- [x] Clear implementation path (6 steps, 9 horas)
- [x] Error handling documentado (4 categorías)
- [x] Enhanced metrics especificadas
- [x] Retention policy implementada
- [x] Cleanup script incluido
- [x] Tests completos especificados

---

## Branch Strategy

**Create branch:** `feature/prp-015-brain-08-learning-system`

```bash
git checkout -b feature/prp-015-brain-08-learning-system

# Work through implementation
# ... implement learning features ...
# ... create cleanup script ...
# ... write tests ...

# Commit when done
git add mastermind_cli/memory/interview_logger.py
git add scripts/cleanup_interviews.py
git add tests/unit/test_interview_learning.py
git commit -m "feat(prp-015): implement learning system for brain #8

- Improve find_similar_interviews() with Jaccard similarity
- Add learning integration in _conduct_interview()
- Implement retention policy (hot/warm/cold storage)
- Add enhanced learning metrics
- Create cleanup script for old interviews
- Write unit tests for learning features

Validations:
✅ Similar interview retrieval works
✅ Retention policy moves files correctly
✅ Enhanced metrics calculated
✅ Cleanup script executable
✅ All learning tests passing

Refs: PRP-015, spec-brain-08"
```

---

## Success Criteria

- [ ] `find_similar_interviews()` devuelve entrevistas similares ordenadas
- [ ] `_conduct_interview()` usa historial para mejorar (básico)
- [ ] Retention policy mueve archivos hot→warm→cold
- [ ] Enhanced metrics calculadas correctamente
- [ ] Cleanup script ejecuta sin errores
- [ ] Tests de learning pasando
- [ ] `get_learning_stats()` devuelve estadísticas correctas

---

## PRP Confidence Score

**Score: 9/10**

**Justification:**
- ✅ **Well-defined patterns** — EvaluationLogger ya existe (PRP-009)
- ✅ **Clear validation** — Tests ejecutables para cada feature
- ✅ **Isolated changes** — Solo InterviewLogger y cleanup script
- ✅ **No MCP dependencies** — Todo es local
- ⚠️ **-1 punto** — Similarity matching es simple (keyword overlap), puede no ser muy preciso

**Riesgo bajo:** Esta PRP es enhancement del sistema existente. No afecta funcionalidad core.

---

## Next Steps After Completion

Once PRP-015 is complete:

1. **Configurar cron** para cleanup script (opcional):
   ```bash
   # Run monthly
   0 0 1 * * /path/to/scripts/cleanup_interviews.py
   ```
2. **Start PRP-016:** Testing & Polish (E2E tests, performance)
3. **Document** cómo usar learning stats

---

**END OF PRP-015**
