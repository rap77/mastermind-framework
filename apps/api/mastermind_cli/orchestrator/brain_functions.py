"""
Pure Function Brains - Stateless brain implementations.

All brains are pure functions: Input → Output (no state access).
This enables multi-user safety, testability, and parallel execution.

Architecture Principle:
"If every brain is a PURE FUNCTION (input → output),
we DON'T need shared state."
"""

import re
from typing import Protocol, runtime_checkable, Any, Literal

# Import interfaces from types module
# Use absolute import to avoid conflict with stdlib 'types' module
from mastermind_cli.types.interfaces import (
    BrainInput,
    ProductStrategy,
    UXResearch,
    UIDesign,
    FrontendDesign,
    BackendDesign,
    QADevOpsPlan,
    GrowthDataEvaluation,
    MasterInterviewerOutput,
)


# =============================================================================
# MCP CLIENT PROTOCOL
# =============================================================================


@runtime_checkable
class MCPClient(Protocol):
    """MCP client protocol for type hints."""

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
        """Query NotebookLM via MCP."""
        ...


# =============================================================================
# PARSING HELPERS - Shared across all brains
# =============================================================================


def _parse_sections(knowledge: str) -> dict[str, str]:
    """
    Parse LABEL: content blocks from NotebookLM structured response.

    Handles both inline (LABEL: value) and multiline (LABEL:\n- item) formats.
    """
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    for line in knowledge.split("\n"):
        # Detect UPPERCASE_KEY: pattern at start of line
        match = re.match(r"^([A-Z][A-Z_]+):\s*(.*)", line)
        if match:
            if current_key is not None:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = match.group(1)
            rest = match.group(2).strip()
            current_lines = [rest] if rest else []
        elif current_key is not None:
            current_lines.append(line)

    if current_key is not None:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections


def _parse_list(text: str) -> list[str]:
    """Parse bullet list items from text. Handles -, *, •, numbered."""
    items: list[str] = []
    for line in text.split("\n"):
        line = line.strip()
        cleaned = re.sub(r"^[-*•]\s+", "", line)
        cleaned = re.sub(r"^\d+\.\s+", "", cleaned)
        if cleaned and not cleaned.endswith(":"):
            items.append(cleaned)
    return items


def _get(sections: dict[str, str], key: str, default: str = "") -> str:
    """Get section value with fallback."""
    return sections.get(key, default) or default


def _get_list(
    sections: dict[str, str], key: str, default: list[str] | None = None
) -> list[str]:
    """Get section as parsed list with fallback."""
    text = sections.get(key, "")
    if not text:
        return default if default is not None else []
    items = _parse_list(text)
    return items if items else (default if default is not None else [])


def _get_context(brain_input: BrainInput, key: str) -> Any:
    """Get value from additional_context (outputs from previous brains)."""
    return brain_input.additional_context.get(key)


# =============================================================================
# BRAIN #1: PRODUCT STRATEGY
# =============================================================================


def brain_01_product_strategy(
    brain_input: BrainInput, mcp_client: MCPClient
) -> ProductStrategy:
    """
    Pure function: Product Strategy brain.

    NO self.state access. NO global variables.
    Only returns ProductStrategy output model.
    """
    notebook_id = "f276ccb3-0bce-4069-8b55-eae8693dbe75"
    brief = brain_input.brief

    query = f"""Based on the following product brief, provide a comprehensive product strategy analysis.

BRIEF: {brief.problem_statement}
CONTEXT: {brief.context}
CONSTRAINTS: {', '.join(brief.constraints)}
TARGET_AUDIENCE: {brief.target_audience or 'Not specified'}

Respond using EXACTLY these labeled sections:

POSITIONING: [unique value proposition and market position]
AUDIENCE: [specific target audience description]
FEATURES:
- [feature 1]
- [feature 2]
- [feature 3]
METRICS:
- [metric 1]
- [metric 2]
RISKS:
- [risk 1]
- [risk 2]

Use the labeled format exactly. Be specific and actionable."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)
    s = _parse_sections(knowledge)

    return ProductStrategy(
        brief=brief,
        positioning=_get(s, "POSITIONING", knowledge[:500]),
        target_audience=_get(
            s,
            "AUDIENCE",
            brief.target_audience or "Software developers and technical teams",
        ),
        key_features=_get_list(s, "FEATURES", ["Core feature 1", "Core feature 2"]),
        success_metrics=_get_list(
            s, "METRICS", ["User adoption rate", "Feature completion rate"]
        ),
        risks=_get_list(s, "RISKS", []),
    )


# =============================================================================
# BRAIN #2: UX RESEARCH
# =============================================================================


def brain_02_ux_research(brain_input: BrainInput, mcp_client: MCPClient) -> UXResearch:
    """
    Pure function: UX Research brain.

    Analyzes user journeys, pain points, and opportunities.
    Chains from Brain #1 output if available in additional_context.
    """
    notebook_id = "ea006ece-00a9-4d5c-91f5-012b8b712936"
    brief = brain_input.brief

    # Chain from Brain #1 if available
    strategy_context = ""
    prev = _get_context(brain_input, "brain-01-product-strategy")
    if prev and isinstance(prev, dict):
        strategy_context = f"\nProduct Strategy Context: {prev.get('positioning', '')}"

    query = f"""Analyze the user experience for the following product.

BRIEF: {brief.problem_statement}
TARGET_AUDIENCE: {brief.target_audience or 'General users'}{strategy_context}

Respond using EXACTLY these labeled sections:

JOURNEYS:
- [journey 1: user path description]
- [journey 2: user path description]
PAIN_POINTS:
- [pain point 1]
- [pain point 2]
OPPORTUNITIES:
- [opportunity 1]
- [opportunity 2]
SCREEN_FLOWS:
- [screen 1 → screen 2: action description]
- [screen 2 → screen 3: action description]
METHODOLOGY: [research approach description]

Use the labeled format exactly. Be specific about user behavior."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)
    s = _parse_sections(knowledge)

    journeys_raw = _get_list(
        s, "JOURNEYS", ["Primary user flow", "Secondary user flow"]
    )
    screen_flows_raw = _get_list(s, "SCREEN_FLOWS", [])

    return UXResearch(
        user_journeys=[{"step": j} for j in journeys_raw],
        pain_points=_get_list(s, "PAIN_POINTS", ["Complexity", "Lack of feedback"]),
        opportunities=_get_list(s, "OPPORTUNITIES", ["Simplification", "Automation"]),
        research_methodology=_get(s, "METHODOLOGY", "NotebookLM-based UX analysis"),
        screen_flows=[{"flow": f} for f in screen_flows_raw],
    )


# =============================================================================
# BRAIN #3: UI DESIGN
# =============================================================================


def brain_03_ui_design(brain_input: BrainInput, mcp_client: MCPClient) -> UIDesign:
    """
    Pure function: UI Design brain.

    Generates visual design system and component hierarchy.
    Chains from Brain #2 (UX Research) if available.
    """
    notebook_id = "8d544475-6860-4cd7-9037-8549325493dd"
    brief = brain_input.brief

    # Chain from Brain #2 if available
    ux_context = ""
    prev = _get_context(brain_input, "brain-02-ux-research")
    if prev and isinstance(prev, dict):
        pain_points = ", ".join(prev.get("pain_points", [])[:3])
        ux_context = f"\nUX Research Context: Key pain points: {pain_points}"

    query = f"""Based on the following product brief, provide a comprehensive UI design system.

BRIEF: {brief.problem_statement}
TARGET_AUDIENCE: {brief.target_audience or 'General users'}
CONTEXT: {brief.context}{ux_context}

Respond using EXACTLY these labeled sections:

VISUAL_LANGUAGE: [style description, aesthetic, mood, tone]
COLOR_PRIMARY: [hex value]
COLOR_SECONDARY: [hex value]
COLOR_ACCENT: [hex value]
COLOR_BACKGROUND: [hex value]
COLOR_TEXT: [hex value]
TYPOGRAPHY_HEADING: [font name and weight]
TYPOGRAPHY_BODY: [font name and weight]
TYPOGRAPHY_MONO: [font name for code]
SPACING_SYSTEM: [spacing scale description, e.g. 4px base, 8-16-24-32-48]
COMPONENTS:
- [component 1: description]
- [component 2: description]
- [component 3: description]
PRINCIPLES:
- [principle 1]
- [principle 2]
- [principle 3]

Use the labeled format exactly."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)
    s = _parse_sections(knowledge)

    return UIDesign(
        visual_language=_get(s, "VISUAL_LANGUAGE", knowledge[:500]),
        color_palette={
            "primary": _get(s, "COLOR_PRIMARY", "#6366f1"),
            "secondary": _get(s, "COLOR_SECONDARY", "#8b5cf6"),
            "accent": _get(s, "COLOR_ACCENT", "#06b6d4"),
            "background": _get(s, "COLOR_BACKGROUND", "#0f172a"),
            "text": _get(s, "COLOR_TEXT", "#f8fafc"),
        },
        typography={
            "heading": _get(s, "TYPOGRAPHY_HEADING", "Inter, 600"),
            "body": _get(s, "TYPOGRAPHY_BODY", "Inter, 400"),
            "mono": _get(s, "TYPOGRAPHY_MONO", "JetBrains Mono"),
        },
        spacing_system=_get(s, "SPACING_SYSTEM", "4px base — 8/16/24/32/48/64px scale"),
        component_hierarchy=[
            {
                "name": c.split(":")[0].strip(),
                "description": c.split(":", 1)[-1].strip(),
            }
            for c in _get_list(
                s, "COMPONENTS", ["Header: navigation", "BrainCard: status display"]
            )
        ],
        design_principles=_get_list(
            s,
            "PRINCIPLES",
            ["Accessibility first", "Consistent spacing", "Dark mode native"],
        ),
    )


# =============================================================================
# BRAIN #4: FRONTEND
# =============================================================================


def brain_04_frontend(brain_input: BrainInput, mcp_client: MCPClient) -> FrontendDesign:
    """
    Pure function: Frontend brain.

    Defines technical frontend architecture and implementation.
    Chains from Brain #3 (UI Design) if available.
    """
    notebook_id = "85e47142-0a65-41d9-9848-49b8b5d2db33"
    brief = brain_input.brief

    # Chain from Brain #3 if available
    design_context = ""
    prev = _get_context(brain_input, "brain-03-ui-design")
    if prev and isinstance(prev, dict):
        visual = prev.get("visual_language", "")
        design_context = f"\nUI Design Context: {visual[:200]}"

    query = f"""Based on the following product brief, provide a concrete frontend architecture specification.

BRIEF: {brief.problem_statement}
CONTEXT: {brief.context}
CONSTRAINTS: {', '.join(brief.constraints)}{design_context}

Respond using EXACTLY these labeled sections:

FRAMEWORK: [framework name and version with justification]
STATE_MANAGEMENT: [approach and library]
STYLING: [CSS solution and libraries]
ROUTING: [routing strategy and key routes]
COMPONENTS_PAGES:
- [page 1]
- [page 2]
COMPONENTS_LAYOUT:
- [layout component 1]
- [layout component 2]
COMPONENTS_SHARED:
- [shared component 1]
- [shared component 2]
BUILD_TOOLS:
- [tool 1]
- [tool 2]
PERFORMANCE:
- [target 1, e.g. LCP < 2.5s]
- [target 2]

Use the labeled format exactly. Be concrete and implementation-ready."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)
    s = _parse_sections(knowledge)

    pages = _get_list(
        s,
        "COMPONENTS_PAGES",
        ["CommandCenter", "TheNexus", "StrategyVault", "EngineRoom"],
    )
    layout = _get_list(s, "COMPONENTS_LAYOUT", ["AppShell", "Sidebar", "Header"])
    shared = _get_list(
        s, "COMPONENTS_SHARED", ["BrainCard", "StatusBadge", "OutputPanel"]
    )

    return FrontendDesign(
        framework=_get(s, "FRAMEWORK", "Next.js 16 + React 19"),
        component_hierarchy={"pages": pages, "layout": layout, "shared": shared},
        state_management=_get(s, "STATE_MANAGEMENT", "Zustand 5"),
        styling_approach=_get(s, "STYLING", "Tailwind CSS 4 + shadcn/ui + Magic UI"),
        routing_strategy=_get(s, "ROUTING", "Next.js App Router — file-based routing"),
        performance_targets=_get_list(s, "PERFORMANCE", ["LCP < 2.5s", "FID < 100ms"]),
        build_tools=_get_list(
            s, "BUILD_TOOLS", ["Next.js 16", "TypeScript 5", "ESLint"]
        ),
    )


# =============================================================================
# BRAIN #5: BACKEND
# =============================================================================


def brain_05_backend(brain_input: BrainInput, mcp_client: MCPClient) -> BackendDesign:
    """
    Pure function: Backend brain.

    Defines backend architecture, API design, and data models.
    Chains from Brain #1 (Product Strategy) if available.
    """
    notebook_id = "c6befbbc-b7dd-4ad0-a677-314750684208"
    brief = brain_input.brief

    # Chain from Brain #1 if available
    strategy_context = ""
    prev = _get_context(brain_input, "brain-01-product-strategy")
    if prev and isinstance(prev, dict):
        features = ", ".join(prev.get("key_features", [])[:3])
        strategy_context = f"\nProduct Strategy Context: Key features: {features}"

    query = f"""Based on the following product brief, provide a concrete backend architecture specification.

BRIEF: {brief.problem_statement}
CONTEXT: {brief.context}
CONSTRAINTS: {', '.join(brief.constraints)}{strategy_context}

Respond using EXACTLY these labeled sections:

ARCHITECTURE: [architecture pattern with rationale]
API_DESIGN: [API approach, protocols, versioning]
DATA_MODEL_1: [entity name: fields description]
DATA_MODEL_2: [entity name: fields description]
DATA_MODEL_3: [entity name: fields description]
AUTHENTICATION: [auth strategy]
PERFORMANCE:
- [requirement 1, e.g. p99 < 200ms]
- [requirement 2]

Use the labeled format exactly. Be concrete and implementation-ready."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)
    s = _parse_sections(knowledge)

    data_models = []
    for i in range(1, 6):
        val = s.get(f"DATA_MODEL_{i}", "")
        if val:
            parts = val.split(":", 1)
            data_models.append(
                {
                    "name": parts[0].strip(),
                    "fields": _parse_list(parts[1]) if len(parts) > 1 else [],
                }
            )

    if not data_models:
        data_models = [
            {"name": "Execution", "fields": ["id", "brief", "status", "created_at"]},
            {"name": "BrainOutput", "fields": ["brain_id", "content", "execution_id"]},
        ]

    return BackendDesign(
        architecture=_get(s, "ARCHITECTURE", "FastAPI + Python 3.14 — monolith"),
        api_design=_get(s, "API_DESIGN", "REST + WebSocket"),
        data_models=data_models,
        authentication=_get(
            s, "AUTHENTICATION", "JWT (30min) + refresh rotation (24h) + API Keys"
        ),
    )


# =============================================================================
# BRAIN #6: QA/DEVOPS
# =============================================================================


def brain_06_qa_devops(brain_input: BrainInput, mcp_client: MCPClient) -> QADevOpsPlan:
    """
    Pure function: QA/DevOps brain.

    Defines testing strategy and deployment pipeline.
    Chains from Brain #4 (Frontend) + Brain #5 (Backend) if available.
    """
    notebook_id = "74cd3a81-1350-4927-af14-c0c4fca41a8e"
    brief = brain_input.brief

    # Chain from Brains #4 and #5 if available
    tech_context = ""
    prev_fe = _get_context(brain_input, "brain-04-frontend")
    prev_be = _get_context(brain_input, "brain-05-backend")
    if prev_fe and isinstance(prev_fe, dict):
        tech_context += f"\nFrontend: {prev_fe.get('framework', '')} + {prev_fe.get('styling_approach', '')}"
    if prev_be and isinstance(prev_be, dict):
        tech_context += f"\nBackend: {prev_be.get('architecture', '')} — {prev_be.get('api_design', '')}"

    query = f"""Based on the following product brief, provide a concrete QA and DevOps strategy.

BRIEF: {brief.problem_statement}
CONTEXT: {brief.context}{tech_context}

Respond using EXACTLY these labeled sections:

TESTING_STRATEGY: [overall testing approach with coverage targets]
UNIT_TESTING: [framework and patterns]
INTEGRATION_TESTING: [approach and key integration points]
E2E_TESTING: [framework and key user flows to test]
CI_CD: [pipeline stages and tools]
MONITORING: [observability approach, logging, alerting]
DEPLOYMENT: [deployment strategy and infrastructure]

Use the labeled format exactly. Be concrete and actionable."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)
    s = _parse_sections(knowledge)

    testing_parts = [
        _get(s, "TESTING_STRATEGY", ""),
        _get(s, "UNIT_TESTING", ""),
        _get(s, "INTEGRATION_TESTING", ""),
        _get(s, "E2E_TESTING", ""),
    ]
    testing_strategy = (
        " | ".join(p for p in testing_parts if p) or "pytest + Playwright"
    )

    return QADevOpsPlan(
        testing_strategy=testing_strategy,
        ci_cd_pipeline=_get(
            s, "CI_CD", "GitHub Actions: typecheck → pytest → semantic regression"
        ),
        monitoring=_get(
            s, "MONITORING", "Structured logging (JSON) + health endpoints"
        ),
        deployment_strategy=_get(
            s, "DEPLOYMENT", "Multi-stage Docker → docker compose up -d"
        ),
    )


# =============================================================================
# BRAIN #7: GROWTH & DATA (EVALUATOR)
# =============================================================================


def brain_07_growth_data(
    brain_input: BrainInput,
    mcp_client: MCPClient,
    previous_outputs: dict[str, Any] | None = None,
) -> GrowthDataEvaluation:
    """
    Pure function: Growth & Data brain (Evaluator).

    Evaluates all previous brain outputs and provides verdict.
    """
    notebook_id = "d8de74d6-7028-44ed-b4d5-784d6a9256e6"

    context = "\n".join(
        f"{brain_id}: {output}" for brain_id, output in (previous_outputs or {}).items()
    )

    query = f"""Evaluate the following product development outputs critically.

ORIGINAL_BRIEF: {brain_input.brief.problem_statement}

OUTPUTS_TO_EVALUATE:
{context}

Respond using EXACTLY these labeled sections:

VERDICT: [APPROVE, CONDITIONAL, REJECT, or ESCALATE]
SCORE: [number from 0 to 10]
FEEDBACK: [detailed evaluation of overall quality and coherence]
CONDITIONS:
- [condition 1 if CONDITIONAL — what needs to change]
- [condition 2 if CONDITIONAL]
REJECTION_REASONS:
- [reason 1 if REJECT]
- [reason 2 if REJECT]

Use the labeled format exactly. Be rigorous — quality over approval."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)
    s = _parse_sections(knowledge)

    return GrowthDataEvaluation(
        verdict=_extract_verdict(s),
        score=_extract_score(s, knowledge),
        feedback=_get(s, "FEEDBACK", knowledge[:1000]),
        approval_conditions=_get_list(s, "CONDITIONS", []),
        rejection_reasons=_get_list(s, "REJECTION_REASONS", []),
    )


def _extract_verdict(
    s: dict[str, str],
) -> Literal["APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"]:
    """Extract verdict from parsed sections."""
    verdict_raw = s.get("VERDICT", "").upper()
    for v in ("APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"):
        if v in verdict_raw:
            return v
    return "CONDITIONAL"


def _extract_score(s: dict[str, str], knowledge: str) -> float:
    """Extract numeric score from parsed sections or raw knowledge."""
    score_text = s.get("SCORE", "")
    numbers = re.findall(r"\b(10|[0-9](?:\.[0-9])?)\b", score_text or knowledge)
    if numbers:
        return min(float(numbers[0]), 10.0)
    return 7.0


# =============================================================================
# BRAIN #8: MASTER INTERVIEWER (DISCOVERY)
# =============================================================================


def brain_08_master_interviewer(
    brain_input: BrainInput, mcp_client: MCPClient
) -> MasterInterviewerOutput:
    """
    Pure function: Master Interviewer brain (Discovery).

    Detects ambiguity in brief and generates real clarifying questions
    from NotebookLM knowledge.
    """
    notebook_id = "5330e845-29dc-4219-9d7e-c1ccb4851bb3"
    brief = brain_input.brief

    # Ambiguity detection (3-tier)
    word_count = len(brief.problem_statement.split())
    has_ambiguity_markers = any(
        marker in brief.problem_statement.lower()
        for marker in ["maybe", "possibly", "something", "thing", "stuff"]
    )
    missing_problem = (
        "?" in brief.problem_statement or "how do" in brief.problem_statement.lower()
    )

    is_ambiguous = (
        word_count < 15
        or brief.problem_statement.count("?") >= 2
        or has_ambiguity_markers
        or missing_problem
    )

    if not is_ambiguous:
        return MasterInterviewerOutput(
            is_ambiguous=False,
            interview_plan=[],
            clarified_brief=brief,
            confidence_score=0.9,
        )

    query = f"""The following product brief needs clarification. Generate 5 specific, insightful questions to understand the real problem.

BRIEF: {brief.problem_statement}
CONTEXT: {brief.context}

Respond using EXACTLY these labeled sections:

QUESTION_1: [specific question about problem definition]
CONTEXT_1: [why this question matters]
QUESTION_2: [specific question about target audience]
CONTEXT_2: [why this question matters]
QUESTION_3: [specific question about success criteria]
CONTEXT_3: [why this question matters]
QUESTION_4: [specific question about constraints or scope]
CONTEXT_4: [why this question matters]
QUESTION_5: [specific question about technical or business requirements]
CONTEXT_5: [why this question matters]

Use the labeled format exactly. Questions must be specific to this brief."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)
    s = _parse_sections(knowledge)

    interview_plan = []
    for i in range(1, 6):
        question = s.get(f"QUESTION_{i}", "")
        context = s.get(f"CONTEXT_{i}", "Clarification needed")
        if question:
            interview_plan.append({"question": question, "context": context})

    # Fallback if parsing failed
    if not interview_plan:
        interview_plan = [
            {
                "question": f"Q{i}: {knowledge[i*100:(i+1)*100].strip()}",
                "context": "From NotebookLM",
            }
            for i in range(min(5, len(knowledge) // 100))
        ]

    return MasterInterviewerOutput(
        is_ambiguous=True,
        interview_plan=interview_plan,
        clarified_brief=None,
        confidence_score=0.3,
    )


# =============================================================================
# BRAIN REGISTRY - Maps brain IDs to pure functions
# =============================================================================

BRAIN_FUNCTIONS = {
    "brain-01-product-strategy": brain_01_product_strategy,
    "brain-02-ux-research": brain_02_ux_research,
    "brain-03-ui-design": brain_03_ui_design,
    "brain-04-frontend": brain_04_frontend,
    "brain-05-backend": brain_05_backend,
    "brain-06-qa-devops": brain_06_qa_devops,
    "brain-07-growth-data": brain_07_growth_data,
    "brain-08-master-interviewer": brain_08_master_interviewer,
}


def get_brain_function(brain_id: str) -> Any:
    """Get pure function for brain ID."""
    return BRAIN_FUNCTIONS.get(brain_id)
