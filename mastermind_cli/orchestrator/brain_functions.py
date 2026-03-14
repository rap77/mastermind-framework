"""
Pure Function Brains - Stateless brain implementations.

All brains are pure functions: Input → Output (no state access).
This enables multi-user safety, testability, and parallel execution.

Architecture Principle:
"If every brain is a PURE FUNCTION (input → output),
we DON'T need shared state."
"""

from typing import Protocol, runtime_checkable

# Import interfaces from types module
# Use absolute import to avoid conflict with stdlib 'types' module
from mastermind_cli.types.interfaces import (
    BrainInput,
    Brief,
    ProductStrategy,
    UXResearch,
    GrowthDataEvaluation,
    MasterInterviewerOutput,
)


# =============================================================================
# MCP CLIENT PROTOCOL
# =============================================================================

@runtime_checkable
class MCPClient(Protocol):
    """MCP client protocol for type hints."""

    def query_notebooklm(
        self,
        notebook_id: str,
        query: str
    ) -> str:
        """Query NotebookLM via MCP."""
        ...


# =============================================================================
# BRAIN #1: PRODUCT STRATEGY
# =============================================================================

def brain_01_product_strategy(
    brain_input: BrainInput,
    mcp_client: MCPClient
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
    knowledge = mcp_client.query_notebooklm(
        notebook_id=notebook_id,
        query=query
    )

    # Parse knowledge into structured output
    # In production, use LLM to extract structured data
    # For now, use simple parsing or mock
    return ProductStrategy(
        positioning=_extract_positioning(knowledge, brief),
        target_audience=_extract_audience(knowledge, brief),
        key_features=_extract_features(knowledge, brief),
        success_metrics=_extract_metrics(knowledge, brief),
        risks=_extract_risks(knowledge, brief)
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
    return [
        "Core feature 1",
        "Core feature 2",
        "Core feature 3"
    ]


def _extract_metrics(knowledge: str, brief: Brief) -> list[str]:
    """Extract success metrics from NotebookLM response."""
    return [
        "User adoption rate",
        "Feature completion rate",
        "User satisfaction score"
    ]


def _extract_risks(knowledge: str, brief: Brief) -> list[str]:
    """Extract risks from NotebookLM response."""
    return [
        "Technical complexity",
        "Market competition",
        "Resource constraints"
    ]


# =============================================================================
# BRAIN #2: UX RESEARCH
# =============================================================================

def brain_02_ux_research(
    brain_input: BrainInput,
    mcp_client: MCPClient
) -> UXResearch:
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

    knowledge = mcp_client.query_notebooklm(
        notebook_id=notebook_id,
        query=query
    )

    return UXResearch(
        user_journeys=[{"step": "Journey step 1"}, {"step": "Journey step 2"}],
        pain_points=["Pain point 1", "Pain point 2"],
        opportunities=["Opportunity 1", "Opportunity 2"],
        research_methodology="NotebookLM-based analysis"
    )


# =============================================================================
# BRAIN #7: GROWTH & DATA (EVALUATOR)
# =============================================================================

def brain_07_growth_data(
    brain_input: BrainInput,
    mcp_client: MCPClient,
    previous_outputs: dict | None = None
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
    context = "\n".join([
        f"{brain_id}: {output}"
        for brain_id, output in (previous_outputs or {}).items()
    ])

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

    knowledge = mcp_client.query_notebooklm(
        notebook_id=notebook_id,
        query=query
    )

    return GrowthDataEvaluation(
        verdict=_extract_verdict(knowledge),
        score=_extract_score(knowledge),
        feedback=knowledge[:1000],
        approval_conditions=[],
        rejection_reasons=[]
    )


def _extract_verdict(knowledge: str) -> str:
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
    scores = re.findall(r'\b([0-9]|10)\b', knowledge)
    if scores:
        return float(scores[0])
    return 7.0  # Default score


# =============================================================================
# BRAIN #8: MASTER INTERVIEWER (DISCOVERY)
# =============================================================================

def brain_08_master_interviewer(
    brain_input: BrainInput,
    mcp_client: MCPClient
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
    missing_problem = "?" in brief.problem_statement or "how do" in brief.problem_statement.lower()

    is_ambiguous = (
        word_count < 15 or
        (brief.problem_statement.count("?") >= 2) or
        has_ambiguity_markers or
        missing_problem
    )

    if not is_ambiguous:
        return MasterInterviewerOutput(
            is_ambiguous=False,
            interview_plan=[],
            clarified_brief=brief,
            confidence_score=0.9
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

    knowledge = mcp_client.query_notebooklm(
        notebook_id=notebook_id,
        query=query
    )

    interview_plan = [
        {"question": f"Question {i+1}", "context": "Clarification needed"}
        for i in range(5)
    ]

    return MasterInterviewerOutput(
        is_ambiguous=True,
        interview_plan=interview_plan,
        clarified_brief=None,
        confidence_score=0.3
    )


# =============================================================================
# BRAIN REGISTRY - Maps brain IDs to pure functions
# =============================================================================

BRAIN_FUNCTIONS = {
    "brain-01-product-strategy": brain_01_product_strategy,
    "brain-02-ux-research": brain_02_ux_research,
    "brain-07-growth-data": brain_07_growth_data,
    "brain-08-master-interviewer": brain_08_master_interviewer,
    # Add more brains as needed
}


def get_brain_function(brain_id: str):
    """Get pure function for brain ID."""
    return BRAIN_FUNCTIONS.get(brain_id)
