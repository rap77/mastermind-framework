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


class TestBrainNormalization:
    """Test brain output models and normalizer."""

    def test_standard_schema_validates_brain_id_content_version(self):
        """Test that StandardSchema validates brain_id, content, version."""
        from mastermind_cli.types import StandardSchema

        schema = StandardSchema(
            brain_id="brain-1",
            content="Strategy output",
            version="v2.0.0"
        )
        assert schema.brain_id == "brain-1"
        assert schema.content == "Strategy output"
        assert schema.version == "v2.0.0"

    def test_standard_schema_accepts_optional_raw_fallback_field(self):
        """Test that StandardSchema accepts optional raw_fallback field."""
        from mastermind_cli.types import StandardSchema

        schema = StandardSchema(
            brain_id="brain-1",
            content="Output",
            raw_fallback="Original unparseable text"
        )
        assert schema.raw_fallback == "Original unparseable text"

    def test_normalize_brain_output_handles_valid_yaml(self):
        """Test that normalize_brain_output() handles valid YAML."""
        from mastermind_cli.types import normalize_brain_output

        raw_yaml = """
brain_id: "strategy-01"
content: "Product validation successful"
version: "v2.0.0"
"""
        result = normalize_brain_output(raw_yaml)
        assert result.brain_id == "strategy-01"
        assert result.content == "Product validation successful"
        assert result.version == "v2.0.0"
        assert result.raw_fallback is None

    def test_normalize_brain_output_falls_back_on_parse_error(self):
        """Test that normalize_brain_output() falls back to raw_fallback on parse error."""
        from mastermind_cli.types import normalize_brain_output

        # Invalid YAML
        raw_yaml = "this is not valid yaml: {unclosed bracket"

        result = normalize_brain_output(raw_yaml)
        assert result.brain_id == "parse_error"
        assert result.content == ""
        assert result.raw_fallback == raw_yaml

    def test_normalize_brain_output_fills_missing_fields_with_defaults(self):
        """Test that normalize_brain_output() fills missing fields with defaults."""
        from mastermind_cli.types import normalize_brain_output

        # YAML with missing fields
        raw_yaml = "content: Only content provided"

        result = normalize_brain_output(raw_yaml)
        assert result.brain_id == "unknown"  # Default
        assert result.content == "Only content provided"
        assert result.version == "v1.0.0"  # Default
        assert result.raw_fallback is None


class TestDiscriminatedUnions:
    """Test YAML config models with discriminated unions."""

    def test_brain_config_validates_based_on_type_field_discriminator(self):
        """Test that BrainConfig validates based on type field discriminator."""
        from mastermind_cli.types import BrainConfig, VectorSearchBrain, GenerativeBrain

        # Vector search brain
        vector_config = VectorSearchBrain(
            type="vector-search",
            top_k=10,
            embedding_model="text-embedding-ada-002"
        )
        assert isinstance(vector_config, VectorSearchBrain)

        # Generative brain
        generative_config = GenerativeBrain(
            type="generative",
            temperature=0.7,
            max_tokens=1000
        )
        assert isinstance(generative_config, GenerativeBrain)

    def test_vector_search_brain_requires_top_k_and_embedding_model(self):
        """Test that VectorSearchBrain requires top_k (embedding_model has default)."""
        from mastermind_cli.types import VectorSearchBrain
        from pydantic import ValidationError

        # top_k is required (no default)
        with pytest.raises(ValidationError):
            VectorSearchBrain(type="vector-search")  # Missing top_k

        # top_k must be between 1 and 100
        with pytest.raises(ValidationError):
            VectorSearchBrain(type="vector-search", top_k=0)

        with pytest.raises(ValidationError):
            VectorSearchBrain(type="vector-search", top_k=101)

        # embedding_model has default value
        config = VectorSearchBrain(type="vector-search", top_k=10)
        assert config.embedding_model == "text-embedding-ada-002"  # Default

        # Can override default
        config2 = VectorSearchBrain(type="vector-search", top_k=10, embedding_model="custom-model")
        assert config2.embedding_model == "custom-model"

    def test_generative_brain_requires_temperature_and_max_tokens(self):
        """Test that GenerativeBrain requires temperature and max_tokens."""
        from mastermind_cli.types import GenerativeBrain
        from pydantic import ValidationError

        # Missing required fields
        with pytest.raises(ValidationError):
            GenerativeBrain(type="generative", temperature=0.7)

        # temperature must be between 0.0 and 2.0
        with pytest.raises(ValidationError):
            GenerativeBrain(type="generative", temperature=-0.1, max_tokens=100)

        with pytest.raises(ValidationError):
            GenerativeBrain(type="generative", temperature=2.1, max_tokens=100)

        # max_tokens must be > 0
        with pytest.raises(ValidationError):
            GenerativeBrain(type="generative", temperature=0.7, max_tokens=0)

    def test_discriminated_union_selects_correct_model_based_on_type_field(self):
        """Test that discriminated union selects correct model based on type field."""
        from mastermind_cli.types import VectorSearchBrain, GenerativeBrain
        from pydantic import ValidationError

        # Valid vector-search config
        config1 = VectorSearchBrain.model_validate({
            "type": "vector-search",
            "top_k": 5,
            "embedding_model": "model-1"
        })
        assert config1.type == "vector-search"
        assert config1.top_k == 5

        # Valid generative config
        config2 = GenerativeBrain.model_validate({
            "type": "generative",
            "temperature": 0.8,
            "max_tokens": 500
        })
        assert config2.type == "generative"
        assert config2.temperature == 0.8

    def test_invalid_discriminator_value_raises_clear_error(self):
        """Test that invalid discriminator value raises clear error."""
        from mastermind_cli.types import VectorSearchBrain
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            VectorSearchBrain.model_validate({
                "type": "unknown-type",  # Invalid literal
                "top_k": 5
            })

        # Error should mention the invalid literal value
        error_str = str(exc_info.value)
        assert "unknown-type" in error_str


class TestCommonTypes:
    """Test common types module."""

    def test_flow_type_enum_has_all_valid_flow_types(self):
        """Test that FlowType enum has all valid flow types."""
        from mastermind_cli.types import FlowType

        assert FlowType.DISCOVERY == "discovery"
        assert FlowType.VALIDATION_ONLY == "validation_only"
        assert FlowType.FULL_PRODUCT == "full_product"

    def test_evaluation_verdict_enum_has_all_verdict_values(self):
        """Test that EvaluationVerdict enum has all verdict values."""
        from mastermind_cli.types import EvaluationVerdict

        assert EvaluationVerdict.APPROVE == "APPROVE"
        assert EvaluationVerdict.CONDITIONAL == "CONDITIONAL"
        assert EvaluationVerdict.REJECT == "REJECT"
        assert EvaluationVerdict.ESCALATE == "ESCALATE"

    def test_enums_can_be_serialized_to_strings(self):
        """Test that enums can be serialized to strings."""
        from mastermind_cli.types import FlowType, EvaluationVerdict

        # Enum values should be strings
        flow = FlowType.DISCOVERY
        assert isinstance(flow.value, str)
        assert flow == "discovery"

        verdict = EvaluationVerdict.APPROVE
        assert isinstance(verdict.value, str)
        assert verdict == "APPROVE"
