"""
Pure Function Interfaces - Pydantic models for brain inputs/outputs.

This module defines type-safe interfaces for pure function brains.
All brains are functions: Input → Output (no state access).

Architecture Principle:
"If every brain is a PURE FUNCTION (input → output),
we DON'T need shared state."

Multi-user safe. Testable. Type-safe.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Any, Protocol, runtime_checkable
from datetime import datetime

# =============================================================================
# INPUT MODELS - What brains receive
# =============================================================================


class Brief(BaseModel):
    """
    User brief input - the problem statement.

    This is the primary input for all brains. Contains the user's request
    with optional context and constraints.
    """

    problem_statement: str = Field(
        ..., min_length=10, description="Clear description of the problem or request"
    )
    context: str = Field("", description="Additional context about the problem")
    constraints: list[str] = Field(
        default_factory=list, description="List of constraints or requirements"
    )
    target_audience: Optional[str] = Field(
        None, description="Who is this for? (optional)"
    )

    @field_validator("problem_statement")
    @classmethod
    def problem_statement_must_be_meaningful(cls, v: str) -> str:
        """Ensure problem statement is not just whitespace."""
        words = v.strip().split()
        if len(words) < 3:
            raise ValueError("Problem statement must have at least 3 words")
        return v.strip()


class BrainInput(BaseModel):
    """
    Generic brain input - all brains inherit from this.

    Pure function brains receive ONLY this as input.
    All dependencies must be passed through this interface.
    """

    brief: Brief = Field(..., description="User's brief")
    additional_context: dict[str, Any] = Field(
        default_factory=dict, description="Any additional data from previous brains"
    )
    execution_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about execution (timestamp, user, etc.)",
    )


# =============================================================================
# OUTPUT MODELS - What brains return
# =============================================================================


class ProductStrategy(BaseModel):
    """
    Brain #1 (Product Strategy) output.

    Defines positioning, audience, and success metrics.
    """

    brain_id: Literal["brain-01-product-strategy"] = "brain-01-product-strategy"
    brief: Brief | None = Field(
        None, description="Original user brief that generated this strategy"
    )
    positioning: str = Field(..., description="Product positioning statement")
    target_audience: str = Field(..., description="Who is this for?")
    key_features: list[str] = Field(
        ..., min_length=1, description="Core features of the product"
    )
    success_metrics: list[str] = Field(
        ..., min_length=1, description="How to measure success"
    )
    risks: list[str] = Field(
        default_factory=list, description="Potential risks or concerns"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now, description="When this strategy was generated"
    )


class UXResearch(BaseModel):
    """
    Brain #2 (UX Research) output.

    Contains user journeys, pain points, and opportunities.
    """

    brain_id: Literal["brain-02-ux-research"] = "brain-02-ux-research"
    user_journeys: list[dict[str, Any]] = Field(
        ..., min_length=1, description="User journey maps"
    )
    pain_points: list[str] = Field(
        ..., min_length=1, description="User problems to solve"
    )
    opportunities: list[str] = Field(
        ..., min_length=1, description="Opportunities for improvement"
    )
    research_methodology: str = Field(
        ..., description="How this research was conducted"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now, description="When this research was generated"
    )


class UIDesign(BaseModel):
    """
    Brain #3 (UI Design) output.

    Visual design system and component hierarchy.
    """

    brain_id: Literal["brain-03-ui-design"] = "brain-03-ui-design"
    visual_language: str = Field(..., description="Visual style description")
    color_palette: dict[str, str] = Field(
        ..., description="Color scheme (primary, secondary, etc.)"
    )
    component_hierarchy: list[dict[str, Any]] = Field(
        ..., min_length=1, description="UI component structure"
    )
    design_principles: list[str] = Field(
        ..., min_length=1, description="Core design principles"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now, description="When this design was generated"
    )


class FrontendDesign(BaseModel):
    """
    Brain #4 (Frontend) output.

    Technical implementation for frontend.
    """

    brain_id: Literal["brain-04-frontend"] = "brain-04-frontend"
    framework: str = Field(..., description="Frontend framework (React, Vue, etc.)")
    component_hierarchy: dict[str, Any] = Field(..., description="Component structure")
    state_management: str = Field(..., description="State management approach")
    styling_approach: str = Field(..., description="CSS/Styling solution")
    build_tools: list[str] = Field(
        default_factory=list, description="Required build tools"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now, description="When this design was generated"
    )


class BackendDesign(BaseModel):
    """
    Brain #5 (Backend) output.

    Technical implementation for backend.
    """

    brain_id: Literal["brain-05-backend"] = "brain-05-backend"
    architecture: str = Field(..., description="Backend architecture pattern")
    api_design: str = Field(..., description="API approach (REST, GraphQL, etc.)")
    data_models: list[dict[str, Any]] = Field(
        ..., min_length=1, description="Core data models"
    )
    authentication: str = Field(..., description="Auth approach")
    generated_at: datetime = Field(
        default_factory=datetime.now, description="When this design was generated"
    )


class QADevOpsPlan(BaseModel):
    """
    Brain #6 (QA/DevOps) output.

    Quality assurance and deployment strategy.
    """

    brain_id: Literal["brain-06-qa-devops"] = "brain-06-qa-devops"
    testing_strategy: str = Field(..., description="Testing approach")
    ci_cd_pipeline: str = Field(..., description="CI/CD setup")
    monitoring: str = Field(..., description="Monitoring and logging")
    deployment_strategy: str = Field(..., description="How to deploy")
    generated_at: datetime = Field(
        default_factory=datetime.now, description="When this plan was generated"
    )


class GrowthDataEvaluation(BaseModel):
    """
    Brain #7 (Growth & Data / Evaluator) output.

    Critical evaluation of all previous outputs.
    """

    brain_id: Literal["brain-07-growth-data"] = "brain-07-growth-data"
    verdict: Literal["APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"] = Field(
        ..., description="Evaluation verdict"
    )
    score: float = Field(..., ge=0.0, le=10.0, description="Quality score (0-10)")
    feedback: str = Field(..., description="Detailed feedback")
    approval_conditions: list[str] = Field(
        default_factory=list, description="Conditions for approval (if CONDITIONAL)"
    )
    rejection_reasons: list[str] = Field(
        default_factory=list, description="Reasons for rejection (if REJECT)"
    )
    evaluated_at: datetime = Field(
        default_factory=datetime.now, description="When this evaluation was made"
    )


class MasterInterviewerOutput(BaseModel):
    """
    Brain #8 (Master Interviewer / Discovery) output.

    Interview-based discovery and clarification.
    """

    brain_id: Literal["brain-08-master-interviewer"] = "brain-08-master-interviewer"
    is_ambiguous: bool = Field(..., description="Whether brief is ambiguous")
    interview_plan: list[dict[str, Any]] = Field(
        ..., description="Questions to ask user"
    )
    clarified_brief: Optional[Brief] = Field(
        None, description="Clarified brief after interview"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in understanding"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now, description="When this output was generated"
    )


# =============================================================================
# MARKETING NICHE BRAINS (M1-M16)
# =============================================================================


class MarketingStrategy(BaseModel):
    """Marketing Brain #1 - Strategy output."""

    brain_id: Literal["marketing-01-strategy"] = "marketing-01-strategy"
    brand_positioning: str = Field(..., description="Brand positioning")
    target_market: str = Field(..., description="Who we're targeting")
    unique_value_prop: str = Field(..., description="UVP")
    generated_at: datetime = Field(default_factory=datetime.now)


class BrandStrategy(BaseModel):
    """Marketing Brain #2 - Brand output."""

    brain_id: Literal["marketing-02-brand"] = "marketing-02-brand"
    brand_identity: str = Field(..., description="Brand identity")
    brand_voice: str = Field(..., description="Brand voice and tone")
    visual_guidelines: dict[str, Any] = Field(..., description="Visual guidelines")
    generated_at: datetime = Field(default_factory=datetime.now)


# Add M3-M16 similarly as needed...


# =============================================================================
# UNION TYPE - All possible brain outputs
# =============================================================================

# For type hints when you don't know which brain output you'll get
BrainOutput = (
    ProductStrategy
    | UXResearch
    | UIDesign
    | FrontendDesign
    | BackendDesign
    | QADevOpsPlan
    | GrowthDataEvaluation
    | MasterInterviewerOutput
    | MarketingStrategy
    | BrandStrategy
)


# =============================================================================
# PURE FUNCTION SIGNATURE
# =============================================================================


@runtime_checkable
class MCPClient(Protocol):
    """MCP client protocol for type hints."""

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
        """Query NotebookLM via MCP."""
        ...


def brain_function_signature(
    brain_input: BrainInput,
    mcp_client: MCPClient,
) -> BrainOutput:
    """
    Pure function signature that all brains should follow.

    Key Principles:
    1. NO self.state access
    2. NO global variables
    3. Only return output model (no side effects)
    4. All dependencies via function parameters

    This makes brains:
    - Multi-user safe (no shared state)
    - Testable (easy to mock inputs)
    - Parallelizable (no locking needed)
    - Type-safe (Pydantic validates everything)

    Returns:
        BrainOutput: One of the specialized brain output models

    Raises:
        NotImplementedError: This is a signature definition only
    """
    # Each brain implements this signature
    # with their specific input/output models
    raise NotImplementedError("Brains must implement this signature")
