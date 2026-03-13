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
