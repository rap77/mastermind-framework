"""
Type definition tests for MasterMind Framework v2.0.

Tests Pydantic v2 models for all orchestration data structures.
"""
import pytest
from typing import get_type_hints


class TestModuleImports:
    """Test type module structure and imports."""

    def test_module_imports_all_exported_types_successfully(self):
        """Test that module imports all exported types successfully."""
        # This test will FAIL until __init__.py exports all types
        import mastermind_cli.types as types_module

        # Expected exports from each submodule
        expected_exports = {
            'coordinator': ['CoordinatorRequest', 'CoordinatorResponse'],
            'mcp': ['MCPRequest', 'MCPResponse'],
            'brains': ['StandardSchema', 'normalize_brain_output'],
            'config': ['BrainConfig', 'ConfigFile'],
            'common': ['FlowType', 'EvaluationVerdict']
        }

        # Check that submodule imports exist
        for submodule, exports in expected_exports.items():
            for export in exports:
                # This will fail if the export doesn't exist
                assert hasattr(types_module, export), f"Missing export: {export} from {submodule}"

    def test_module_is_importable_without_errors(self):
        """Test that module is importable without errors."""
        # This test will FAIL if there are import errors
        try:
            import mastermind_cli.types
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import mastermind_cli.types: {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error importing mastermind_cli.types: {e}")


class TestCoordinatorModels:
    """Test coordinator request and response models."""

    def test_coordinator_request_validates_required_fields(self):
        """Test that CoordinatorRequest validates required fields (brief, flow)."""
        from mastermind_cli.types import CoordinatorRequest

        # Valid request with required field
        request = CoordinatorRequest(brief="Build me a CRM app")
        assert request.brief == "Build me a CRM app"
        assert request.dry_run is False  # Default value
        assert request.max_iterations == 3  # Default value

    def test_coordinator_request_accepts_optional_fields(self):
        """Test that CoordinatorRequest accepts optional fields (dry_run, output_file, max_iterations)."""
        from mastermind_cli.types import CoordinatorRequest

        request = CoordinatorRequest(
            brief="Build me a CRM app",
            flow="discovery",
            dry_run=True,
            output_file="/tmp/output.md",
            max_iterations=5,
            use_mcp=True
        )
        assert request.flow == "discovery"
        assert request.dry_run is True
        assert request.output_file == "/tmp/output.md"
        assert request.max_iterations == 5
        assert request.use_mcp is True

    def test_coordinator_request_validates_constraints(self):
        """Test that CoordinatorRequest validates field constraints."""
        from mastermind_cli.types import CoordinatorRequest
        from pydantic import ValidationError

        # max_iterations must be between 1 and 10
        with pytest.raises(ValidationError):
            CoordinatorRequest(brief="Test", max_iterations=0)

        with pytest.raises(ValidationError):
            CoordinatorRequest(brief="Test", max_iterations=11)

        # brief must have min_length=1
        with pytest.raises(ValidationError):
            CoordinatorRequest(brief="")

    def test_coordinator_response_has_all_status_fields(self):
        """Test that CoordinatorResponse has all status fields (status, plan, results)."""
        from mastermind_cli.types import CoordinatorResponse
        from datetime import datetime

        response = CoordinatorResponse(
            status="success",
            plan={"task": "build CRM"},
            results={"brain_1": "output"},
            output="Formatted output",
            iterations=2
        )
        assert response.status == "success"
        assert response.plan is not None
        assert response.results is not None
        assert response.output is not None
        assert response.iterations == 2
        assert isinstance(response.timestamp, datetime)

    def test_coordinator_models_use_pydantic_v2_field_with_descriptions(self):
        """Test that models use Pydantic v2 Field with descriptions."""
        from mastermind_cli.types import CoordinatorRequest
        from pydantic import Field

        # Check that fields have descriptions
        request = CoordinatorRequest(brief="Test")
        field_info = CoordinatorRequest.model_fields['brief']
        assert field_info.description is not None
        assert "brief" in field_info.description.lower() or "text" in field_info.description.lower()


class TestMCPModels:
    """Test MCP request and response models."""

    def test_mcp_request_validates_brain_id_and_query(self):
        """Test that MCPRequest validates brain_id and query."""
        from mastermind_cli.types import MCPRequest

        request = MCPRequest(brain_id="brain-1", query="What is product strategy?")
        assert request.brain_id == "brain-1"
        assert request.query == "What is product strategy?"
        assert request.timeout == 30  # Default value

    def test_mcp_request_accepts_optional_context_dict(self):
        """Test that MCPRequest accepts optional context dict."""
        from mastermind_cli.types import MCPRequest

        request = MCPRequest(
            brain_id="brain-1",
            query="Test query",
            context={"project": "CRM", "user": "alice"},
            timeout=60
        )
        assert request.context is not None
        assert request.context["project"] == "CRM"
        assert request.timeout == 60

    def test_mcp_request_validates_constraints(self):
        """Test that MCPRequest validates field constraints."""
        from mastermind_cli.types import MCPRequest
        from pydantic import ValidationError

        # timeout must be between 5 and 300
        with pytest.raises(ValidationError):
            MCPRequest(brain_id="brain-1", query="Test", timeout=4)

        with pytest.raises(ValidationError):
            MCPRequest(brain_id="brain-1", query="Test", timeout=301)

        # query must have min_length=1
        with pytest.raises(ValidationError):
            MCPRequest(brain_id="brain-1", query="")

    def test_mcp_response_uses_extra_allow_for_evolutivo_approach(self):
        """Test that MCPResponse uses extra='allow' for evolutivo approach."""
        from mastermind_cli.types import MCPResponse

        # Create response with extra fields
        response = MCPResponse(
            brain_id="brain-1",
            response="Strategy output",
            success=True,
            unknown_field="preserved",  # This should be preserved
            another_unknown=42
        )

        # Extra fields should be preserved
        assert hasattr(response, 'unknown_field')
        assert response.unknown_field == "preserved"
        assert hasattr(response, 'another_unknown')
        assert response.another_unknown == 42

    def test_mcp_response_preserves_unknown_fields_from_notebooklm(self):
        """Test that MCPResponse preserves unknown fields from NotebookLM."""
        from mastermind_cli.types import MCPResponse

        # Simulate NotebookLM response with evolving schema
        raw_data = {
            "brain_id": "brain-1",
            "response": "Output",
            "success": True,
            "new_field_v2": "new value",  # Field added in NotebookLM v2
            "metadata": {"source": "notebooklm", "version": "2.0"}
        }

        response = MCPResponse(**raw_data)

        # All fields should be preserved
        assert response.new_field_v2 == "new value"
        assert response.metadata["source"] == "notebooklm"
