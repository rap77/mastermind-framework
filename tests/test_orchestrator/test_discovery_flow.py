"""
Integration tests for Discovery Flow (Brain #8).

Tests the complete discovery flow from ambiguous brief detection through
interview conduction to final deliverable generation.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class TestDiscoveryFlow:
    """Test suite for discovery flow functionality."""

    def test_detect_flow_with_short_brief(self):
        """Test that short briefs trigger discovery flow."""
        from mastermind_cli.orchestrator.coordinator import Coordinator
        from mastermind_cli.orchestrator.output_formatter import OutputFormatter

        coordinator = Coordinator(use_mcp=False, enable_logging=False)

        # Short brief (< 15 words)
        short_brief = "quiero una app moderna"
        flow = coordinator._detect_flow(short_brief)

        assert flow == Coordinator.FLOW_DISCOVERY, f"Expected discovery flow, got {flow}"

    def test_detect_flow_with_clear_brief(self):
        """Test that clear briefs use standard flow detection."""
        from mastermind_cli.orchestrator.coordinator import Coordinator

        coordinator = Coordinator(use_mcp=False, enable_logging=False)

        # Clear, detailed brief
        clear_brief = """Necesito validar mi idea de una plataforma B2B para gestión de inventario.
El problema principal es que las PYMEs pierden track de su stock y necesito saber
si hay market fit antes de invertir en desarrollo."""

        flow = coordinator._detect_flow(clear_brief)

        # Should NOT trigger discovery (has problem statement and good length)
        assert flow == "validation_only", f"Expected validation_only, got {flow}"

    def test_detect_flow_with_ambiguity_markers(self):
        """Test that ambiguity markers trigger discovery flow."""
        from mastermind_cli.orchestrator.coordinator import Coordinator

        coordinator = Coordinator(use_mcp=False, enable_logging=False)

        # Brief with ambiguity markers
        ambiguous_brief = "quiero crear un sistema moderno y bueno"

        flow = coordinator._detect_flow(ambiguous_brief)

        assert flow == Coordinator.FLOW_DISCOVERY, f"Expected discovery flow, got {flow}"

    def test_generate_interview_plan(self):
        """Test interview plan generation."""
        from mastermind_cli.orchestrator.coordinator import Coordinator

        coordinator = Coordinator(use_mcp=False, enable_logging=False)

        brief = "quiero una app para mi negocio"

        plan = coordinator._generate_interview_plan(brief)

        assert plan is not None, "Plan should not be None"
        assert plan.get('status') == 'success', f"Plan status should be success, got {plan.get('status')}"
        assert 'plan' in plan, "Plan should have 'plan' key"

        # Check structure
        interview_strategy = plan['plan'].get('interview_strategy', {})
        assert 'categories' in interview_strategy, "Should have categories"
        assert 'initial_questions' in interview_strategy, "Should have initial questions"

    def test_conduct_interview_basic(self):
        """Test basic interview conduction."""
        from mastermind_cli.orchestrator.coordinator import Coordinator
        from unittest.mock import patch

        coordinator = Coordinator(use_mcp=False, enable_logging=False)

        # Create a mock interview plan
        mock_plan = {
            'status': 'success',
            'plan': {
                'interview_strategy': {
                    'categories': [
                        {'id': 'users', 'name': 'Users', 'target_brain': 2, 'priority': 'high'}
                    ],
                    'initial_questions': [
                        {'category': 'users', 'question': 'Who are your users?', 'target_brain': 2}
                    ],
                    'detected_gaps': [],
                    'estimated_questions': 2
                }
            }
        }

        # Mock _route_to_domain_brain to avoid MCP calls
        original_route = coordinator._route_to_domain_brain
        coordinator._route_to_domain_brain = lambda question, answer, brain_id, brief: {
            'has_follow_up': False,
            'follow_up_question': None,
            'insights': [answer],
            'gaps': [],
            'should_continue': False
        }

        try:
            # Mock input() to avoid stdin reading during test
            with patch('builtins.input', return_value='My users are small business owners'):
                interview_doc = coordinator._conduct_interview(mock_plan, "test brief")

            # Verify structure
            assert 'metadata' in interview_doc, "Should have metadata"
            assert 'qa_pairs' in interview_doc, "Should have qa_pairs"
            assert 'outcome' in interview_doc, "Should have outcome"
            assert interview_doc['outcome']['total_questions_asked'] >= 1, "Should have asked at least 1 question"

        finally:
            # Restore original method
            coordinator._route_to_domain_brain = original_route

    def test_output_formatter_discovery_methods(self):
        """Test that OutputFormatter has discovery methods."""
        from mastermind_cli.orchestrator.output_formatter import OutputFormatter

        formatter = OutputFormatter()

        # Check all discovery methods exist
        assert hasattr(formatter, 'format_separator'), "Missing format_separator"
        assert hasattr(formatter, 'format_interview_plan'), "Missing format_interview_plan"
        assert hasattr(formatter, 'format_question_to_user'), "Missing format_question_to_user"
        assert hasattr(formatter, 'format_followup_response'), "Missing format_followup_response"
        assert hasattr(formatter, 'format_interview_complete'), "Missing format_interview_complete"

        # Test they return strings
        assert isinstance(formatter.format_separator(), str)
        assert isinstance(formatter.format_question_to_user("Test?"), str)

    def test_discovery_flow_constant(self):
        """Test FLOW_DISCOVERY constant exists."""
        from mastermind_cli.orchestrator.coordinator import Coordinator

        assert hasattr(Coordinator, 'FLOW_DISCOVERY'), "Missing FLOW_DISCOVERY constant"
        assert Coordinator.FLOW_DISCOVERY == "discovery", f"FLOW_DISCOVERY should be 'discovery', got {Coordinator.FLOW_DISCOVERY}"

    def test_parse_follow_up_basic(self):
        """Test basic follow-up parsing."""
        from mastermind_cli.orchestrator.coordinator import Coordinator

        coordinator = Coordinator(use_mcp=False, enable_logging=False)

        # Test with short answer
        follow_up = coordinator._generate_basic_follow_up(
            question="What is your name?",
            answer="John"
        )

        assert follow_up is not None, "Follow-up should not be None"
        assert 'has_follow_up' in follow_up, "Should have has_follow_up key"
        assert 'insights' in follow_up, "Should have insights key"

    def test_generate_session_id(self):
        """Test session ID generation."""
        from mastermind_cli.orchestrator.coordinator import Coordinator

        coordinator = Coordinator(use_mcp=False, enable_logging=False)

        session_id = coordinator._generate_session_id()

        assert session_id is not None, "Session ID should not be None"
        assert isinstance(session_id, str), "Session ID should be string"
        assert session_id.startswith("session-"), "Session ID should start with 'session-'"


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
