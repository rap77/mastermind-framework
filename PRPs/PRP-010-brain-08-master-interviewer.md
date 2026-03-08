# PRP-010: Cerebro #8 - Master Interviewer / Discovery Brain

**Status:** Draft | Ready for Review
**Priority:** High (core scalability feature)
**Estimated Time:** 55-60 hours
**Dependencies:** PRP-009 (Memory System Phase 1)

---

## Executive Summary

Implementar el **Cerebro #8: Master Interviewer / Discovery Brain**, un cerebro especializado en extracción de información a través de entrevistas estructuradas. A diferencia de los cerebros #1-7 (expertos de dominio), el Cerebro #8 es un **facilitador** que sabe CÓMO entrevistar, estructurar información y orquestar otros cerebros para extraer requisitos completos.

**Características clave:**
- Entrevistas iterativas con follow-ups dinámicos de cerebros de dominio
- Detección de gaps de conocimiento y recomendación de nuevos cerebros
- Generación de documentos Q&A en JSON/YAML/Markdown
- Integración con PRP-009 para aprendizaje continuo
- Comando `/mm:discovery` para entrevistas guiadas

---

## Context from Clarification Session

### Decisiones Críticas (del spec)

1. **Arquitectura:** Cerebro #8 es un facilitador (no meta-orquestador)
   - **NO contiene knowledge de dominio** — eso es #1-7
   - **SÍ contiene metodología de entrevista** — The Mom Test, Socratic questioning
   - Orquestador (código Python) decide routing, Cerebro #8 solo entrevista

2. **Flujo Iterativo:** No batch — preguntas con follow-ups dinámicos
   ```
   Cerebro #8 pregunta → Usuario responde → Brain #2 profundiza → Usuario responde → [Loop]
   ```

3. **Multi-formato Output:** JSON + YAML + Markdown
   - JSON: Comunicación API (escalable)
   - YAML: Logging PRP-009 (consistente)
   - Markdown: Human-readable

4. **Escalabilidad:** Registry extensible (no hardcoded a 7 cerebros)
   - Load from YAML: `mastermind_cli/config/brains.yaml`
   - Soporta N cerebros futuros (#9, #10, etc.)

5. **Gap Detection:** Cerebro #8 recomienda crear nuevos cerebros
   - Detecta cuando falta expertise (ej: SEO, Marketing)
   - Genera recomendación con expertos sugeridos

### Expertos del Cerebro #8 (10 Fuentes)

| ID | Título | Autor | Tipo | Prioridad |
|----|--------|-------|------|-----------|
| FUENTE-801 | The Mom Test | Rob Fitzpatrick | Book | 🔴 Alta |
| FUENTE-802 | Never Split the Difference | Chris Voss | Book | 🔴 Alta |
| FUENTE-803 | The Coaching Habit | Michael Bungay Stanier | Book | 🟡 Media |
| FUENTE-804 | Continuous Discovery Habits | Teresa Torres | Book | 🔴 Alta |
| FUENTE-805 | User Interviews | Erika Hall | Book | 🟡 Media |
| FUENTE-806 | Thinking, Fast and Slow | Daniel Kahneman | Book | 🟡 Media |
| FUENTE-807 | Crucial Conversations | Patterson et al. | Book | 🟢 Baja |
| FUENTE-808 | Improve Your Retrospectives | Judith Andres | Book | 🟢 Baja |
| FUENTE-809 | Ask Method | Ryan Levesque | Book | 🟢 Baja |
| FUENTE-810 | Socratic Questioning | Various | Compilation | 🟢 Baja |

---

## External Resources

### NotebookLM Documentation
- **Upload Sources:** https://notebooklm.google.com/ — Arrastrar archivos a notebook
- **Query via MCP:** Usar `mcp__notebooklm-mcp__notebook_query`
- **Notebook ID Format:** UUID en URL (ej: `f276ccb3-0bce-4069-8b55-eae8693dbe75`)

### Interview Methodology References
- **The Mom Test:** https://momtestbook.com/ — Descubrir necesidades reales
- **Teresa Torres - Continuous Discovery:** https://www.techatlas.com/continuous-discovery-habits/
- **Socratic Questioning:** https://en.wikipedia.org/wiki/Socratic_method — Técnica de preguntas

### Python YAML Handling
- **PyYAML Documentation:** https://pyyaml.org/wiki/PyYAMLDocumentation
- **YAML Schema Validation:** https://pyyaml.org/wiki/PyYAMLDocumentation#schema-validation

### Click CLI (para /mm:discovery)
- **Click Arguments:** https://click.palletsprojects.com/en/8.1.x/arguments/
- **Rich Console:** https://rich.readthedocs.io/en/stable/console.html

---

## Codebase Patterns to Follow

### 1. Brain Registry Pattern (Current - Hardcoded)

**Archivo:** `mastermind_cli/orchestrator/brain_executor.py:23-67`

```python
BRAIN_CONFIGS = {
    1: {
        'id': 'product-strategy',
        'name': 'Product Strategy',
        'notebook_id': 'f276ccb3-0bce-4069-8b55-eae8693dbe75',
        'status': 'active'
    },
    # ... cerebros 2-7
}
```

**⚠️ PATRÓN A MEJORAR:** Este PRP extiende esto a YAML-based registry.

### 2. Brain Executor Query Pattern

**Archivo:** `mastermind_cli/orchestrator/brain_executor.py:173-190`

```python
if use_mcp and self.mcp_client and self.mcp_client.is_available():
    try:
        response = self.mcp_client.query_notebook(
            brain_id=1,
            query=query
        )
        if response.get('status') == 'success':
            return self._format_brain_response(1, response.get('content', ''), brief)
    except Exception as e:
        return self._mock_brain_1_response(brief, query, error=str(e))
```

**✅ PATRÓN A SEGUIR:** Mismo pattern para Brain #8.

### 3. Coordinator Flow Pattern

**Archivo:** `mastermind_cli/orchestrator/coordinator.py:45-100`

```python
def orchestrate(self, brief: str, flow: Optional[str] = None, ...):
    # Step 1: Detect or validate flow
    if not flow:
        flow = self.flow_detector.detect(brief)

    # Step 2: Generate execution plan
    self.current_plan = self.plan_generator.generate(brief, flow)

    # Step 3: If dry_run, print plan and exit
    if dry_run:
        return {'status': 'dry_run_complete', 'plan': self.current_plan}

    # Step 4: Execute with iteration loop
    execution_report = self._execute_with_iterations(max_iterations)

    # Step 5: Format and deliver final result
    final_output = self.formatter.format_final_deliverable(execution_report)
```

**✅ PATRÓN A EXTENDER:** Agregar `FLOW_DISCOVERY` y `_execute_discovery_flow()`.

### 4. Memory Logger Pattern (PRP-009)

**Archivo:** `mastermind_cli/memory/storage.py` (referencia)

```python
def save_evaluation(self, evaluation: EvaluationEntry) -> str:
    """Save evaluation to YAML log."""
    hot_dir = self.log_dir / "hot" / datetime.now().strftime("%Y-%m")
    hot_dir.mkdir(parents=True, exist_ok=True)

    log_path = hot_dir / f"{evaluation.id}.yaml"
    with open(log_path, "w") as f:
        yaml.dump(evaluation.model_dump(), f, default_flow_style=False)

    return str(log_path)
```

**✅ PATRÓN A REPLICAR:** InterviewLogger con misma estructura.

### 5. Slash Command Pattern

**Archivo:** `.claude/commands/mm/ask-product.md`

```markdown
---
name: ask-product
description: Consult Product Strategy brain
usage: /mm:ask-product "<question>"
---

# Ask Product Strategy

## Usage
Run this command to get product insights from Brain #1.

...
```

**✅ PATRÓN A SEGUIR:** Crear `.claude/commands/mm/discovery.md` con mismo formato.

---

## Implementation Blueprint

### Phase 0: Pre-Implementation (1 hour)

#### Task 0.1: Review PRP-009
- Leer `mastermind_cli/memory/` para entender EvaluationLogger
- Localizar: `mastermind_cli/memory/models.py`, `storage.py`, `logger.py`
- Entender cómo se loguean evaluaciones del Brain #7

#### Task 0.2: NotebookLM Setup
- Crear cuenta en https://notebooklm.google.com
- Crear notebook: "Brain 08 - Master Interviewer"
- **NO** agregar fuentes todavía (Phase 2)

#### Task 0.3: Create GitHub Issue
- Título: "PRP-010: Implement Brain #8 - Master Interviewer"
- Body: Link a este spec + checklist de tareas
- Labels: `enhancement`, `brain-8`, `interview-system`

---

### Phase 1: Core Infrastructure (8.5 hours)

#### Task 1.1: Create YAML Brain Registry (30 min)

**Crear archivo:** `mastermind_cli/config/brains.yaml`

```yaml
version: "1.0"
brains:
  - id: 1
    name: Product Strategy
    notebook_id: f276ccb3-0bce-4069-8b55-eae8693dbe75
    system_prompt: agents/brains/product-strategy.md
    status: active

  - id: 2
    name: UX Research
    notebook_id: ea006ece-00a9-4d5c-91f5-012b8b712936
    status: active

  # ... brains 3-7 ...

  - id: 8
    name: Master Interviewer / Discovery
    notebook_id: PENDING  # Updated in Phase 2
    system_prompt: agents/brains/master-interviewer.md
    expertise:
      - Interview methodology
      - Information extraction
      - Question structuring
      - Gap detection
      - Facilitation techniques
    status: active
```

#### Task 1.2: Update brain_registry.py (1 hour)

**Editar:** `mastermind_cli/brain_registry.py`

```python
import yaml
from pathlib import Path

def load_brain_configs() -> dict:
    """Load brain configurations from YAML file."""
    config_path = Path(__file__).parent / "config" / "brains.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    brains = {}
    for brain in config["brains"]:
        brains[brain["id"]] = brain

    return brains

# Replace hardcoded BRAIN_CONFIGS
BRAIN_CONFIGS = load_brain_configs()
```

#### Task 1.3: Add Brain #8 Entry (30 min)

**Ya incluido en Task 1.1** — solo update notebook_id en Phase 2.

#### Task 1.4: Update BrainExecutor (1 hour)

**Editar:** `mastermind_cli/orchestrator/brain_executor.py`

```python
# Add to BRAIN_CONFIGS (after loading from YAML):
8: {
    'id': 'master-interviewer',
    'name': 'Master Interviewer / Discovery',
    'notebook_id': 'PENDING',  # Updated in Phase 2
    'status': 'active'
}

# Add to execute() method:
elif brain_id == 8:
    return self._execute_brain_8(task, use_mcp=use_mcp)

# Add new method:
def _execute_brain_8(self, task: Dict, use_mcp: bool = True) -> Dict:
    """Execute Master Interviewer brain."""
    context = task.get('context', {})
    query = f"""As a Master Interviewer, {context.get('instruction', 'design an interview strategy')}

Context: {context.get('brief', '')}

Provide interview strategy in JSON format with categories, questions, and target brains.
"""

    if use_mcp and self.mcp_client and self.mcp_client.is_available():
        try:
            response = self.mcp_client.query_notebook(brain_id=8, query=query)
            if response.get('status') == 'success':
                return self._format_brain_response(8, response.get('content', ''), context.get('brief', ''))
        except Exception as e:
            return self._mock_brain_8_response(context.get('brief', ''), query, error=str(e))

    return self._mock_brain_8_response(context.get('brief', ''), query)

def _mock_brain_8_response(self, brief: str, query: str, error: str = None) -> Dict:
    """Mock response for Brain #8 (testing)."""
    return {
        'brain_id': 8,
        'brain_name': 'Master Interviewer',
        'status': 'mock',
        'output': {'note': 'Brain #8 mock response', 'brief': brief, 'mcp_error': error},
        'message': 'Brain #8 mock response (MCP not available)'
    }
```

#### Task 1.5: Create InterviewLogger Class (3 hours)

**Crear archivo:** `mastermind_cli/memory/interview_logger.py`

```python
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import yaml
import json

class InterviewLogger:
    """Log interviews for learning and improvement."""

    def __init__(self, enabled: bool = True, log_dir: Optional[Path] = None):
        self.enabled = enabled
        self.log_dir = log_dir or Path("logs/interviews")

    def log_interview(
        self,
        session_id: str,
        brief_original: str,
        interview_doc: Dict,
        outcome: Dict
    ) -> Optional[str]:
        """Log an interview session."""
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
                "questions_asked": len(interview_doc["document"]["qa"]),
                "duration_minutes": outcome.get("duration_minutes", 0),
                "categories_covered": len(interview_doc["document"]["categories"]),
                "questions_with_followup": self._count_followups(interview_doc),
                "gaps_identified": len(interview_doc["document"].get("gaps_detected", []))
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

    def find_similar_interviews(self, brief: str, limit: int = 5) -> List[Dict]:
        """Find similar past interviews for learning."""
        index_path = self.log_dir / "hot" / "index.yaml"
        if not index_path.exists():
            return []

        with open(index_path) as f:
            index = yaml.safe_load(f)

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
                    "useful_questions": entry.get("useful_questions", [])
                })

        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:limit]

    # Helper methods...
    def _detect_context_type(self, brief: str) -> str:
        keywords = {
            "feature_spec": ["feature", "funcionalidad", "característica"],
            "technical_design": ["architecture", "arquitectura", "api"],
            "client_onboarding": ["client", "cliente", "onboarding"]
        }
        brief_lower = brief.lower()
        for context_type, kw_list in keywords.items():
            if any(kw in brief_lower for kw in kw_list):
                return context_type
        return "general"

    def _count_followups(self, interview_doc: Dict) -> int:
        return sum(1 for q in interview_doc["document"]["qa"] if q.get("follow_up_questions"))

    def _extract_keywords(self, brief: str) -> List[str]:
        stop_words = {"el", "la", "de", "que", "y", "a", "en"}
        words = brief.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 3]

    def _calculate_metrics(self, interview_doc: Dict, outcome: Dict) -> Dict:
        qa = interview_doc["document"]["qa"]
        useful_questions = set(outcome.get("useful_questions", []))
        effectiveness_rate = len(useful_questions) / len(qa) if qa else 0

        confidence_scores = {"high": 3, "medium": 2, "low": 1}
        avg_confidence = sum(
            confidence_scores.get(q.get("confidence", "medium"), 2)
            for q in qa
        ) / len(qa) if qa else 2

        return {
            "question_effectiveness_rate": round(effectiveness_rate, 2),
            "user_satisfaction_score": self._satisfaction_to_score(outcome.get("user_satisfaction")),
            "avg_confidence_score": self._confidence_to_label(avg_confidence)
        }

    def _satisfaction_to_score(self, satisfaction: str) -> int:
        mapping = {"low": 1, "medium": 3, "high": 5}
        return mapping.get(satisfaction, 3)

    def _confidence_to_label(self, score: float) -> str:
        if score >= 2.5: return "high"
        elif score >= 1.5: return "medium"
        return "low"

    def _next_sequence(self) -> int:
        return 1  # Simplified

    def _save_json(self, interview_id: str, doc: Dict) -> str:
        json_dir = self.log_dir / "json" / datetime.now().strftime("%Y-%m")
        json_dir.mkdir(parents=True, exist_ok=True)
        json_path = json_dir / f"{interview_id}.json"
        with open(json_path, "w") as f:
            json.dump(doc, f, indent=2)
        return str(json_path)

    def _generate_summary(self, interview_doc: Dict) -> str:
        qa = interview_doc["document"]["qa"]
        gaps = interview_doc["document"].get("gaps_detected", [])
        return f"Interview for {interview_doc['metadata']['context_type']} - {len(qa)} Qs, {len(gaps)} gaps"

    def _detect_industry(self, interview_doc: Dict) -> str:
        return interview_doc["metadata"].get("industry", "general")

    def _update_index(self, log_entry: Dict):
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
            "useful_questions": log_entry["outcome"]["useful_questions"]
        })

        with open(index_path, "w") as f:
            yaml.dump(index, f, default_flow_style=False)
```

#### Task 1.6: Write Unit Tests (2 hours)

**Crear archivo:** `tests/unit/test_interview_logger.py`

```python
import pytest
from mastermind_cli.memory.interview_logger import InterviewLogger
from pathlib import Path
import tempfile
import yaml

def test_log_interview_creates_file():
    """Test that logging creates YAML file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = InterviewLogger(enabled=True, log_dir=Path(tmpdir))

        log_path = logger.log_interview(
            session_id="test-001",
            brief_original="test brief",
            interview_doc={
                "document": {
                    "qa": [{"question": "Q1", "answer": "A1", "confidence": "high"}],
                    "categories": [{"id": "ux"}],
                    "gaps_detected": []
                },
                "metadata": {"context_type": "feature_spec"}
            },
            outcome={"user_satisfaction": "high"}
        )

        assert Path(log_path).exists()
        assert log_path.endswith(".yaml")

        # Verify content
        with open(log_path) as f:
            content = yaml.safe_load(f)

        assert content["session_id"] == "test-001"
        assert content["brain"] == "brain-08"

def test_find_similar_interviews():
    """Test interview similarity matching."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = InterviewLogger(enabled=True, log_dir=Path(tmpdir))

        # Log a reference interview
        logger.log_interview(
            session_id="ref-001",
            brief_original="app moderna delivery",
            interview_doc={...},
            outcome={...}
        )

        # Find similar
        matches = logger.find_similar_interviews("app delivery moderna")

        assert len(matches) > 0
        assert matches[0]["similarity_score"] > 0
```

---

### Phase 2: NotebookLM Setup (5 hours)

#### Tasks 2.1-2.10: Create Expert Sources

**Crear directorio:** `docs/software-development/08-master-interviewer-brain/sources/`

**Usar plantilla:** `docs/software-development/01-product-strategy-brain/sources/FUENTE-001-inspired-cagan.md`

**Template para cada fuente:**

```yaml
---
source_id: "FUENTE-80X"
brain: "brain-software-08-master-interviewer"
niche: "software-development"
title: "Book Title"
author: "Author Name"
expert_id: "EXP-80X"
type: "book"
year: YYYY
isbn: "978-XXXXXXXX"
publisher: "Publisher"
pages: XXX
skills_covered: ["interview", "discovery", "facilitation"]
distillation_date: "2026-03-07"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
changelog:
  - version: "1.0.0"
    date: "2026-03-07"
    changes:
      - "Destilación inicial para Brain #8"
status: "active"

---

# FUENTE-80X: Book Title

## Datos de la Fuente

| Campo | Valor |
|-------|-------|
| **Autor** | Author Name |
| **Tipo** | Libro |
| **Título** | Book Title |
| **Año** | YYYY |
| **ISBN** | 978-XXXXXXXX |

## Contenido Destilado

### 1. Principios Fundamentales

[Extraer principios clave del libro]

### 2. Frameworks y Metodologías

[Extraer frameworks aplicables a entrevistas]

### 3. Modelos Mentales

[Extraer modelos mentales para el cerebro]

### 4. Criterios de Decisión

[Extraer criterios para decidir cómo/de qué preguntar]

### 5. Anti-patrones

[Extraer qué NO hacer al entrevistar]
```

**Fuentes a crear (10):**

| FUENTE | Título | Autor | ISBN |
|--------|--------|-------|------|
| 801 | The Mom Test | Rob Fitzpatrick | 978-0993181515 |
| 802 | Never Split the Difference | Chris Voss | 978-0062407803 |
| 803 | The Coaching Habit | Michael Bungay Stanier | 978-0978440749 |
| 804 | Continuous Discovery Habits | Teresa Torres | 978-1734313504 |
| 805 | User Interviews | Erika Hall | - |
| 806 | Thinking, Fast and Slow | Daniel Kahneman | 978-0374533557 |
| 807 | Crucial Conversations | Patterson et al. | 978-1469266824 |
| 808 | Improve Your Retrospectives | Judith Andres | - |
| 809 | Ask Method | Ryan Levesque | - |
| 810 | Socratic Questioning | Various | - |

#### Task 2.11: Create Notebook in NotebookLM

1. Ir a https://notebooklm.google.com/
2. Click "New notebook"
3. Name: `Brain 08 - Master Interviewer`
4. Copy notebook ID from URL (ej: `d8de74d6-7028-44ed-b4d4-784d6a9256e6`)

#### Task 2.12-2.13: Upload Sources to NotebookLM

1. Click "Add sources" → "Google Drive"
2. Upload all 10 FUENTE-XXX.md files
3. Wait for processing (check `loaded_in_notebook: true`)

#### Task 2.14: Update brain_registry with Notebook ID

**Editar:** `mastermind_cli/config/brains.yaml`

```yaml
  - id: 8
    name: Master Interviewer / Discovery
    notebook_id: "d8de74d6-7028-44ed-b4d4-784d6a9256e6"  # Replace with actual ID
    system_prompt: agents/brains/master-interviewer.md
    expertise: [...]
    status: active
```

#### Task 2.15: Test MCP Connection

```bash
mm brain status

# Expected output:
# Brain #8: Master Interviewer
#   Status: Active
#   Notebook: [ID]
#   Sources: 10
```

---

### Phase 3: Orchestrator Integration (23 hours)

#### Task 3.1: Add FLOW_DISCOVERY Constant (2 hours)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
class Coordinator:
    FLOW_DISCOVERY = "discovery"  # Add this
    MAX_ITERATIONS = 3
```

#### Task 3.2: Implement _detect_flow() (1 hour)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _detect_flow(self, brief: str) -> str:
    """Detect if brief needs discovery interview."""
    # Check if brief is too vague
    if len(brief.split()) < 15:  # Less than 15 words
        return self.FLOW_DISCOVERY

    # Check for ambiguity markers
    ambiguity_markers = ["moderno", "nuevo", "bueno", "mejor", "app"]
    if any(marker in brief.lower() for marker in ambiguity_markers):
        return self.FLOW_DISCOVERY

    # Default: existing flows
    return self.flow_detector.detect(brief)
```

#### Task 3.3-3.8: Implement Discovery Flow (16 hours)

**Agregar métodos a Coordinator** — **Ver spec completo para pseudocódigo detallado**

```python
def _execute_discovery_flow(self, brief: str) -> Dict:
    """Execute discovery interview with Brain #8."""
    # Step 1: Generate interview plan via Brain #8
    interview_plan = self._generate_interview_plan(brief)

    # Step 2: Execute iterative interview
    interview_doc = self._conduct_interview(interview_plan)

    # Step 3: Distribute to relevant brains
    recommendations = self._distribute_interview(interview_doc)

    # Step 4: Synthesize final output
    return self._synthesize_recommendations(recommendations)

def _generate_interview_plan(self, brief: str) -> Dict:
    """Ask Brain #8 to design interview strategy."""
    query = f"""
    Design an interview strategy for the following brief:

    Brief: {brief}

    Provide:
    1. Categories to cover (e.g., users, platforms, architecture)
    2. Target brain for each category (1-7)
    3. Initial questions for each category
    4. Order of categories

    Format as JSON.
    """

    response = self.mcp_client.query_notebook(brain_id=8, query=query)
    return parse_json(response)

def _conduct_interview(self, plan: Dict) -> Dict:
    """Conduct iterative interview with user."""
    interview_state = {
        "current_category": 0,
        "qa": [],
        "gaps": []
    }

    for category in plan["categories"]:
        questions = category["questions"]

        for question in questions:
            # Display question via AskUserQuestion
            user_answer = self._ask_question(
                question=question,
                category=category,
                options=question.get("options")
            )

            # Route to target brain for potential follow-up
            target_brain = category["target_brain"]
            follow_up = self._request_followup(
                brain_id=target_brain,
                question=question,
                answer=user_answer
            )

            # Record Q&A
            interview_state["qa"].append({
                "question": question,
                "answer": user_answer,
                "category": category["id"],
                "target_brain": target_brain,
                "follow_up": follow_up
            })

            # If brain signals "enough", move to next category
            if follow_up.get("complete", False):
                break

    # Generate final document via Brain #8
    return self._finalize_interview(interview_state)
```

#### Task 3.9: Add Error Handling (2 hours)

**Ver spec sección "Error Handling"** para implementar:

```python
try:
    interview_plan = self._generate_interview_plan(brief)
except NotebookLMTimeoutError:
    return self._handle_timeout(brief)
except NotebookLMUnavailableError:
    return self._handle_mcp_unavailable(brief)
except BrainNotFoundError as e:
    return self._handle_invalid_brain(e, brief)
```

#### Task 3.10: Write Integration Tests (3 hours)

**Crear:** `tests/integration/test_discovery_flow.py`

```python
def test_full_discovery_flow():
    """Test end-to-end discovery flow."""
    coordinator = Coordinator(use_mcp=False)  # Mock mode
    result = coordinator.orchestrate(
        brief="quiero una app de delivery",
        flow="discovery"
    )

    assert result["status"] == "completed"
    assert "qa_document" in result
    assert len(result["qa_document"]["document"]["qa"]) > 0

def test_gap_detection():
    """Test that knowledge gaps are detected."""
    brief = "Necesito una app con SEO y content marketing"

    result = coordinator.orchestrate(brief=brief, flow="discovery")

    gaps = result["qa_document"]["document"].get("gaps_detected", [])
    assert len(gaps) > 0
    assert any("marketing" in gap["missing_expertise"].lower() for gap in gaps)
```

---

### Phase 4: Slash Command (4 hours)

#### Task 4.1: Create /mm:discovery Command (2 hours)

**Crear archivo:** `.claude/commands/mm/discovery.md`

```yaml
---
name: discovery
description: Conduct structured discovery interview using Brain #8
usage: /mm:discovery "<problem or requirement>"
examples:
  - /mm:discovery "Quiero crear una app de delivery"
  - /mm:discovery "Necesito un sistema de login"
  - /mm:discovery "Onboarding de cliente de marketing"
---

# MasterMind Discovery Interviewer

## Usage

Run this command when you need to:
- Extract requirements from vague user input
- Conduct onboarding interviews for clients
- Clarify technical specifications
- Discover user needs before designing features

## What It Does

1. **Analyzes your input** to understand context
2. **Consults Brain #8** (Master Interviewer) for interview strategy
3. **Conducts iterative interview** with guided questions
4. **Routes questions** to domain brains (#1-7) for follow-ups
5. **Generates structured Q&A document** in JSON/YAML/Markdown
6. **Detects knowledge gaps** and recommends new brains

## Examples

### Client Onboarding

Input: `Cliente de agencia de marketing necesita app`

**Result:** Structured brief with user personas, platforms, key features

### Feature Clarification

Input: `Quiero una app moderna`

**Result:** Clarified requirements (what "modern" means, target users, problems solved)

### Technical Specification

Input: `Necesitamos integrar OAuth con Google y Microsoft`

**Result:** Technical spec with security requirements, token handling, error cases
```

#### Tasks 4.2-4.3: Test & Document (2 hours)

- Manual testing con 3 inputs diferentes
- Update `docs/CLI-REFERENCE.md`

---

### Phase 5: Learning System Integration (9 hours)

#### Tasks 5.1-5.4: Add Learning Features to InterviewLogger

**Ver spec sección "Integration Points"** para implementar:

- `find_similar_interviews()` — retrieval de entrevistas similares
- `_calculate_metrics()` — métricas de aprendizaje
- Integration en `_conduct_interview()` — usar historial para mejorar
- Retention policy — hot/warm/cold storage

#### Task 5.5: Write Tests (2 hours)

**Crear:** `tests/unit/test_interview_learning.py`

---

### Phase 6: Testing & Polish (5 hours)

#### Tasks 6.1-6.3: E2E Tests (Manual)

1. **Test:** "quiero una app moderna" → Clarified brief
2. **Test:** Client onboarding → Technical spec
3. **Test:** "Necesito SEO" → Gap detection → Brain recommendation

#### Task 6.4: Performance Test

- Test con 10+ questions
- Verify < 5 minutos

#### Tasks 6.5-6.6: Documentation & Bug Fixes

---

### Phase 7: Release (2 hours)

#### Task 7.1: Update README.md

```markdown
## Brain #8: Master Interviewer / Discovery

Expert in information extraction through structured interviews. Use `/mm:discovery` to conduct guided interviews and extract requirements from vague inputs.

**Key Features:**
- Iterative interviews with domain brain follow-ups
- Gap detection and new brain recommendations
- Multi-format output (JSON/YAML/Markdown)
- Learning system integration

**Usage:**
```bash
/mm:discovery "Quiero crear una app de delivery"
```
```

#### Task 7.2: Update MEMORY.md

```markdown
## Brain Status

| # | Brain | Expertos | NotebookLM | Estado |
|---|-------|----------|------------|--------|
| 1 | Product Strategy | Cagan, Torres, Perri | f276ccb3... | **Activo** |
| ... | ... | ... | ... | ... |
| 8 | Master Interviewer | Fitzpatrick, Voss, Torres | [ID] | **Activo** ✨ |
```

#### Tasks 7.3-7.4: Tag & Release Notes

```bash
git tag v1.1.0 -m "Release Brain #8: Master Interviewer"
git push origin v1.1.0
```

---

## Validation Gates

### Phase 1: Core Infrastructure

```bash
# Syntax & Style
cd mastermind_cli
ruff check config/ orchestrator/
ruff format --check config/ orchestrator/

# Type check
mypy mastermind_cli/config/
mypy mastermind_cli/orchestrator/

# Unit tests
uv run pytest tests/unit/test_brain_registry.py -v
uv run pytest tests/unit/test_interview_logger.py -v

# Integration
uv run pytest tests/integration/test_brain_executor.py -v
```

### Phase 2: NotebookLM Setup

```bash
# Verify Brain #8 accessibility
mm brain status

# Expected output includes Brain #8 with 10 sources
```

### Phase 3: Orchestrator Integration

```bash
# Integration tests
uv run pytest tests/integration/test_discovery_flow.py -v

# Test with mock (no MCP)
mm orchestrate run --flow discovery --brief "test brief" --dry-run

# Expected: Generates interview plan
```

### Phase 4: Slash Command

```bash
# Test command manually
/mm:discovery "quiero una app de delivery"

# Expected: Launches interactive interview
```

### Phase 5: Learning System

```bash
# Unit tests
uv run pytest tests/unit/test_interview_learning.py -v

# Test similarity search
uv run python -c "
from mastermind_cli.memory.interview_logger import InterviewLogger
logger = InterviewLogger()
matches = logger.find_similar_interviews('app delivery')
print(f'Found {len(matches)} similar interviews')
"
```

### Phase 6: Full E2E

```bash
# Complete workflow test
/mm:discovery "quiero una app moderna"

# Expected:
# 1. Interview conducted
# 2. Q&A document generated
# 3. Saved to logs/interviews/
# 4. Gaps detected (if any)
```

### Final Validation

```bash
# All tests
uv run pytest tests/ -v --cov=mastermind_cli

# Coverage check
coverage report | grep "TOTAL"
# Expected: > 80%

# Type check
mypy mastermind_cli/

# Lint
ruff check mastermind_cli/
```

---

## Quality Checklist

- [x] All necessary context included (spec completo referenciado)
- [x] Validation gates are executable by AI
- [x] References existing patterns (brain_executor.py, coordinator.py, PRP-009)
- [x] Clear implementation path (7 fases, 53 tareas)
- [x] Error handling documented (6 categorías de errores)
- [x] External resources provided (NotebookLM, Click, Rich, PyYAML)
- [x] Code examples included (pseudocódigo para todas las fases)
- [x] Integration with PRP-009 explained

---

## PRP Confidence Score

**Score: 9/10**

**Justification:**
- ✅ **Spec completo** con 17 secciones, ~1,500 líneas
- ✅ **Patrones del codebase referenciados** (brain_executor, coordinator, memory)
- ✅ **Validación clara** con comandos ejecutables
- ✅ **7 fases interconectadas** con dependencias explícitas
- ✅ **53 tareas específicas** con estimaciones de tiempo
- ⚠️ **-1 punto**: Complejidad de la implementación (iterative interview flow es NOVEDOSO en el codebase)

**Riesgo identificado:** El flujo de entrevista iterativa con AskUserQuestion es un patrón nuevo que no existe actualmente en el código. La primera implementación podría requerir iteraciones para pulir la experiencia de usuario.

---

## Appendix: Quick Reference

### Archivos Clave a Crear/Modificar

```
mastermind_cli/
├── config/
│   └── brains.yaml                    # NEW - YAML registry
├── orchestrator/
│   ├── coordinator.py                 # MOD - Add discovery flow
│   └── brain_executor.py              # MOD - Add brain #8
├── memory/
│   └── interview_logger.py            # NEW - Interview logging
.claude/commands/mm/
└── discovery.md                       # NEW - /mm:discovery command
docs/software-development/
└── 08-master-interviewer-brain/
    ├── spec-brain-08-master-interviewer.md  # DONE
    └── sources/
        ├── FUENTE-801_*.md            # NEW x10
        └── ...
tests/
├── unit/
│   ├── test_brain_registry.py         # NEW
│   ├── test_interview_logger.py       # NEW
│   └── test_interview_learning.py     # NEW
└── integration/
    └── test_discovery_flow.py         # NEW
```

### Comandos Clave

```bash
# Desarrollo
mm brain status              # Verify Brain #8
mm orchestrate run --flow discovery --brief "test"  # Test flow

# Testing
uv run pytest tests/unit/test_interview_logger.py -v
uv run pytest tests/integration/test_discovery_flow.py -v

# Usage
/mm:discovery "quiero una app de delivery"
```

---

**END OF PRP-010**
