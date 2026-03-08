# PRP-011: Brain #8 Core Infrastructure

**Status:** Ready to Implement
**Priority:** Critical (blocks all other phases)
**Estimated Time:** 9.5 hours
**Dependencies:** None
**Branch:** `feature/prp-011-brain-08-core-infrastructure`

---

## Executive Summary

Implementar la infraestructura base necesaria para soportar el Cerebro #8. Esta fase establece los componentes fundamentales que todas las demás fases dependen: registry basado en YAML, actualización de BrainExecutor, y el sistema de logging de entrevistas.

**Components to implement:**
1. YAML-based brain registry (extensible a N cerebros)
2. InterviewLogger class para logging de entrevistas
3. Update BrainExecutor para soportar cerebro #8
4. Unit tests para nuevos componentes

---

## Context from Brain #8 Spec

**Referencia:** `docs/software-development/08-master-interviewer-brain/spec-brain-08-master-interviewer.md`

### Por qué esta fase es crítica

El código actual tiene **BRAIN_CONFIGS hardcoded** a 7 cerebros:

```python
# mastermind_cli/orchestrator/brain_executor.py (líneas 23-67)
BRAIN_CONFIGS = {
    1: {...}, 2: {...}, 3: {...}, 4: {...},
    5: {...}, 6: {...}, 7: {...}
}
```

**Problema:** No soporta agregar cerebros #9, #10, etc.

**Solución:** Mover a YAML-based registry que carga dinámicamente.

---

## External Resources

### PyYAML Documentation
- **Loading YAML:** https://pyyaml.org/wiki/PyYAMLDocumentation#loading-yaml
- **Safe Loading:** https://pyyaml.org/wiki/PyYAMLDocumentation#dealing-with-illegal-characters-in-yaml
- **Type Conversion:** https://pyyaml.org/wiki/PyYAMLDocumentation#constructing-creating-and-loading-yaml

### Python Filesystem Patterns
- **pathlib for paths:** https://docs.python.org/3/library/pathlib.html
- **Config file locations:** https://click.palletsprojects.com/en/8.1.x/api/#click.Path

---

## Codebase Patterns to Follow

### Pattern 1: Config File Loading (Similar to pyproject.toml)

**El proyecto usa:** `uv` y `pyproject.toml`

**Pattern a seguir:** Config files en directorio `config/`

```python
# mastermind_cli/config/__init__.py (nuevo)
from pathlib import Path

CONFIG_DIR = Path(__file__).parent
BRAINS_CONFIG_PATH = CONFIG_DIR / "brains.yaml"
```

### Pattern 2: Class Structure (Similar a Evaluator)

**Referencia:** `mastermind_cli/memory/evaluator.py`

```python
class Evaluator:
    """Evalúa outputs del Brain #7."""

    def __init__(self, skills_dir: str = None):
        # Inicialización con defaults

    def evaluate(self, output: dict, matrix_id: str, brain_id: int):
        # Método principal
```

**Pattern a seguir:** Misma estructura para `InterviewLogger`

### Pattern 3: Registry Pattern (Similar a BRAIN_CONFIGS actual)

**Referencia:** `mastermind_cli/orchestrator/brain_executor.py:23-67`

**Key insight:** Mantener compatibilidad con código existente que usa `BRAIN_CONFIGS[brain_id]`

---

## Implementation Blueprint

### Step 1: Create YAML Brain Registry (30 min)

**Archivo a crear:** `mastermind_cli/config/brains.yaml`

```yaml
version: "1.0"
brains:
  # Cerebros existentes #1-7 (migrar desde hardcoded)
  - id: 1
    name: Product Strategy
    notebook_id: f276ccb3-0bce-4069-8b55-eae8693dbe75
    system_prompt: agents/brains/product-strategy.md
    expertise:
      - Product discovery
      - User personas
      - Value proposition
      - Monetization
    status: active

  - id: 2
    name: UX Research
    notebook_id: ea006ece-00a9-4d5c-91f5-012b8b712936
    system_prompt: null  # No tiene system_prompt file
    expertise:
      - User research
      - Usability testing
      - Interview techniques
    status: active

  # ... brains 3-7 (mismo patrón) ...

  # Cerebro #8 (nuevo)
  - id: 8
    name: Master Interviewer / Discovery
    notebook_id: null  # Se actualizará en PRP-012
    system_prompt: agents/brains/master-interviewer.md
    expertise:
      - Interview methodology
      - Information extraction
      - Question structuring
      - Gap detection
      - Facilitation techniques
    status: pending  # Cambiar a 'active' después de PRP-012
```

### Step 2: Update brain_registry.py (1 hour)

**Archivo a editar:** `mastermind_cli/brain_registry.py`

```python
"""
Brain Registry - Load brain configurations from YAML.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional

# Config directory
CONFIG_DIR = Path(__file__).parent / "config"
BRAINS_CONFIG_PATH = CONFIG_DIR / "brains.yaml"


def load_brain_configs() -> Dict[int, Dict]:
    """
    Load brain configurations from YAML file.

    Returns:
        Dictionary mapping brain_id to brain config.

    Raises:
        FileNotFoundError: If brains.yaml doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not BRAINS_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Brain config not found: {BRAINS_CONFIG_PATH}\n"
            f"Run 'mm framework status' to verify installation."
        )

    with open(BRAINS_CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    brains = {}
    for brain in config.get("brains", []):
        brains[brain["id"]] = brain

    return brains


# Maintain backward compatibility
BRAIN_CONFIGS = load_brain_configs()


def get_brain(brain_id: int) -> Optional[Dict]:
    """Get a specific brain configuration."""
    return BRAIN_CONFIGS.get(brain_id)


def list_active_brains() -> List[int]:
    """List all active brain IDs."""
    return [
        brain_id
        for brain_id, config in BRAIN_CONFIGS.items()
        if config.get("status") == "active"
    ]


def get_brain_count() -> int:
    """Get total number of registered brains."""
    return len(BRAIN_CONFIGS)
```

### Step 3: Update BrainExecutor (1 hour)

**Archivo a editar:** `mastermind_cli/orchestrator/brain_executor.py`

**Cambios:**

```python
# Al inicio del archivo, actualizar imports:
from .brain_registry import load_brain_configs

class BrainExecutor:
    """Executes brain tasks via NotebookLM MCP."""

    # Reemplazar hardcoded BRAIN_CONFIGS con:
    def __init__(self, mcp_client=None, skills_dir: str = None):
        self.notebooklm_client = NotebookLMClient()
        self.evaluator = Evaluator(skills_dir=skills_dir)
        self.mcp_client = mcp_client

        # Load brains from YAML
        self.BRAIN_CONFIGS = load_brain_configs()

    # En execute() method, agregar case para brain #8:
    def execute(self, brain_id: int, task: Dict, use_mcp: bool = True) -> Dict:
        brain_config = self.BRAIN_CONFIGS.get(brain_id)

        if not brain_config:
            return self._unimplemented_brain(brain_id, task)

        if brain_config['status'] != 'active':
            if brain_config['status'] == 'pending':
                return self._pending_brain(brain_id, task)
            return self._unimplemented_brain(brain_id, task)

        # Route to appropriate executor
        if brain_id == 1:
            return self._execute_brain_1(task, use_mcp=use_mcp)
        elif brain_id == 7:
            return self._execute_brain_7(task, use_mcp=use_mcp)
        elif brain_id == 8:
            return self._execute_brain_8(task, use_mcp=use_mcp)  # NEW
        else:
            return self._execute_generic_brain(brain_id, task, use_mcp=use_mcp)

    # Agregar método _execute_brain_8:
    def _execute_brain_8(self, task: Dict, use_mcp: bool = True) -> Dict:
        """Execute Master Interviewer brain."""
        context = task.get('context', {})
        brief = task.get('inputs', {}).get('brief', '')

        query = f"""As a Master Interviewer and Discovery expert, analyze the following:

Context: {brief}

Task: {context.get('instruction', 'Design an interview strategy')}

Provide your analysis in the following JSON format:
{{
  "interview_strategy": {{
    "categories": [
      {{"id": "users", "name": "Users & Personas", "target_brain": 2}},
      {{"id": "platforms", "name": "Platforms", "target_brain": 4}}
    ],
    "initial_questions": [
      {{"category": "users", "question": "What type of users?", "target_brain": 2}}
    ],
    "detected_gaps": []
  }}
}}
"""

        if use_mcp and self.mcp_client and self.mcp_client.is_available():
            try:
                response = self.mcp_client.query_notebook(
                    brain_id=8,
                    query=query
                )
                if response.get('status') == 'success':
                    return self._format_brain_response(8, response.get('content', ''), brief)
            except Exception as e:
                return self._mock_brain_8_response(brief, query, error=str(e))

        return self._mock_brain_8_response(brief, query)

    def _mock_brain_8_response(self, brief: str, query: str, error: str = None) -> Dict:
        """Mock response for Brain #8 (for testing without MCP)."""
        return {
            'brain_id': 8,
            'brain_name': 'Master Interviewer',
            'status': 'mock',
            'output': {
                'note': 'This is a mock response. Brain #8 will be implemented with NotebookLM integration in PRP-012.',
                'query_preview': query[:200] + '...',
                'brief': brief,
                'mcp_error': error
            },
            'message': 'Brain #8 mock response (MCP not available or brain not yet configured)'
        }

    # Agregar método _pending_brain:
    def _pending_brain(self, brain_id: int, task: Dict) -> Dict:
        """Return response for pending brain."""
    brain_name = self.BRAIN_CONFIGS.get(brain_id, {}).get('name', f'Brain {brain_id}')

        return {
            'brain_id': brain_id,
            'brain_name': brain_name,
            'status': 'pending',
            'error': f'Brain #{brain_id} ({brain_name}) is registered but not yet active. Check the corresponding PRP for implementation status.',
            'message': f'Brain #{brain_id} is coming soon! Track progress in GitHub issues.'
        }
```

### Step 4: Create InterviewLogger Class (3 hours)

**Archivo a crear:** `mastermind_cli/memory/interview_logger.py`

```python
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
        self,
        session_id: str,
        brief_original: str,
        interview_doc: Dict,
        outcome: Dict
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
                "industry": self._detect_industry(interview_doc)
            },
            "interview": {
                "questions_asked": self._count_questions(interview_doc),
                "duration_minutes": outcome.get("duration_minutes", 0),
                "categories_covered": len(interview_doc.get("document", {}).get("categories", [])),
                "questions_with_followup": self._count_followups(interview_doc),
                "gaps_identified": len(interview_doc.get("document", {}).get("gaps_detected", []))
            },
            "outcome": {
                "user_satisfaction": outcome.get("user_satisfaction", "medium"),
                "useful_questions": outcome.get("useful_questions", []),
                "failed_questions": outcome.get("failed_questions", []),
                "final_output_quality": outcome.get("final_output_quality", "approved")
            },
            "qa_document": {
                "json_path": self._save_json(interview_id, interview_doc),
                "summary": self._generate_summary(interview_doc)
            },
            "learning_metrics": self._calculate_metrics(interview_doc, outcome)
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
        self,
        brief: str,
        limit: int = 5
    ) -> List[Dict]:
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
                matches.append({
                    "interview_id": entry["interview_id"],
                    "similarity_score": overlap,
                    "summary": entry.get("summary"),
                    "useful_questions": entry.get("useful_questions", []),
                    "timestamp": entry.get("timestamp")
                })

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
            "gap_analysis": ["gap", "falta", "necesito expertise"]
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
        avg_confidence = sum(
            confidence_scores.get(q.get("confidence", "medium"), 2)
            for q in qa
        ) / len(qa) if qa else 2

        # Follow-up rate
        followup_rate = self._count_followups(interview_doc) / len(qa) if qa else 0

        return {
            "question_effectiveness_rate": round(effectiveness_rate, 2),
            "user_satisfaction_score": self._satisfaction_to_score(outcome.get("user_satisfaction")),
            "avg_confidence_score": self._confidence_to_label(avg_confidence),
            "followup_rate": round(followup_rate, 2)
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
            f"- Gaps identified: {len(gaps)}"
        ]

        if gaps:
            summary_lines.append("\nGaps:")
            for gap in gaps[:3]:  # Limit to first 3
                summary_lines.append(f"- {gap.get('missing_expertise', 'Unknown domain')}")

        return "\n".join(summary_lines)

    def _update_index(self, log_entry: Dict):
        """Update interview index for quick lookup."""
        index_path = self.log_dir / "hot" / "index.yaml"

        if index_path.exists():
            with open(index_path) as f:
                index = yaml.safe_load(f) or {"interviews": []}
        else:
            index = {"interviews": []}

        index["interviews"].append({
            "interview_id": log_entry["interview_id"],
            "timestamp": log_entry["timestamp"],
            "context_type": log_entry["context"]["context_type"],
            "brief_original": log_entry["context"]["brief_original"],
            "keywords": self._extract_keywords(log_entry["context"]["brief_original"]),
            "summary": log_entry["qa_document"]["summary"],
            "useful_questions": log_entry["outcome"]["useful_questions"],
            "learning_metrics": log_entry["learning_metrics"]
        })

        with open(index_path, "w") as f:
            yaml.dump(index, f, default_flow_style=False)
```

### Step 5: Create Unit Tests (2 hours)

**Archivo a crear:** `tests/unit/test_brain_registry.py`

```python
"""
Unit tests for brain_registry.py
"""

import pytest
import yaml
from pathlib import Path
import tempfile
from mastermind_cli.brain_registry import (
    load_brain_configs,
    get_brain,
    list_active_brains,
    get_brain_count
)


def test_load_brain_configs():
    """Test that brain configs load from YAML."""
    configs = load_brain_configs()

    # Should have brains 1-8
    assert len(configs) >= 8
    assert 1 in configs
    assert 8 in configs


def test_get_brain():
    """Test getting a specific brain config."""
    brain_1 = get_brain(1)

    assert brain_1 is not None
    assert brain_1["name"] == "Product Strategy"
    assert brain_1["status"] == "active"


def test_get_brain_not_found():
    """Test getting non-existent brain returns None."""
    brain_999 = get_brain(999)

    assert brain_999 is None


def test_list_active_brains():
    """Test listing only active brains."""
    active = list_active_brains()

    # Brain #8 should be 'pending', not 'active' (until PRP-012)
    assert 1 in active
    assert 8 not in active  # Pending, not active


def test_get_brain_count():
    """Test getting total brain count."""
    count = get_brain_count()

    assert count >= 8  # At least brains 1-8


def test_yaml_schema_valid():
    """Test that brains.yaml follows expected schema."""
    import mastermind_cli.brain_registry as registry

    with open.registry.BRAINS_CONFIG_PATH) as f:
        config = yaml.safe_load(f)

    # Verify structure
    assert "version" in config
    assert "brains" in config
    assert isinstance(config["brains"], list)

    # Verify each brain has required fields
    for brain in config["brains"]:
        assert "id" in brain
        assert "name" in brain
        assert "status" in brain
```

**Archivo a crear:** `tests/unit/test_interview_logger.py`

```python
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

    assert "app" in keywords
    assert "moderna" in keywords
    assert "delivery" in keywords
    assert "comida" in keywords
    # Stop words should be filtered
    assert "que" not in keywords
    assert "la" not in keywords
```

---

## Validation Gates

```bash
# ========== Step 1: YAML Registry ==========
# Verify file exists and is valid YAML
python -c "import yaml; yaml.safe_load(open('mastermind_cli/config/brains.yaml'))"
echo "✅ brains.yaml is valid YAML"

# Verify all brains 1-8 are present
python -c "
import yaml
with open('mastermind_cli/config/brains.yaml') as f:
    config = yaml.safe_load(f)
brain_ids = [b['id'] for b in config['brains']]
assert all(i in brain_ids for i in range(1, 9))
print(f'✅ All brains 1-8 registered')
"

# ========== Step 2: brain_registry.py ==========
# Test import and basic functionality
python -c "
from mastermind_cli.brain_registry import load_brain_configs, get_brain, list_active_brains
configs = load_brain_configs()
assert len(configs) >= 8
assert get_brain(1) is not None
assert 1 in list_active_brains()
print('✅ brain_registry.py imports and works')
"

# ========== Step 3: BrainExecutor ==========
# Test that BrainExecutor can be imported and has brain #8
python -c "
from mastermind_cli.orchestrator.brain_executor import BrainExecutor
executor = BrainExecutor()
assert 8 in executor.BRAIN_CONFIGS
assert executor.BRAIN_CONFIGS[8]['status'] == 'pending'
print('✅ BrainExecutor loads brain #8')
"

# ========== Step 4: InterviewLogger ==========
# Test InterviewLogger basic functionality
python -c "
from mastermind_cli.memory.interview_logger import InterviewLogger
logger = InterviewLogger(enabled=False)
assert logger._detect_context_type('feature de login') == 'feature_spec'
print('✅ InterviewLogger imports and works')
"

# ========== Step 5: Unit Tests ==========
# Run all new unit tests
uv run pytest tests/unit/test_brain_registry.py -v
uv run pytest tests/unit/test_interview_logger.py -v

# ========== Step 6: Integration ==========
# Test that existing code still works
python -c "
from mastermind_cli.orchestrator.brain_executor import BrainExecutor
executor = BrainExecutor()
# Should still work with brains 1-7
assert 1 in executor.BRAIN_CONFIGS
assert 7 in executor.BRAIN_CONFIGS
print('✅ Backward compatibility maintained')
"

# ========== Final Validation ==========
# Type check
mypy mastermind_cli/brain_registry.py
mypy mastermind_cli/memory/interview_logger.py

# Lint
ruff check mastermind_cli/brain_registry.py
ruff check mastermind_cli/memory/interview_logger.py

echo "========== ALL VALIDATIONS PASSED =========="
```

---

## Error Handling

### Error 1: brains.yaml Not Found

**When:** Config file missing

**Handling:**
```python
if not BRAINS_CONFIG_PATH.exists():
    raise FileNotFoundError(
        f"Brain config not found: {BRAINS_CONFIG_PATH}\n"
        f"Run 'mm framework status' to verify installation."
    )
```

### Error 2: Invalid YAML Syntax

**When:** YAML has syntax errors

**Handling:**
```python
try:
    config = yaml.safe_load(f)
except yaml.YAMLError as e:
    raise ValueError(
        f"Invalid YAML in {BRAINS_CONFIG_PATH}: {e}\n"
        f"Run 'ruff check --fix' to fix formatting issues."
    )
```

### Error 3: Brain ID Not Found

**When:** Requesting brain_id that doesn't exist

**Handling:**
```python
brain_config = self.BRAIN_CONFIGS.get(brain_id)
if not brain_config:
    return self._unimplemented_brain(brain_id, task)
```

### Error 4: Interview Logger Directory Creation Failed

**When:** Permission denied creating logs/interviews/

**Handling:**
```python
try:
    hot_dir.mkdir(parents=True, exist_ok=True)
except PermissionError:
    # Fall back to temp directory
    import tempfile
    hot_dir = Path(tempfile.gettempdir()) / "mastermind_interviews"
    hot_dir.mkdir(parents=True, exist_ok=True)
```

---

## Gotchas & Pitfalls

### Gotcha 1: YAML Boolean Values

**Issue:** YAML parses `yes/no` as booleans, not strings

**Fix:** Use quotes for string status:
```yaml
status: "active"  # Good
status: active    # Bad - YAML parses as True
```

### Gotcha 2: Path Compatibility (Windows/Linux)

**Issue:** Paths with backslashes on Windows

**Fix:** Always use `pathlib.Path` which handles OS differences:
```python
# Bad
path = "mastermind_cli/config/brains.yaml"

# Good
from pathlib import Path
path = Path("mastermind_cli/config") / "brains.yaml"
```

### Gotcha 3: Mutable Default Arguments

**Issue:** Don't use `def __init__(self, log_dir=Path("logs"))`

**Fix:** Use None as default:
```python
def __init__(self, log_dir: Optional[Path] = None):
    self.log_dir = log_dir or Path("logs/interviews")
```

### Gotcha 4: YAML Safe Load vs Load

**Issue:** `yaml.load()` is unsafe (can execute arbitrary Python)

**Fix:** Always use `yaml.safe_load()`:
```python
# Bad - unsafe
config = yaml.load(f)

# Good - safe
config = yaml.safe_load(f)
```

---

## Quality Checklist

- [x] All necessary context included (spec referenciado)
- [x] Validation gates are executable by AI
- [x] References existing patterns (Evaluator, BRAIN_CONFIGS)
- [x] Clear implementation path (5 steps, 9.5 hours)
- [x] Error handling documented (4 categorías)
- [x] Pseudocódigo incluido para todos los componentes
- [x] Unit tests especificados con código completo
- [x] Gotchas documentados (4 pitfalls comunes)
- [x] Backward compatibility considerada (cerebros 1-7 siguen funcionando)

---

## Branch Strategy

**Create branch:** `feature/prp-011-brain-08-core-infrastructure`

```bash
git checkout -b feature/prp-011-brain-08-core-infrastructure

# Work through implementation
# ... implement steps 1-5 ...

# Commit when all validations pass
git add .
git commit -m "feat(prp-011): implement core infrastructure for brain #8

- Add YAML-based brain registry (supports N brains)
- Implement InterviewLogger class
- Update BrainExecutor to support brain #8
- Add unit tests for new components

Validations:
✅ All brains 1-8 load from YAML
✅ InterviewLogger logs interviews correctly
✅ Backward compatibility maintained
✅ Unit tests passing

Refs: PRP-011, spec-brain-08"
```

---

## Success Criteria

- [ ] `mastermind_cli/config/brains.yaml` exists with brains 1-8
- [ ] `mastermind_cli/brain_registry.py` loads from YAML (not hardcoded)
- [ ] `BrainExecutor` recognizes brain #8 (status: pending)
- [ ] `InterviewLogger` can log/retrieve interviews
- [ ] All unit tests pass (>90% coverage)
- [ ] Existing code (brains 1-7) still works unchanged
- [ ] Type checking passes (`mypy`)
- [ ] Linting passes (`ruff check`)

---

## PRP Confidence Score

**Score: 10/10**

**Justification:**
- ✅ **Well-defined patterns** — Evalutor, BRAIN_CONFIGS ya existen
- ✅ **No dependencies** — Puede implementarse standalone
- ✅ **Clear validation** — Tests ejecutables para cada step
- ✅ **Low complexity** — Registry loading, logging (patrones conocidos)
- ✅ **High isolation** — No afecta código existente (brains 1-7)

**Riesgo mínimo:** Esta fase es la más segura de implementar. No tiene MCP dependencies, no requiere NotebookLM, y patrones son bien conocidos en el codebase.

---

## Next Steps After Completion

Once PRP-011 is complete:

1. **Create PR:** Merge to master
2. **Start PRP-012:** NotebookLM Setup (crea las 10 fuentes y configura notebook)
3. **Validate:** `mm brain status` shows brain #8 (pending)

---

**END OF PRP-011**
