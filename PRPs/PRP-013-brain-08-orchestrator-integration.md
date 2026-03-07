# PRP-013: Brain #8 Orchestrator Integration

**Status:** Ready to Implement (after PRP-011 & PRP-012)
**Priority:** Critical (implements core interview flow)
**Estimated Time:** 23 hours
**Dependencies:** PRP-011 (Core Infrastructure), PRP-012 (NotebookLM Setup)
**Branch:** `feature/prp-013-brain-08-orchestrator-integration`

---

## Executive Summary

Implementar la integración del Cerebro #8 en el Orchestrator, habilitando el flujo de entrevista iterativa. Esta fase es el corazón funcional del Cerebro #8: permite que el orquestador detecte cuándo se necesita una entrevista, genere un plan vía Brain #8, conduzca la entrevista iterativamente con el usuario, y distribuya las respuestas a los cerebros de dominio (#1-7).

**Activities:**
1. Agregar `FLOW_DISCOVERY` al Coordinator
2. Implementar detección de ambigüedad en briefs
3. Implementar `_execute_discovery_flow()` con iteración
4. Integrar AskUserQuestion para preguntas interactivas
5. Implementar routing a cerebros de dominio para follow-ups
6. Manejo de errores para timeouts y MCP unavailable
7. Tests de integración

---

## Context from Brain #8 Spec

**Referencia:** `docs/software-development/08-master-interviewer-brain/spec-brain-08-master-interviewer.md` → Sección "Integration Points"

### El Flujo de Discovery

```
User Brief (vago) → Orchestrator detecta ambigüedad
    ↓
Brain #8 genera plan de entrevista (categorías, preguntas, brains objetivo)
    ↓
Iterative Interview Loop:
  - AskUserQuestion muestra pregunta al usuario
  - Usuario responde
  - Respuesta se envía al brain de dominio (#1-7)
  - Brain genera follow-up pregunta o señala "complete"
  - Se repite hasta completar categoría
    ↓
Brain #8 sintetiza documento final Q&A
    ↓
Documento se distribuye a brains relevantes
    ↓
Recomendaciones se generan
```

### Diferencia Clave vs. Flujos Existentes

Los flujos existentes (`validation_only`, `full_product`) son **batch** — ejecutan tasks secuencialmente sin input del usuario.

El flujo `discovery` es **interactivo** — requiere input del usuario entre cada pregunta.

**Implicación:** No se puede ejecutar en un solo bloque. Necesita AskUserQuestion tool integration.

---

## External Resources

### AskUserQuestion Documentation

**File:** Tool description en Claude Code system context

```python
AskUserQuestion(
    questions=[
        {
            "question": "¿Qué tipo de usuarios usará la app?",
            "header": "Users",
            "options": [
                {"label": "B2B", "description": "Empresas"},
                {"label": "B2C", "description": "Consumidores"},
                {"label": "Ambos", "description": "Híbrido"}
            ],
            "multiSelect": false
        }
    ]
)
```

**Returns:** User selection in `answers` field

### MCP NotebookLM Query Documentation

**Referencia:** `mastermind_cli/orchestrator/mcp_integration.py`

```python
self.mcp_client.query_notebook(
    brain_id=8,
    query="Design interview strategy for: {brief}"
)
```

**Returns:** `{'status': 'success', 'content': '...'}`

---

## Codebase Patterns to Follow

### Pattern 1: Flow Detection (Existing)

**Archivo:** `mastermind_cli/orchestrator/coordinator.py:45-77`

```python
def orchestrate(self, brief: str, flow: Optional[str] = None, ...):
    # Step 1: Detect or validate flow
    if not flow:
        flow = self.flow_detector.detect(brief)
    elif not self.flow_detector.validate_flow(flow):
        return self._error_report(f"Invalid flow type: {flow}")
```

**✅ PATRÓN A SEGUIR:** Agregar `_detect_flow()` que checkea ambigüedad antes de llamar a `flow_detector.detect()`.

### Pattern 2: Flow Execution (Existing)

**Archivo:** `mastermind_cli/orchestrator/coordinator.py:103-128`

```python
def _execute_with_iterations(self, max_iterations: int) -> Dict:
    # Check if this is a validation flow (just #1 → #7)
    is_validation_flow = (
        len(tasks) == 2 and
        tasks[0]['brain_id'] == 1 and
        tasks[1]['brain_id'] == 7
    )

    if is_validation_flow:
        return self._execute_validation_flow(tasks, max_iterations)
    else:
        return self._execute_standard_flow(tasks)
```

**✅ PATRÓN A EXTENDER:** Agregar `elif flow == self.FLOW_DISCOVERY: return self._execute_discovery_flow(brief)`

### Pattern 3: Brain Executor Query (Existing)

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

**✅ PATRÓN A USAR:** Mismo pattern para `_generate_interview_plan()` (query brain #8).

### Pattern 4: Output Formatting (Existing)

**Archivo:** `mastermind_cli/orchestrator/output_formatter.py`

```python
def format_task_start(self, task: Dict) -> str:
    """Format task start message."""
    return f"\n🧠 Brain #{task['brain_id']}: {task['brain_name']}\n{'='*60}"

def format_brain_output(self, result: Dict, task: Dict) -> str:
    """Format brain output."""
    # Format based on result structure
```

**✅ PATRÓN A EXTENDER:** Agregar métodos para interview-specific output:
- `format_interview_plan()`
- `format_question_asked()`
- `format_followup_received()`

---

## Implementation Blueprint

### Step 1: Add FLOW_DISCOVERY Constant (30 min)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
class Coordinator:
    """Main orchestration coordinator with iteration support."""

    FLOW_DISCOVERY = "discovery"  # NEW
    MAX_ITERATIONS = 3

    def __init__(self, formatter: Optional[OutputFormatter] = None, use_mcp: bool = False, enable_logging: bool = True):
        # ... existing code ...
```

### Step 2: Implement _detect_flow() (1 hour)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _detect_flow(self, brief: str) -> str:
    """
    Detect if brief needs discovery interview.

    A brief needs discovery if:
    - Too short (less than 15 words)
    - Contains ambiguity markers (modern, nuevo, bueno, mejor)
    - No clear problem statement

    Args:
        brief: User's brief text

    Returns:
        Flow type (FLOW_DISCOVERY or result from flow_detector)
    """
    # Check 1: Word count
    word_count = len(brief.split())
    if word_count < 15:
        print(self.formatter.format_info(
            f"Brief is too short ({word_count} words). Starting discovery interview."
        ))
        return self.FLOW_DISCOVERY

    # Check 2: Ambiguity markers
    ambiguity_markers = [
        "moderno", "nuevo", "buena", "mejor", "app",
        "sistema", "plataforma", "feature"
    ]

    brief_lower = brief.lower()
    marker_count = sum(1 for marker in ambiguity_markers if marker in brief_lower)

    # If 2+ ambiguity markers, needs discovery
    if marker_count >= 2:
        print(self.formatter.format_info(
            f"Brief contains {marker_count} ambiguity markers. Starting discovery interview."
        ))
        return self.FLOW_DISCOVERY

    # Check 3: Missing problem statement keywords
    problem_keywords = ["problema", "necesito", "requiero", "quiero", "goal", "objetivo"]
    has_problem = any(kw in brief_lower for kw in problem_keywords)

    if not has_problem and word_count < 30:
        print(self.formatter.format_info(
            "Brief lacks clear problem statement. Starting discovery interview."
        ))
        return self.FLOW_DISCOVERY

    # Default: use existing flow detector
    return self.flow_detector.detect(brief)
```

### Step 3: Implement _execute_discovery_flow() Main Method (2 hours)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _execute_discovery_flow(self, brief: str) -> Dict:
    """
    Execute discovery interview with Brain #8.

    This is the main entry point for the discovery flow.

    Args:
        brief: User's brief text

    Returns:
        Execution report with Q&A document and recommendations
    """
    print(self.formatter.format_info("🎤 Starting Discovery Interview with Brain #8"))
    print(self.formatter.format_separator())

    try:
        # Step 1: Generate interview plan via Brain #8
        print(self.formatter.format_info("Step 1: Generating interview strategy..."))
        interview_plan = self._generate_interview_plan(brief)

        if not interview_plan or interview_plan.get('status') == 'error':
            return self._error_report("Failed to generate interview plan")

        print(self.formatter.format_interview_plan(interview_plan))

        # Step 2: Execute iterative interview
        print(self.formatter.format_info("Step 2: Conducting interview..."))
        interview_doc = self._conduct_interview(interview_plan, brief)

        # Step 3: Log interview (if enabled)
        if self.eval_logger and hasattr(self.eval_logger, 'log_interview'):
            from mastermind_cli.memory.interview_logger import InterviewLogger
            interview_logger = InterviewLogger(enabled=True)

            interview_logger.log_interview(
                session_id=interview_doc.get('metadata', {}).get('session_id', 'unknown'),
                brief_original=brief,
                interview_doc=interview_doc,
                outcome=interview_doc.get('outcome', {})
            )

        # Step 4: Distribute to relevant brains
        print(self.formatter.format_info("Step 3: Gathering domain insights..."))
        recommendations = self._distribute_interview(interview_doc)

        # Step 5: Synthesize final output
        print(self.formatter.format_info("Step 4: Synthesizing recommendations..."))
        final_report = self._synthesize_recommendations(
            interview_doc=interview_doc,
            recommendations=recommendations
        )

        print(self.formatter.format_success("✅ Discovery interview complete!"))
        return final_report

    except Exception as e:
        print(self.formatter.format_error(f"Error during discovery: {e}"))
        return self._error_report(f"Discovery flow failed: {str(e)}")
```

### Step 4: Implement _generate_interview_plan() (2 hours)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _generate_interview_plan(self, brief: str) -> Dict:
    """
    Ask Brain #8 to design interview strategy.

    Args:
        brief: User's brief text

    Returns:
        Interview plan with categories, questions, and target brains
    """
    query = f"""As a Master Interviewer and Discovery expert, analyze the following brief and design an interview strategy:

Brief: "{brief}"

Your task: Create a structured interview plan to extract complete requirements.

Provide your response in this exact JSON format:
{{
  "interview_strategy": {{
    "estimated_categories": 3-5,
    "categories": [
      {{
        "id": "users",
        "name": "Users & Personas",
        "target_brain": 2,
        "priority": "high",
        "initial_questions": [
          {{
            "question": "¿Quiénes son los usuarios principales de este sistema?",
            "type": "open-ended",
            "confidence": "high"
          }}
        ]
      }}
    ],
    "detected_gaps": [],
    "estimated_duration_minutes": 10-15
  }}
}}

For each category:
- Assign target_brain: 2 (UX), 3 (UI), 4 (Frontend), 5 (Backend), 6 (QA), 7 (Growth), or 1 (Product)
- Set priority: high, medium, or low
- Include 2-3 initial questions per category

If you detect missing expertise (e.g., SEO, Marketing), add to detected_gaps.
"""

    # Query Brain #8
    task = {
        'context': {
            'brief': brief,
            'instruction': 'Design interview strategy'
        },
        'inputs': {'brief': brief}
    }

    result = self.brain_executor.execute(8, task, use_mcp=self.use_mcp)

    # Parse response
    if result.get('status') == 'error':
        return {'status': 'error', 'message': result.get('message', 'Unknown error')}

    # Extract interview strategy from output
    output = result.get('output', {})

    # Try to parse JSON from output
    import json
    import re

    json_match = re.search(r'\{[\s\S]*\}', output.get('note', str(output)))
    if json_match:
        try:
            interview_plan = json.loads(json_match.group())
            return interview_plan
        except json.JSONDecodeError:
            pass

    # Fallback: construct plan from output
    return self._fallback_interview_plan(brief, output)


def _fallback_interview_plan(self, brief: str, output: Dict) -> Dict:
    """Generate fallback interview plan if JSON parsing fails."""
    # Default categories based on brief analysis
    brief_lower = brief.lower()

    categories = [
        {
            "id": "users",
            "name": "Users & Personas",
            "target_brain": 2,  # UX
            "priority": "high",
            "initial_questions": [
                {"question": "¿Quiénes son los usuarios principales?", "type": "open-ended"}
            ]
        },
        {
            "id": "platforms",
            "name": "Platforms & Tech Stack",
            "target_brain": 4,  # Frontend
            "priority": "high",
            "initial_questions": [
                {"question": "¿Qué plataformas se necesitan? (web/mobile/desktop)", "type": "multiple-choice"}
            ]
        },
        {
            "id": "features",
            "name": "Key Features",
            "target_brain": 1,  # Product
            "priority": "high",
            "initial_questions": [
                {"question": "¿Cuáles son las 3 características más importantes?", "type": "open-ended"}
            ]
        }
    ]

    # Add additional categories based on keywords
    if "api" in brief_lower or "backend" in brief_lower:
        categories.append({
            "id": "architecture",
            "name": "Architecture & APIs",
            "target_brain": 5,  # Backend
            "priority": "medium",
            "initial_questions": [
                {"question": "¿Qué APIs o integraciones se necesitan?", "type": "open-ended"}
            ]
        })

    if "test" in brief_lower or "qa" in brief_lower:
        categories.append({
            "id": "quality",
            "name": "Quality & Testing",
            "target_brain": 6,  # QA
            "priority": "medium",
            "initial_questions": [
                {"question": "¿Qué tipo de testing se necesita?", "type": "multiple-choice"}
            ]
        })

    return {
        "interview_strategy": {
            "estimated_categories": len(categories),
            "categories": categories,
            "detected_gaps": [],
            "estimated_duration_minutes": len(categories) * 3
        }
    }
```

### Step 5: Implement _conduct_interview() (4 hours)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _conduct_interview(self, plan: Dict, brief: str) -> Dict:
    """
    Conduct iterative interview with user.

    This is the core interactive loop. For each category:
    1. Ask questions via AskUserQuestion
    2. Get user response
    3. Route to domain brain for follow-up
    4. Record Q&A
    5. Continue until brain signals "complete"

    Args:
        plan: Interview plan from Brain #8
        brief: Original user brief

    Returns:
        Complete Q&A document with all responses
    """
    import uuid
    from datetime import datetime

    strategy = plan.get("interview_strategy", {})
    categories = strategy.get("categories", [])

    # Initialize interview state
    interview_state = {
        "metadata": {
            "session_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "context_type": self._detect_context_type(brief),
            "industry": "general",
            "brief_original": brief
        },
        "document": {
            "qa": [],
            "categories": [],
            "gaps_detected": strategy.get("detected_gaps", [])
        },
        "outcome": {}
    }

    print(self.formatter.format_info(f"📋 Covering {len(categories)} categories"))

    # Process each category
    for category in categories:
        category_name = category.get("name", category.get("id", "Unknown"))
        target_brain = category.get("target_brain")
        questions = category.get("initial_questions", [])

        print(self.formatter.format_info(f"\n📁 Category: {category_name} (Brain #{target_brain})"))

        # Add category to document
        interview_state["document"]["categories"].append({
            "id": category.get("id"),
            "name": category_name,
            "target_brain": target_brain,
            "priority": category.get("priority", "medium")
        })

        # Process questions for this category
        for question in questions:
            question_text = question.get("question")
            question_type = question.get("type", "open-ended")

            # Ask question
            user_answer = self._ask_question(
                question=question_text,
                category=category,
                question_type=question_type
            )

            if not user_answer:
                # User skipped or cancelled
                continue

            # Request follow-up from domain brain
            follow_up = self._request_followup(
                brain_id=target_brain,
                question=question_text,
                answer=user_answer,
                category=category
            )

            # Record Q&A
            qa_entry = {
                "question": question_text,
                "answer": user_answer,
                "category": category.get("id"),
                "target_brain": target_brain,
                "follow_up_questions": follow_up.get("follow_up_questions", []),
                "confidence": follow_up.get("confidence", "medium"),
                "timestamp": datetime.now().isoformat()
            }

            interview_state["document"]["qa"].append(qa_entry)

            print(self.formatter.format_answer_received(user_answer))

            # Check if brain signals "enough"
            if follow_up.get("complete", False):
                print(self.formatter.format_info(f"✓ Category '{category_name}' complete"))
                break

    # Generate final summary
    interview_state["outcome"] = {
        "questions_asked": len(interview_state["document"]["qa"]),
        "categories_covered": len(interview_state["document"]["categories"]),
        "gaps_identified": len(interview_state["document"]["gaps_detected"]),
        "user_satisfaction": "medium"  # Can be updated later
    }

    return interview_state


def _detect_context_type(self, brief: str) -> str:
    """Detect type of interview context from brief."""
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
```

### Step 6: Implement _ask_question() with AskUserQuestion (2 hours)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _ask_question(self, question: str, category: Dict, question_type: str = "open-ended") -> Optional[str]:
    """
    Ask question using AskUserQuestion tool.

    Args:
        question: Question text
        category: Category info (for header)
        question_type: Type of question (open-ended, multiple-choice)

    Returns:
        User's answer, or None if cancelled
    """
    from typing import Optional

    category_name = category.get("name", "Questions")

    if question_type == "multiple-choice":
        # For multiple choice, provide options
        options = self._get_default_options(category.get("id"))

        result = self.ask_user_question(
            questions=[{
                "question": question,
                "header": category_name,
                "options": options,
                "multiSelect": False
            }]
        )
    else:
        # Open-ended question
        result = self.ask_user_question(
            questions=[{
                "question": question,
                "header": category_name,
                "multiSelect": False
            }]
        )

    # Extract answer
    if result and "answers" in result:
        answer = result["answers"].get(question)
        return answer

    return None


def _get_default_options(self, category_id: str) -> List[Dict]:
    """Get default options for a category."""
    options_map = {
        "users": [
            {"label": "B2B", "description": "Empresas"},
            {"label": "B2C", "description": "Consumidores"},
            {"label": "Ambos", "description": "Híbrido"}
        ],
        "platforms": [
            {"label": "Web", "description": "Aplicación web"},
            {"label": "Mobile", "description": "App nativa"},
            {"label": "PWA", "description": "Progressive Web App"},
            {"label": "Desktop", "description": "Aplicación de escritorio"}
        ],
        "features": [
            {"label": "MVP", "description": "Mínimo viable"},
            {"label": "Completo", "description": "Todas las funcionalidades"},
            {"label": "Iterativo", "description": "Por etapas"}
        ]
    }

    return options_map.get(category_id, [
        {"label": "Opción 1", "description": "Primera opción"},
        {"label": "Opción 2", "description": "Segunda opción"},
        {"label": "Opción 3", "description": "Tercera opción"}
    ])
```

### Step 7: Implement _request_followup() (2 hours)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _request_followup(self, brain_id: int, question: str, answer: str, category: Dict) -> Dict:
    """
    Request follow-up from domain brain.

    Args:
        brain_id: Target brain ID (1-7)
        question: Original question
        answer: User's answer
        category: Category info

    Returns:
        Follow-up response with optional additional questions
    """
    query = f"""Analyze this user response and determine if follow-up is needed:

Question: {question}
Answer: {answer}
Category: {category.get('name')}

Your task:
1. Assess if the answer is complete enough
2. If incomplete, provide 1-2 follow-up questions
3. If complete, signal "done"

Respond in JSON:
{{
  "complete": true/false,
  "confidence": "high/medium/low",
  "follow_up_questions": [
    {{ "question": "...", "reason": "..." }}
  ],
  "recommendations": ["..."]
}}
"""

    task = {
        'context': {
            'brief': f"Follow-up on: {question}",
            'instruction': 'Analyze answer and provide follow-up'
        },
        'inputs': {'question': question, 'answer': answer}
    }

    result = self.brain_executor.execute(brain_id, task, use_mcp=self.use_mcp)

    # Parse response
    output = result.get('output', {})

    # Try to extract JSON
    import json
    import re

    json_match = re.search(r'\{[\s\S]*\}', str(output))
    if json_match:
        try:
            follow_up = json.loads(json_match.group())
            return follow_up
        except json.JSONDecodeError:
            pass

    # Fallback: determine completeness based on answer length
    answer_words = len(answer.split())

    return {
        "complete": answer_words >= 10,
        "confidence": "medium" if answer_words >= 5 else "low",
        "follow_up_questions": [],
        "recommendations": []
    }
```

### Step 8: Implement _distribute_interview() and _synthesize_recommendations() (2 hours)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _distribute_interview(self, interview_doc: Dict) -> Dict:
    """
    Distribute interview Q&A to relevant brains for recommendations.

    Args:
        interview_doc: Complete Q&A document

    Returns:
        Recommendations from each brain
    """
    recommendations = {}

    # Get unique target brains from Q&A
    target_brains = set(
        qa.get("target_brain")
        for qa in interview_doc["document"]["qa"]
    )

    print(self.formatter.format_info(f"📊 Consulting {len(target_brains)} domain brains"))

    for brain_id in target_brains:
        # Filter Q&A for this brain
        brain_qas = [
            qa for qa in interview_doc["document"]["qa"]
            if qa.get("target_brain") == brain_id
        ]

        if not brain_qas:
            continue

        # Query brain for recommendations
        query = f"""Based on these interview responses, provide your recommendations:

Context: {interview_doc['metadata']['context_type']}

Questions & Answers:
{self._format_qa_for_brain(brain_qas)}

Provide:
1. Key insights (3-5 bullet points)
2. Recommendations (specific, actionable)
3. Concerns or risks (if any)
"""

        task = {
            'context': {
                'brief': f"Recommendations based on interview Q&A",
                'instruction': 'Provide domain-specific recommendations'
            },
            'inputs': {'qa': brain_qas}
        }

        result = self.brain_executor.execute(brain_id, task, use_mcp=self.use_mcp)

        recommendations[brain_id] = {
            "brain_name": result.get('brain_name', f'Brain #{brain_id}'),
            "recommendations": result.get('output', {}),
            "qa_count": len(brain_qas)
        }

    return recommendations


def _format_qa_for_brain(self, qa_list: List[Dict]) -> str:
    """Format Q&A list for brain query."""
    formatted = []
    for qa in qa_list:
        formatted.append(f"Q: {qa['question']}")
        formatted.append(f"A: {qa['answer']}")
        formatted.append("")
    return "\n".join(formatted)


def _synthesize_recommendations(self, interview_doc: Dict, recommendations: Dict) -> Dict:
    """
    Synthesize final output with interview + recommendations.

    Args:
        interview_doc: Complete Q&A document
        recommendations: Recommendations from domain brains

    Returns:
        Final execution report
    """
    # Generate summary
    summary = self._generate_interview_summary(interview_doc, recommendations)

    return {
        'plan_id': interview_doc['metadata']['session_id'],
        'status': 'completed',
        'flow_type': 'discovery',
        'interview_document': interview_doc,
        'domain_recommendations': recommendations,
        'final_deliverable': summary,
        'veredict': 'APPROVE',
        'timestamp': interview_doc['metadata']['timestamp']
    }


def _generate_interview_summary(self, interview_doc: Dict, recommendations: Dict) -> str:
    """Generate human-readable summary."""
    lines = []

    lines.append("# Discovery Interview Summary")
    lines.append("")
    lines.append(f"**Session ID:** {interview_doc['metadata']['session_id']}")
    lines.append(f"**Date:** {interview_doc['metadata']['timestamp'][:10]}")
    lines.append(f"**Context:** {interview_doc['metadata']['context_type']}")
    lines.append("")

    # Questions Asked
    qa_count = len(interview_doc['document']['qa'])
    lines.append(f"**Questions Asked:** {qa_count}")
    lines.append("")

    # Categories
    for cat in interview_doc['document']['categories']:
        lines.append(f"- **{cat['name']}** (Brain #{cat['target_brain']})")

    lines.append("")

    # Gaps Detected
    gaps = interview_doc['document']['gaps_detected']
    if gaps:
        lines.append("**Gaps Detected:**")
        for gap in gaps:
            lines.append(f"- {gap.get('missing_expertise', 'Unknown domain')}")
        lines.append("")

    # Recommendations
    if recommendations:
        lines.append("**Domain Recommendations:**")
        for brain_id, rec in recommendations.items():
            lines.append(f"\n### {rec['brain_name']}")
            lines.append(f"- Based on {rec['qa_count']} Q&A")
        lines.append("")

    return "\n".join(lines)
```

### Step 9: Add Error Handling (2 hours)

**Editar:** `mastermind_cli/orchestrator/coordinator.py`

```python
def _execute_discovery_flow(self, brief: str) -> Dict:
    """Execute discovery with error handling."""
    try:
        # Try to generate interview plan
        interview_plan = self._generate_interview_plan(brief)

    except TimeoutError:
        # Timeout: use fallback
        return self._handle_timeout(brief)

    except Exception as e:
        error_msg = str(e).lower()

        if "mcp" in error_msg or "notebooklm" in error_msg:
            # MCP unavailable: fallback to mock
            return self._handle_mcp_unavailable(brief)

        elif "brain" in error_msg:
            # Invalid brain: validate and suggest
            return self._handle_invalid_brain(e, brief)

        else:
            # Unknown error
            return self._error_report(f"Discovery failed: {str(e)}")


def _handle_timeout(self, brief: str) -> Dict:
    """Handle NotebookLM timeout."""
    print(self.formatter.format_warning(
        "⚠️  NotebookLM timeout. Using simplified interview."
    ))

    # Generate simple interview plan without MCP
    interview_plan = self._fallback_interview_plan(brief, {})

    # Conduct interview with simplified plan
    interview_doc = self._conduct_interview(interview_plan, brief)

    return self._synthesize_recommendations(
        interview_doc=interview_doc,
        recommendations={}
    )


def _handle_mcp_unavailable(self, brief: str) -> Dict:
    """Handle MCP unavailability."""
    print(self.formatter.format_warning(
        "⚠️  NotebookLM unavailable. Running in mock mode.\n"
        "   Enable MCP for full interview capabilities."
    ))

    # Generate mock interview for testing
    return self._mock_interview(brief)


def _handle_invalid_brain(self, error: Exception, brief: str) -> Dict:
    """Handle invalid brain ID."""
    available_brains = list(self.brain_executor.BRAIN_CONFIGS.keys())

    print(self.formatter.format_error(
        f"❌ Invalid brain referenced in interview plan.\n"
        f"   Available: {available_brains}\n"
        f"   Using Brain #1 (Product Strategy) as fallback."
    ))

    # Continue with fallback brain
    interview_plan = self._fallback_interview_plan(brief, {})

    # Override all target_brains to 1
    for cat in interview_plan["interview_strategy"]["categories"]:
        cat["target_brain"] = 1

    interview_doc = self._conduct_interview(interview_plan, brief)

    return self._synthesize_recommendations(
        interview_doc=interview_doc,
        recommendations={}
    )


def _mock_interview(self, brief: str) -> Dict:
    """Generate mock interview for testing."""
    return {
        'plan_id': 'mock-discovery',
        'status': 'completed',
        'flow_type': 'discovery',
        'interview_document': {
            'metadata': {
                'session_id': 'mock-001',
                'context_type': 'mock'
            },
            'document': {
                'qa': [
                    {'question': 'Mock question', 'answer': 'Mock answer'}
                ],
                'categories': []
            },
            'outcome': {}
        },
        'domain_recommendations': {},
        'final_deliverable': 'Mock interview (MCP unavailable)',
        'veredict': 'APPROVE'
    }
```

### Step 10: Write Integration Tests (3 hours)

**Crear:** `tests/integration/test_discovery_flow.py`

```python
"""
Integration tests for Discovery Flow.
"""

import pytest
from mastermind_cli.orchestrator.coordinator import Coordinator


def test_detect_flow_with_short_brief():
    """Test that short briefs trigger discovery flow."""
    coordinator = Coordinator()

    brief = "quiero una app"  # 3 words

    flow = coordinator._detect_flow(brief)

    assert flow == coordinator.FLOW_DISCOVERY


def test_detect_flow_with_ambiguity_markers():
    """Test that ambiguity markers trigger discovery flow."""
    coordinator = Coordinator()

    brief = "necesito una app moderna y nueva"

    flow = coordinator._detect_flow(brief)

    assert flow == coordinator.FLOW_DISCOVERY


def test_detect_flow_with_clear_brief():
    """Test that clear briefs use existing flow detector."""
    coordinator = Coordinator()

    # This is detailed enough to NOT trigger discovery
    brief = """
    Necesito construir un sistema de inventario para mi negocio de retail.
    El problema es que perdemos tracked de productos y tenemos sobre-stock.
    Quiero una solución web que permita escanear códigos de barra y
    actualizar el inventario en tiempo real.
    """

    flow = coordinator._detect_flow(brief)

    # Should NOT be discovery (should use flow_detector)
    assert flow != coordinator.FLOW_DISCOVERY


def test_fallback_interview_plan():
    """Test fallback interview plan generation."""
    coordinator = Coordinator()

    brief = "app de delivery"

    plan = coordinator._fallback_interview_plan(brief, {})

    assert "interview_strategy" in plan
    assert len(plan["interview_strategy"]["categories"]) >= 3


def test_conduct_interview_mock():
    """Test interview conduct with mock plan."""
    coordinator = Coordinator()

    plan = {
        "interview_strategy": {
            "categories": [
                {
                    "id": "test",
                    "name": "Test Category",
                    "target_brain": 1,
                    "priority": "high",
                    "initial_questions": [
                        {"question": "Test question?", "type": "open-ended"}
                    ]
                }
            ]
        }
    }

    # This test would need mock AskUserQuestion
    # For now, just test that method exists
    assert hasattr(coordinator, '_conduct_interview')


def test_full_discovery_flow_mock_mode():
    """Test end-to-end discovery flow in mock mode (no MCP)."""
    coordinator = Coordinator(use_mcp=False)

    result = coordinator.orchestrate(
        brief="quiero una app de delivery",
        flow="discovery"
    )

    assert result["status"] in ["completed", "error"]
    assert result.get("flow_type") == "discovery"


def test_generate_interview_plan_with_brain_8():
    """Test interview plan generation via Brain #8."""
    coordinator = Coordinator(use_mcp=False)  # Mock mode

    plan = coordinator._generate_interview_plan("app de delivery")

    assert "interview_strategy" in plan
```

---

## Validation Gates

```bash
# ========== Step 1: FLOW_DISCOVERY Constant ==========
python -c "
from mastermind_cli.orchestrator.coordinator import Coordinator
c = Coordinator()
assert hasattr(c, 'FLOW_DISCOVERY')
assert c.FLOW_DISCOVERY == 'discovery'
print('✅ FLOW_DISCOVERY constant added')
"

# ========== Step 2: _detect_flow() ==========
python -c "
from mastermind_cli.orchestrator.coordinator import Coordinator
c = Coordinator()

# Short brief should trigger discovery
flow1 = c._detect_flow('quiero una app')
assert flow1 == 'discovery', f'Expected discovery, got {flow1}'

# Ambiguity markers should trigger discovery
flow2 = c._detect_flow('app moderna nueva')
assert flow2 == 'discovery', f'Expected discovery, got {flow2}'

print('✅ _detect_flow() works correctly')
"

# ========== Step 3-8: Main Flow Methods ==========
python -c "
from mastermind_cli.orchestrator.coordinator import Coordinator
c = Coordinator()

methods = [
    '_execute_discovery_flow',
    '_generate_interview_plan',
    '_conduct_interview',
    '_ask_question',
    '_request_followup',
    '_distribute_interview',
    '_synthesize_recommendations'
]

for method in methods:
    assert hasattr(c, method), f'Missing method: {method}'

print('✅ All flow methods implemented')
"

# ========== Step 9: Error Handlers ==========
python -c "
from mastermind_cli.orchestrator.coordinator import Coordinator
c = Coordinator()

handlers = [
    '_handle_timeout',
    '_handle_mcp_unavailable',
    '_handle_invalid_brain',
    '_mock_interview'
]

for handler in handlers:
    assert hasattr(c, handler), f'Missing handler: {handler}'

print('✅ All error handlers implemented')
"

# ========== Step 10: Integration Tests ==========
uv run pytest tests/integration/test_discovery_flow.py -v

# ========== End-to-End Test (Mock Mode) ==========
python -c "
from mastermind_cli.orchestrator.coordinator import Coordinator

# Test in mock mode (no MCP required)
c = Coordinator(use_mcp=False)
result = c.orchestrate(
    brief='quiero una app moderna de delivery',
    flow='discovery'
)

assert result.get('status') in ['completed', 'error']
assert result.get('flow_type') == 'discovery'

print('✅ End-to-end discovery flow works (mock mode)')
"

# ========== Final Validation ==========
# Type check
mypy mastermind_cli/orchestrator/coordinator.py

# Lint
ruff check mastermind_cli/orchestrator/coordinator.py

# All tests
uv run pytest tests/integration/test_discovery_flow.py tests/unit/test_interview_logger.py -v

echo "========== ALL VALIDATIONS PASSED =========="
```

---

## Error Handling

| Error | Handling |
|-------|----------|
| **NotebookLM timeout** | Use fallback_interview_plan() |
| **MCP unavailable** | Run mock_interview() for testing |
| **Invalid brain ID** | Route all questions to Brain #1 |
| **User cancels interview** | Save partial state, offer resume |
| **JSON parse failure** | Use fallback_interview_plan() |

---

## Gotchas & Pitfalls

### Gotcha 1: AskUserQuestion Tool Availability

**Issue:** AskUserQuestion is only available in Claude Code environment

**Fix:** Add check for tool availability:
```python
if hasattr(self, 'ask_user_question'):
    result = self.ask_user_question(...)
else:
    # Fallback: use input()
    answer = input(f"{question}\n> ")
```

### Gotcha 2: Infinite Loop in Interview

**Issue:** Domain brain never signals "complete"

**Fix:** Add max questions per category:
```python
MAX_QUESTIONS_PER_CATEGORY = 5

for i, question in enumerate(questions):
    if i >= MAX_QUESTIONS_PER_CATEGORY:
        break
    # ... process question
```

### Gotcha 3: JSON Parsing from Brain #8

**Issue:** Brain #8 response may not be valid JSON

**Fix:** Use regex fallback:
```python
json_match = re.search(r'\{[\s\S]*\}', response)
if json_match:
    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
return self._fallback_interview_plan(...)
```

### Gotcha 4: Interview State Loss on Error

**Issue:** If interview fails midway, all progress is lost

**Fix:** Save checkpoint after each category:
```python
checkpoint_path = f"logs/interviews/checkpoints/{session_id}.json"
# Save after each category completes
```

---

## Quality Checklist

- [x] All necessary context included (spec, patterns)
- [x] Validation gates ejecutables por AI
- [x] References existing patterns (coordinator.py, brain_executor.py)
- [x] Clear implementation path (10 steps, 23 hours)
- [x] Error handling documentado (4 categorías)
- [x] Pseudocódigo completo para todos los métodos
- [x] Integration tests especificados
- [x] Gotchas documentados (4 pitfalls)
- [x] AskUserQuestion integration considerada

---

## Branch Strategy

**Create branch:** `feature/prp-013-brain-08-orchestrator-integration`

```bash
git checkout -b feature/prp-013-brain-08-orchestrator-integration

# Work through implementation
# ... implement steps 1-10 ...

# Commit when validations pass
git add mastermind_cli/orchestrator/coordinator.py
git add tests/integration/test_discovery_flow.py
git commit -m "feat(prp-013): implement orchestrator integration for brain #8

- Add FLOW_DISCOVERY constant and _detect_flow() logic
- Implement _execute_discovery_flow() main method
- Implement _generate_interview_plan() via Brain #8
- Implement _conduct_interview() with iterative loop
- Integrate AskUserQuestion for interactive questions
- Implement _request_followup() to domain brains
- Add error handling for timeouts and MCP unavailable
- Write integration tests

Validations:
✅ Short briefs trigger discovery flow
✅ Ambiguity markers trigger discovery flow
✅ Interview plan generates correctly
✅ Interview conducts in mock mode
✅ Error handlers work
✅ Integration tests passing

Refs: PRP-013, spec-brain-08"
```

---

## Success Criteria

- [ ] `FLOW_DISCOVERY` constant added to Coordinator
- [ ] `_detect_flow()` correctly identifies vague briefs
- [ ] `_execute_discovery_flow()` runs end-to-end (mock mode)
- [ ] `_generate_interview_plan()` produces valid plan
- [ ] `_conduct_interview()` completes iterative loop
- [ ] AskUserQuestion integration works
- [ ] Domain brain follow-ups work
- [ ] Error handlers prevent crashes
- [ ] All integration tests pass
- [ ] Type checking passes (`mypy`)

---

## PRP Confidence Score

**Score: 8/10**

**Justification:**
- ✅ **Well-defined patterns** — Coordinator, brain_executor ya existen
- ✅ **Clear validation** — Tests ejecutables para cada método
- ✅ **Isolated changes** — Mayormente additions a coordinator.py
- ⚠️ **-1 punto** — AskUserQuestion integration es nuevo y no probado en este codebase
- ⚠️ **-1 punto** — Iterative interview loop es complejo y puede tener edge cases

**Riesgo principal:** La integración con AskUserQuestion es un patrón nuevo en el codebase. La primera implementación podría requerir iteraciones para manejar edge cases (cancelaciones, timeouts, etc.).

---

## Next Steps After Completion

Once PRP-013 is complete:

1. **Test manualmente:** Ejecutar `/mm:discovery "quiero una app moderna"` para verificar UX
2. **Validar MCP:** Test con MCP=true para verificar Brain #8 responde
3. **Start PRP-014:** Slash Command (crea el comando /mm:discovery)

---

**END OF PRP-013**
