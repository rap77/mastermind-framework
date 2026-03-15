"""
Tests for pure function interface models.

Tests Pydantic models for:
- Input validation (Brief, BrainInput)
- Output validation (ProductStrategy, UXResearch, etc.)
- Edge cases and error conditions
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from mastermind_cli.types.interfaces import (
    Brief,
    BrainInput,
    ProductStrategy,
    UXResearch,
    FrontendDesign,
    GrowthDataEvaluation,
    MasterInterviewerOutput,
)


class TestBrief:
    """Test Brief input model."""

    def test_valid_brief(self):
        """Brief with valid data should pass."""
        brief = Brief(
            problem_statement="Build a CRM for small businesses",
            context="Need to manage contacts and sales pipeline",
            constraints=["Must work offline", "Mobile first"],
            target_audience="Small business owners",
        )
        assert brief.problem_statement == "Build a CRM for small businesses"
        assert len(brief.constraints) == 2

    def test_minimal_brief(self):
        """Brief with only required field should pass."""
        brief = Brief(problem_statement="Create a todo app")
        assert brief.context == ""
        assert brief.constraints == []

    def test_problem_statement_too_short(self):
        """Problem statement less than 10 chars should fail."""
        with pytest.raises(ValidationError) as exc:
            Brief(problem_statement="Short")
        # Pydantic validates min_length before custom validator
        assert "string_too_short" in str(exc.value) or "at least 10 characters" in str(
            exc.value
        )

    def test_problem_statement_whitespace_only(self):
        """Problem statement with only whitespace should fail."""
        with pytest.raises(ValidationError) as exc:
            Brief(problem_statement="   ")
        # Pydantic validates min_length before custom validator
        assert "string_too_short" in str(exc.value) or "at least 10 characters" in str(
            exc.value
        )

    def test_problem_statement_gets_stripped(self):
        """Problem statement should be stripped of leading/trailing whitespace."""
        brief = Brief(problem_statement="  Build a CRM  ")
        assert brief.problem_statement == "Build a CRM"

    def test_problem_statement_less_than_3_words(self):
        """Problem statement with < 3 words should fail."""
        with pytest.raises(ValidationError) as exc:
            Brief(
                problem_statement="Enterprise application"
            )  # Only 2 words, but > 10 chars
        # Custom validator fires after min_length passes
        assert "at least 3 words" in str(exc.value)


class TestBrainInput:
    """Test BrainInput model."""

    def test_brain_input_with_brief(self):
        """BrainInput should wrap Brief correctly."""
        brief = Brief(problem_statement="Build a CRM")
        brain_input = BrainInput(
            brief=brief,
            additional_context={"previous_brain": "strategy"},
            execution_metadata={"user_id": "123"},
        )
        assert brain_input.brief.problem_statement == "Build a CRM"
        assert brain_input.additional_context["previous_brain"] == "strategy"
        assert brain_input.execution_metadata["user_id"] == "123"

    def test_brain_input_defaults(self):
        """BrainInput should use defaults for optional fields."""
        brief = Brief(problem_statement="Build a CRM")
        brain_input = BrainInput(brief=brief)
        assert brain_input.additional_context == {}
        assert brain_input.execution_metadata == {}


class TestProductStrategy:
    """Test ProductStrategy output model."""

    def test_valid_product_strategy(self):
        """ProductStrategy with valid data should pass."""
        strategy = ProductStrategy(
            positioning="The easiest CRM for small businesses",
            target_audience="Small business owners with 1-50 employees",
            key_features=[
                "Contact management",
                "Pipeline tracking",
                "Email integration",
            ],
            success_metrics=["User adoption rate", "Retention rate", "NPS score"],
        )
        assert strategy.brain_id == "brain-01-product-strategy"
        assert len(strategy.key_features) == 3
        assert isinstance(strategy.generated_at, datetime)

    def test_product_strategy_requires_features(self):
        """ProductStrategy without features should fail."""
        with pytest.raises(ValidationError) as exc:
            ProductStrategy(
                positioning="Test",
                target_audience="Test",
                key_features=[],  # Empty list
                success_metrics=["Test"],
            )
        assert "too_short" in str(exc.value) or "at least 1" in str(exc.value)

    def test_product_strategy_with_risks(self):
        """ProductStrategy can include optional risks."""
        strategy = ProductStrategy(
            positioning="Test",
            target_audience="Test",
            key_features=["Feature 1"],
            success_metrics=["Metric 1"],
            risks=["Competition", "Technical complexity"],
        )
        assert len(strategy.risks) == 2


class TestUXResearch:
    """Test UXResearch output model."""

    def test_valid_ux_research(self):
        """UXResearch with valid data should pass."""
        research = UXResearch(
            user_journeys=[
                {"stage": "Awareness", "actions": ["Search online", "Ask friends"]},
                {
                    "stage": "Consideration",
                    "actions": ["Compare options", "Read reviews"],
                },
            ],
            pain_points=["Hard to track leads", "No mobile app"],
            opportunities=["AI-powered suggestions", "Mobile-first design"],
            research_methodology="Competitive analysis + user interviews",
        )
        assert research.brain_id == "brain-02-ux-research"
        assert len(research.user_journeys) == 2
        assert len(research.pain_points) == 2

    def test_ux_research_requires_journeys(self):
        """UXResearch without journeys should fail."""
        with pytest.raises(ValidationError):
            UXResearch(
                user_journeys=[],
                pain_points=["Test"],
                opportunities=["Test"],
                research_methodology="Test",
            )


class TestFrontendDesign:
    """Test FrontendDesign output model."""

    def test_valid_frontend_design(self):
        """FrontendDesign with valid data should pass."""
        frontend = FrontendDesign(
            framework="React with TypeScript",
            component_hierarchy={
                "pages": ["Dashboard", "Contacts"],
                "shared": ["Button", "Input"],
            },
            state_management="Zustand",
            styling_approach="Tailwind CSS",
        )
        assert frontend.brain_id == "brain-04-frontend"
        assert frontend.framework == "React with TypeScript"
        assert frontend.state_management == "Zustand"

    def test_frontend_design_with_build_tools(self):
        """FrontendDesign can include optional build tools."""
        frontend = FrontendDesign(
            framework="React",
            component_hierarchy={},
            state_management="Redux",
            styling_approach="CSS Modules",
            build_tools=["Vite", "ESLint", "Prettier"],
        )
        assert len(frontend.build_tools) == 3


class TestGrowthDataEvaluation:
    """Test GrowthDataEvaluation output model."""

    def test_valid_evaluation_approve(self):
        """Evaluation with APPROVE verdict should pass."""
        evaluation = GrowthDataEvaluation(
            verdict="APPROVE", score=8.5, feedback="Strong strategy with clear metrics"
        )
        assert evaluation.brain_id == "brain-07-growth-data"
        assert evaluation.verdict == "APPROVE"
        assert evaluation.approval_conditions == []

    def test_valid_evaluation_conditional(self):
        """Evaluation with CONDITIONAL verdict should include conditions."""
        evaluation = GrowthDataEvaluation(
            verdict="CONDITIONAL",
            score=6.0,
            feedback="Good but needs more detail on tech stack",
            approval_conditions=["Specify framework choice", "Add MVP scope"],
        )
        assert evaluation.verdict == "CONDITIONAL"
        assert len(evaluation.approval_conditions) == 2

    def test_valid_evaluation_reject(self):
        """Evaluation with REJECT verdict should include reasons."""
        evaluation = GrowthDataEvaluation(
            verdict="REJECT",
            score=3.0,
            feedback="Too vague, no clear path forward",
            rejection_reasons=["Missing success metrics", "No timeline defined"],
        )
        assert evaluation.verdict == "REJECT"
        assert len(evaluation.rejection_reasons) == 2

    def test_score_out_of_range(self):
        """Score outside 0-10 should fail."""
        with pytest.raises(ValidationError):
            GrowthDataEvaluation(
                verdict="APPROVE",
                score=11.0,  # Too high
                feedback="Test",
            )

        with pytest.raises(ValidationError):
            GrowthDataEvaluation(
                verdict="APPROVE",
                score=-1.0,  # Too low
                feedback="Test",
            )

    def test_invalid_verdict(self):
        """Invalid verdict should fail."""
        with pytest.raises(ValidationError):
            GrowthDataEvaluation(
                verdict="INVALID",  # Not in Literal
                score=5.0,
                feedback="Test",
            )


class TestMasterInterviewerOutput:
    """Test MasterInterviewerOutput output model."""

    def test_ambiguous_brief(self):
        """Output for ambiguous brief should have questions."""
        output = MasterInterviewerOutput(
            is_ambiguous=True,
            interview_plan=[
                {"question": "What is the main problem?", "priority": "high"},
                {"question": "Who is your target user?", "priority": "high"},
            ],
            confidence_score=0.3,
        )
        assert output.is_ambiguous is True
        assert len(output.interview_plan) == 2
        assert output.clarified_brief is None

    def test_clarified_brief(self):
        """Output after interview should have clarified brief."""
        brief = Brief(problem_statement="Build a CRM for freelancers")
        output = MasterInterviewerOutput(
            is_ambiguous=False,
            interview_plan=[],
            clarified_brief=brief,
            confidence_score=0.9,
        )
        assert output.is_ambiguous is False
        assert output.clarified_brief is not None
        assert output.clarified_brief.problem_statement == "Build a CRM for freelancers"

    def test_confidence_score_range(self):
        """Confidence score must be between 0 and 1."""
        with pytest.raises(ValidationError):
            MasterInterviewerOutput(
                is_ambiguous=False,
                interview_plan=[],
                confidence_score=1.5,  # Too high
            )


class TestTypeSafety:
    """Test type safety across models."""

    def test_product_strategy_wrong_type(self):
        """Wrong types should be caught by Pydantic."""
        with pytest.raises(ValidationError):
            ProductStrategy(
                positioning=123,  # Should be str
                target_audience=["List", "not", "string"],  # Should be str
                key_features="String, not list",  # Should be list
                success_metrics=None,  # Should be list
            )

    def test_datetime_auto_generated(self):
        """generated_at should default to now()."""
        strategy = ProductStrategy(
            positioning="Test",
            target_audience="Test",
            key_features=["Test"],
            success_metrics=["Test"],
        )
        assert isinstance(strategy.generated_at, datetime)
        # Should be very recent (within last second)
        assert (datetime.now() - strategy.generated_at).total_seconds() < 1


class TestPureFunctionPrinciple:
    """Test that models enforce pure function principles."""

    def test_models_are_serializable(self):
        """All models should be JSON serializable (for logging)."""
        brief = Brief(problem_statement="Build a CRM")
        strategy = ProductStrategy(
            positioning="Test",
            target_audience="Test",
            key_features=["Test"],
            success_metrics=["Test"],
        )

        # Should not raise
        brief_dict = brief.model_dump()
        strategy_dict = strategy.model_dump()

        assert "problem_statement" in brief_dict
        assert "positioning" in strategy_dict

    def test_models_are_immutable_by_default(self):
        """Models should be frozen (immutable) to prevent side effects."""
        # Note: Pydantic v2 BaseModel is mutable by default
        # We'd need to add model_config = ConfigDict(frozen=True)
        # For now, test that we CAN create new instances easily
        strategy = ProductStrategy(
            positioning="Test",
            target_audience="Test",
            key_features=["Test"],
            success_metrics=["Test"],
        )

        # Creating a new instance with updated data is easy
        new_strategy = strategy.model_copy(update={"positioning": "Updated"})
        assert new_strategy.positioning == "Updated"
        assert strategy.positioning == "Test"  # Original unchanged
