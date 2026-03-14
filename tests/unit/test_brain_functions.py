"""
Unit tests for pure function brains.

Tests verify:
1. Pure function behavior (no side effects)
2. Output model validation
3. Type safety
"""

import pytest
from mastermind_cli.types.interfaces import (
    BrainInput,
    Brief,
    ProductStrategy,
    UXResearch,
    GrowthDataEvaluation,
    MasterInterviewerOutput,
)


# =============================================================================
# MOCK MCP CLIENT
# =============================================================================

class MockMCPClient:
    """Mock MCP client for testing."""

    def __init__(self, responses: dict = None):
        """Initialize with predefined responses."""
        self.responses = responses or {}
        self.queries = []

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
        """Mock query that returns predefined response."""
        self.queries.append((notebook_id, query))
        return self.responses.get(
            notebook_id,
            f"Mock response for {notebook_id}"
        )


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def sample_brief():
    """Sample brief for testing."""
    return Brief(
        problem_statement="Build a CRM for small businesses",
        context="Need to manage customer relationships",
        constraints=["Low budget", "Quick launch"],
        target_audience="Small business owners"
    )


@pytest.fixture
def brain_input(sample_brief):
    """Sample brain input for testing."""
    return BrainInput(
        brief=sample_brief,
        additional_context={"industry": "SaaS"},
        execution_metadata={"user_id": "test-user"}
    )


@pytest.fixture
def mock_mcp():
    """Mock MCP client with sample responses."""
    return MockMCPClient({
        "f276ccb3-0bce-4069-8b55-eae8693dbe75": """
        Product Strategy Analysis:

        1. Positioning: A simple, affordable CRM designed specifically
           for small businesses that find enterprise CRMs too complex.

        2. Target Audience: Small business owners with 5-50 employees
           who need basic contact management and sales tracking.

        3. Key Features:
           - Contact management with tags
           - Simple sales pipeline
           - Email integration
           - Mobile app

        4. Success Metrics:
           - User adoption rate
           - Feature completion rate
           - Customer satisfaction

        5. Risks:
           - Competition from established CRMs
           - Limited budget for development
           - Need for quick time-to-market
        """
    })


# =============================================================================
# BRAIN #1: PRODUCT STRATEGY TESTS
# =============================================================================

def test_brain_01_is_pure_function(brain_input, mock_mcp):
    """Test that brain_01 is a pure function (no side effects)."""
    from mastermind_cli.orchestrator.brain_functions import brain_01_product_strategy

    # Call function twice with same input
    output1 = brain_01_product_strategy(brain_input, mock_mcp)
    output2 = brain_01_product_strategy(brain_input, mock_mcp)

    # Same input should produce same output (deterministic)
    assert output1.positioning == output2.positioning
    assert output1.target_audience == output2.target_audience


def test_brain_01_returns_valid_model(brain_input, mock_mcp):
    """Test that brain_01 returns valid ProductStrategy model."""
    from mastermind_cli.orchestrator.brain_functions import brain_01_product_strategy

    output = brain_01_product_strategy(brain_input, mock_mcp)

    # Verify output type
    assert isinstance(output, ProductStrategy)

    # Verify required fields
    assert output.positioning
    assert output.target_audience
    assert len(output.key_features) >= 1
    assert len(output.success_metrics) >= 1


def test_brain_01_queries_notebooklm(brain_input, mock_mcp):
    """Test that brain_01 queries NotebookLM via MCP."""
    from mastermind_cli.orchestrator.brain_functions import brain_01_product_strategy

    brain_01_product_strategy(brain_input, mock_mcp)

    # Verify MCP was called
    assert len(mock_mcp.queries) == 1
    notebook_id, query = mock_mcp.queries[0]
    assert notebook_id == "f276ccb3-0bce-4069-8b55-eae8693dbe75"
    assert "CRM" in query or "small business" in query


# =============================================================================
# BRAIN #2: UX RESEARCH TESTS
# =============================================================================

def test_brain_02_is_pure_function(brain_input, mock_mcp):
    """Test that brain_02 is a pure function."""
    from mastermind_cli.orchestrator.brain_functions import brain_02_ux_research

    output1 = brain_02_ux_research(brain_input, mock_mcp)
    output2 = brain_02_ux_research(brain_input, mock_mcp)

    assert output1.research_methodology == output2.research_methodology


def test_brain_02_returns_valid_model(brain_input, mock_mcp):
    """Test that brain_02 returns valid UXResearch model."""
    from mastermind_cli.orchestrator.brain_functions import brain_02_ux_research

    output = brain_02_ux_research(brain_input, mock_mcp)

    assert isinstance(output, UXResearch)
    assert len(output.user_journeys) >= 1
    assert len(output.pain_points) >= 1
    assert len(output.opportunities) >= 1


# =============================================================================
# BRAIN #7: GROWTH & DATA TESTS
# =============================================================================

def test_brain_07_evaluates_previous_outputs(brain_input, mock_mcp):
    """Test that brain_07 evaluates previous brain outputs."""
    from mastermind_cli.orchestrator.brain_functions import brain_07_growth_data

    previous_outputs = {
        "brain-01": ProductStrategy(
            positioning="Test positioning",
            target_audience="Test audience",
            key_features=["Feature 1"],
            success_metrics=["Metric 1"]
        )
    }

    output = brain_07_growth_data(brain_input, mock_mcp, previous_outputs)

    assert isinstance(output, GrowthDataEvaluation)
    assert output.verdict in ["APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"]
    assert 0 <= output.score <= 10


def test_brain_07_requires_previous_outputs(brain_input, mock_mcp):
    """Test that brain_07 works without previous outputs (edge case)."""
    from mastermind_cli.orchestrator.brain_functions import brain_07_growth_data

    # Should not crash with None or empty dict
    output = brain_07_growth_data(brain_input, mock_mcp, None)
    assert isinstance(output, GrowthDataEvaluation)

    output = brain_07_growth_data(brain_input, mock_mcp, {})
    assert isinstance(output, GrowthDataEvaluation)


# =============================================================================
# BRAIN #8: MASTER INTERVIEWER TESTS
# =============================================================================

def test_brain_08_detects_ambiguity():
    """Test that brain_08 detects ambiguous briefs."""
    from mastermind_cli.orchestrator.brain_functions import brain_08_master_interviewer

    # Ambiguous brief
    ambiguous_brief = Brief(
        problem_statement="Maybe something for a thing?",
        context=""
    )
    ambiguous_input = BrainInput(brief=ambiguous_brief)

    mock_mcp = MockMCPClient()
    output = brain_08_master_interviewer(ambiguous_input, mock_mcp)

    assert isinstance(output, MasterInterviewerOutput)
    assert output.is_ambiguous is True
    assert output.confidence_score < 0.5


def test_brain_08_clears_unambiguous_brief():
    """Test that brain_08 approves clear briefs."""
    from mastermind_cli.orchestrator.brain_functions import brain_08_master_interviewer

    # Clear brief
    clear_brief = Brief(
        problem_statement="Build a CRM for small businesses with contact management and sales pipeline features targeting owners of 5-50 employee companies",
        context="Need to manage customer relationships"
    )
    clear_input = BrainInput(brief=clear_brief)

    mock_mcp = MockMCPClient()
    output = brain_08_master_interviewer(clear_input, mock_mcp)

    assert isinstance(output, MasterInterviewerOutput)
    assert output.is_ambiguous is False
    assert output.confidence_score >= 0.7


# =============================================================================
# BRAIN REGISTRY TESTS
# =============================================================================

def test_brain_registry_contains_functions():
    """Test that brain registry maps IDs to functions."""
    from mastermind_cli.orchestrator.brain_functions import BRAIN_FUNCTIONS, get_brain_function

    # Verify registry has expected brains
    assert "brain-01-product-strategy" in BRAIN_FUNCTIONS
    assert "brain-02-ux-research" in BRAIN_FUNCTIONS
    assert "brain-07-growth-data" in BRAIN_FUNCTIONS
    assert "brain-08-master-interviewer" in BRAIN_FUNCTIONS


def test_get_brain_function():
    """Test that get_brain_function returns callable."""
    from mastermind_cli.orchestrator.brain_functions import get_brain_function

    func = get_brain_function("brain-01-product-strategy")
    assert callable(func)

    func = get_brain_function("non-existent")
    assert func is None


# =============================================================================
# TYPE SAFETY TESTS
# =============================================================================

def test_brain_outputs_validate_pydantic_models(brain_input, mock_mcp):
    """Test that all brain outputs are valid Pydantic models."""
    from mastermind_cli.orchestrator.brain_functions import (
        brain_01_product_strategy,
        brain_02_ux_research,
        brain_08_master_interviewer,
    )

    # Test Brain #1
    output1 = brain_01_product_strategy(brain_input, mock_mcp)
    assert output1.brain_id == "brain-01-product-strategy"
    assert output1.generated_at  # Should have timestamp

    # Test Brain #2
    output2 = brain_02_ux_research(brain_input, mock_mcp)
    assert output2.brain_id == "brain-02-ux-research"
    assert output2.generated_at

    # Test Brain #8
    output8 = brain_08_master_interviewer(brain_input, mock_mcp)
    assert output8.brain_id == "brain-08-master-interviewer"
    assert output8.generated_at


def test_brain_inputs_validate_constraints():
    """Test that BrainInput validates constraints."""
    # Should fail: problem_statement too short
    with pytest.raises(ValueError):
        Brief(problem_statement="Hi")

    # Should fail: problem_statement too short (less than 3 words)
    with pytest.raises(ValueError):
        Brief(problem_statement="Build app")

    # Should pass
    brief = Brief(problem_statement="Build a CRM app")
    assert brief.problem_statement == "Build a CRM app"
