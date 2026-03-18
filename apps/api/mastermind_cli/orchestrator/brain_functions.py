"""
Pure Function Brains - Stateless brain implementations.

All brains are pure functions: Input → Output (no state access).
This enables multi-user safety, testability, and parallel execution.

Architecture Principle:
"If every brain is a PURE FUNCTION (input → output),
we DON'T need shared state."
"""

from typing import Protocol, runtime_checkable, Any, Literal

# Import interfaces from types module
# Use absolute import to avoid conflict with stdlib 'types' module
from mastermind_cli.types.interfaces import (
    BrainInput,
    Brief,
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
# BRAIN #1: PRODUCT STRATEGY
# =============================================================================


def brain_01_product_strategy(
    brain_input: BrainInput, mcp_client: MCPClient
) -> ProductStrategy:
    """
    Pure function: Product Strategy brain.

    NO self.state access. NO global variables.
    Only returns ProductStrategy output model.

    Args:
        brain_input: User's brief and context
        mcp_client: Injected MCP client (not global)

    Returns:
        ProductStrategy with positioning, audience, features, metrics
    """
    # NotebookLM notebook for Brain #1 (Software Development)
    notebook_id = "f276ccb3-0bce-4069-8b55-eae8693dbe75"

    # Construct query from brief
    brief = brain_input.brief
    query = f"""Based on the following product brief, provide a comprehensive product strategy analysis:

Brief: {brief.problem_statement}

Context: {brief.context}
Constraints: {', '.join(brief.constraints)}

Please provide:
1. Product Positioning (what makes it unique)
2. Target Audience (who is this for?)
3. Key Features (MVP scope, prioritized)
4. Success Metrics (how to measure success)
5. Risks (potential concerns)

Provide a clear, concise response."""

    # Query NotebookLM via MCP
    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)

    # Parse knowledge into structured output
    # In production, use LLM to extract structured data
    # For now, use simple parsing or mock
    return ProductStrategy(
        brief=brief,
        positioning=_extract_positioning(knowledge, brief),
        target_audience=_extract_audience(knowledge, brief),
        key_features=_extract_features(knowledge, brief),
        success_metrics=_extract_metrics(knowledge, brief),
        risks=_extract_risks(knowledge, brief),
    )


def _extract_positioning(knowledge: str, brief: Brief) -> str:
    """Extract positioning from NotebookLM response."""
    # Simple extraction - in production use LLM parsing
    return knowledge[:500] if len(knowledge) > 500 else knowledge


def _extract_audience(knowledge: str, brief: Brief) -> str:
    """Extract target audience from NotebookLM response."""
    if brief.target_audience:
        return brief.target_audience
    return "Software developers and technical teams"


def _extract_features(knowledge: str, brief: Brief) -> list[str]:
    """Extract key features from NotebookLM response."""
    # Simple parsing - in production use LLM
    return ["Core feature 1", "Core feature 2", "Core feature 3"]


def _extract_metrics(knowledge: str, brief: Brief) -> list[str]:
    """Extract success metrics from NotebookLM response."""
    return ["User adoption rate", "Feature completion rate", "User satisfaction score"]


def _extract_risks(knowledge: str, brief: Brief) -> list[str]:
    """Extract risks from NotebookLM response."""
    return ["Technical complexity", "Market competition", "Resource constraints"]


# =============================================================================
# BRAIN #2: UX RESEARCH
# =============================================================================


def brain_02_ux_research(brain_input: BrainInput, mcp_client: MCPClient) -> UXResearch:
    """
    Pure function: UX Research brain.

    Analyzes user journeys, pain points, and opportunities.

    Args:
        brain_input: User's brief and context
        mcp_client: Injected MCP client

    Returns:
        UXResearch with journeys, pain points, opportunities
    """
    notebook_id = "ux-research-notebook-id"  # TODO: Set actual notebook

    brief = brain_input.brief
    query = f"""Analyze the user experience for the following product:

Brief: {brief.problem_statement}
Target Audience: {brief.target_audience or "General users"}

Please provide:
1. User Journeys (key paths through the product)
2. Pain Points (user problems to solve)
3. Opportunities (improvement areas)
4. Research Methodology (how this analysis was done)

Provide a clear, concise response."""

    # Query NotebookLM (result not used in mock implementation)
    _ = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)

    return UXResearch(
        user_journeys=[{"step": "Journey step 1"}, {"step": "Journey step 2"}],
        pain_points=["Pain point 1", "Pain point 2"],
        opportunities=["Opportunity 1", "Opportunity 2"],
        research_methodology="NotebookLM-based analysis",
    )


# =============================================================================
# BRAIN #3: UI DESIGN
# =============================================================================


def brain_03_ui_design(brain_input: BrainInput, mcp_client: MCPClient) -> UIDesign:
    """
    Pure function: UI Design brain.

    Generates visual design system and component hierarchy.

    Args:
        brain_input: User's brief and context
        mcp_client: Injected MCP client

    Returns:
        UIDesign with visual language, color palette, component hierarchy
    """
    notebook_id = "8d544475-6860-4cd7-9037-8549325493dd"

    brief = brain_input.brief
    query = f"""Based on the following product brief, provide a comprehensive UI design system:

Brief: {brief.problem_statement}
Target Audience: {brief.target_audience or "General users"}
Context: {brief.context}

Please provide:
1. Visual Language (style, aesthetic, mood)
2. Color Palette (primary, secondary, accent, background, text)
3. Component Hierarchy (header, navigation, main content, cards, forms, etc.)
4. Design Principles (accessibility, consistency, simplicity, etc.)

Provide a clear, actionable design specification."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)

    return UIDesign(
        visual_language=knowledge[:500] if len(knowledge) > 500 else knowledge,
        color_palette={
            "primary": "#6366f1",
            "secondary": "#8b5cf6",
            "accent": "#06b6d4",
            "background": "#0f172a",
            "text": "#f8fafc",
        },
        component_hierarchy=[
            {
                "name": "Header",
                "type": "navigation",
                "children": ["Logo", "Nav", "UserMenu"],
            },
            {
                "name": "MainContent",
                "type": "layout",
                "children": ["HeroSection", "BrainGrid"],
            },
            {
                "name": "BrainCard",
                "type": "interactive",
                "children": ["Status", "Output", "Actions"],
            },
        ],
        design_principles=[
            "Accessibility first",
            "Consistent spacing",
            "Progressive disclosure",
            "Dark mode native",
        ],
    )


# =============================================================================
# BRAIN #4: FRONTEND
# =============================================================================


def brain_04_frontend(brain_input: BrainInput, mcp_client: MCPClient) -> FrontendDesign:
    """
    Pure function: Frontend brain.

    Defines technical frontend architecture and implementation.

    Args:
        brain_input: User's brief and context
        mcp_client: Injected MCP client

    Returns:
        FrontendDesign with framework, components, state management
    """
    notebook_id = "85e47142-0a65-41d9-9848-49b8b5d2db33"

    brief = brain_input.brief
    query = f"""Based on the following product brief, provide a frontend architecture specification:

Brief: {brief.problem_statement}
Context: {brief.context}
Constraints: {', '.join(brief.constraints)}

Please provide:
1. Framework choice and justification (React, Vue, Next.js, etc.)
2. Component structure (atomic design, composition patterns)
3. State management approach (Zustand, Redux, Context, etc.)
4. Styling solution (Tailwind, CSS Modules, styled-components, etc.)
5. Build tools and toolchain (Vite, Next.js, webpack, etc.)

Provide a concrete, implementation-ready specification."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)

    return FrontendDesign(
        framework=f"Next.js 16 + React 19 — {knowledge[:200] if len(knowledge) > 200 else knowledge}",
        component_hierarchy={
            "pages": ["CommandCenter", "TheNexus", "StrategyVault", "EngineRoom"],
            "layout": ["AppShell", "Sidebar", "Header"],
            "shared": ["BrainCard", "StatusBadge", "OutputPanel"],
        },
        state_management="Zustand 5 — WebSocket dispatcher as singleton store",
        styling_approach="Tailwind CSS 4 + shadcn/ui + Magic UI",
        build_tools=["Next.js 16", "TypeScript 5", "ESLint", "Prettier"],
    )


# =============================================================================
# BRAIN #5: BACKEND
# =============================================================================


def brain_05_backend(brain_input: BrainInput, mcp_client: MCPClient) -> BackendDesign:
    """
    Pure function: Backend brain.

    Defines backend architecture, API design, and data models.

    Args:
        brain_input: User's brief and context
        mcp_client: Injected MCP client

    Returns:
        BackendDesign with architecture, API design, data models
    """
    notebook_id = "c6befbbc-b7dd-4ad0-a677-314750684208"

    brief = brain_input.brief
    query = f"""Based on the following product brief, provide a backend architecture specification:

Brief: {brief.problem_statement}
Context: {brief.context}
Constraints: {', '.join(brief.constraints)}

Please provide:
1. Architecture pattern (microservices, monolith, event-driven, etc.)
2. API design approach (REST, GraphQL, WebSocket, etc.)
3. Core data models (entities, relationships, schema)
4. Authentication and authorization strategy
5. Performance and scalability considerations

Provide a concrete, implementation-ready specification."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)

    return BackendDesign(
        architecture=f"FastAPI + Python 3.14 — {knowledge[:200] if len(knowledge) > 200 else knowledge}",
        api_design="REST + WebSocket (real-time brain execution events)",
        data_models=[
            {
                "name": "Execution",
                "fields": ["id", "brief", "status", "brain_outputs", "created_at"],
            },
            {
                "name": "BrainOutput",
                "fields": ["brain_id", "content", "confidence", "execution_id"],
            },
            {
                "name": "APIKey",
                "fields": ["id", "key_hash", "user_id", "created_at", "last_used"],
            },
        ],
        authentication="JWT (30min) + refresh rotation (24h) + API Keys (mmsk_ prefix)",
    )


# =============================================================================
# BRAIN #6: QA/DEVOPS
# =============================================================================


def brain_06_qa_devops(brain_input: BrainInput, mcp_client: MCPClient) -> QADevOpsPlan:
    """
    Pure function: QA/DevOps brain.

    Defines testing strategy and deployment pipeline.

    Args:
        brain_input: User's brief and context
        mcp_client: Injected MCP client

    Returns:
        QADevOpsPlan with testing strategy, CI/CD, monitoring, deployment
    """
    notebook_id = "74cd3a81-1350-4927-af14-c0c4fca41a8e"

    brief = brain_input.brief
    query = f"""Based on the following product brief, provide a QA and DevOps strategy:

Brief: {brief.problem_statement}
Context: {brief.context}

Please provide:
1. Testing strategy (unit, integration, E2E, coverage targets)
2. CI/CD pipeline (stages, tools, automation)
3. Monitoring and logging (observability, alerting)
4. Deployment strategy (Docker, cloud, zero-downtime)

Provide a concrete, implementation-ready specification."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)

    return QADevOpsPlan(
        testing_strategy=f"pytest (unit/integration) + Playwright (E2E) — {knowledge[:200] if len(knowledge) > 200 else knowledge}",
        ci_cd_pipeline="GitHub Actions: typecheck → pytest → semantic regression (3-tier)",
        monitoring="Structured logging (JSON) + health endpoints + Docker metrics",
        deployment_strategy="Multi-stage Docker build → docker compose up -d (api:8000, web:3000)",
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

    Args:
        brain_input: User's brief and context
        mcp_client: Injected MCP client
        previous_outputs: Dict of {brain_id: output} to evaluate

    Returns:
        GrowthDataEvaluation with verdict, score, feedback
    """
    notebook_id = "evaluator-notebook-id"  # TODO: Set actual notebook

    # Build evaluation context from previous outputs
    context = "\n".join(
        [
            f"{brain_id}: {output}"
            for brain_id, output in (previous_outputs or {}).items()
        ]
    )

    query = f"""Evaluate the following product strategy outputs:

{context}

Original Brief: {brain_input.brief.problem_statement}

Please provide:
1. Verdict (APPROVE, CONDITIONAL, REJECT, ESCALATE)
2. Score (0-10)
3. Detailed feedback
4. Approval conditions (if CONDITIONAL)
5. Rejection reasons (if REJECT)

Provide a clear, concise evaluation."""

    knowledge = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)

    return GrowthDataEvaluation(
        verdict=_extract_verdict(knowledge),
        score=_extract_score(knowledge),
        feedback=knowledge[:1000],
        approval_conditions=[],
        rejection_reasons=[],
    )


def _extract_verdict(
    knowledge: str,
) -> Literal["APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"]:
    """Extract verdict from evaluation."""
    knowledge_upper = knowledge.upper()
    if "APPROVE" in knowledge_upper and "CONDITIONAL" not in knowledge_upper:
        return "APPROVE"
    elif "REJECT" in knowledge_upper or "ESCALATE" in knowledge_upper:
        return "REJECT" if "REJECT" in knowledge_upper else "ESCALATE"
    else:
        return "CONDITIONAL"


def _extract_score(knowledge: str) -> float:
    """Extract score from evaluation."""
    # Simple parsing - look for number in 0-10 range
    import re

    scores = re.findall(r"\b([0-9]|10)\b", knowledge)
    if scores:
        return float(scores[0])
    return 7.0  # Default score


# =============================================================================
# BRAIN #8: MASTER INTERVIEWER (DISCOVERY)
# =============================================================================


def brain_08_master_interviewer(
    brain_input: BrainInput, mcp_client: MCPClient
) -> MasterInterviewerOutput:
    """
    Pure function: Master Interviewer brain (Discovery).

    Detects ambiguity in brief and generates interview plan.

    Args:
        brain_input: User's brief and context
        mcp_client: Injected MCP client

    Returns:
        MasterInterviewerOutput with ambiguity detection and interview plan
    """
    notebook_id = "5330e845-29dc-4219-9d7e-c1ccb4851bb3"  # Brain #8 notebook

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
        or (brief.problem_statement.count("?") >= 2)
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

    # Generate interview plan via NotebookLM
    query = f"""The following user brief is ambiguous. Generate 3-5 clarifying questions:

Brief: {brief.problem_statement}
Context: {brief.context}

Generate questions to clarify:
1. Problem definition (what exactly are we solving?)
2. Target audience (who is this for?)
3. Success criteria (how will we know it works?)

Provide questions in a clear, numbered format."""

    # Query NotebookLM (result not used in mock implementation)
    _ = mcp_client.query_notebooklm(notebook_id=notebook_id, query=query)

    interview_plan = [
        {"question": f"Question {i+1}", "context": "Clarification needed"}
        for i in range(5)
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
