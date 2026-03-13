"""
Unit tests for dependency resolver and parallel execution types.

Tests follow TDD approach: RED (failing tests) → GREEN (implementation) → REFACTOR
"""

import pytest
from pydantic import ValidationError
from mastermind_cli.types.parallel import FlowConfig, TaskState, ProviderConfig


class TestTaskState:
    """Test TaskState enum."""

    def test_task_state_values(self):
        """Test TaskState has all required values."""
        assert TaskState.PENDING.value == "pending"
        assert TaskState.RUNNING.value == "running"
        assert TaskState.COMPLETED.value == "completed"
        assert TaskState.FAILED.value == "failed"
        assert TaskState.CANCELLED.value == "cancelled"
        assert TaskState.KILLED.value == "killed"


class TestProviderConfig:
    """Test ProviderConfig model."""

    def test_provider_config_defaults(self):
        """Test ProviderConfig with default values."""
        config = ProviderConfig(name="test-provider")

        assert config.name == "test-provider"
        assert config.max_concurrent_calls == 10
        assert config.retry_attempts == 3
        assert config.backoff_base == 1.0

    def test_provider_config_custom_values(self):
        """Test ProviderConfig with custom values."""
        config = ProviderConfig(
            name="custom-provider",
            max_concurrent_calls=5,
            retry_attempts=5,
            backoff_base=2.0
        )

        assert config.name == "custom-provider"
        assert config.max_concurrent_calls == 5
        assert config.retry_attempts == 5
        assert config.backoff_base == 2.0

    def test_provider_config_validation_max_concurrent_too_low(self):
        """Test ProviderConfig rejects max_concurrent_calls < 1."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(name="test", max_concurrent_calls=0)

        assert "max_concurrent_calls" in str(exc_info.value)

    def test_provider_config_validation_max_concurrent_too_high(self):
        """Test ProviderConfig rejects max_concurrent_calls > 100."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(name="test", max_concurrent_calls=101)

        assert "max_concurrent_calls" in str(exc_info.value)

    def test_provider_config_validation_retry_attempts_negative(self):
        """Test ProviderConfig rejects negative retry_attempts."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(name="test", retry_attempts=-1)

        assert "retry_attempts" in str(exc_info.value)

    def test_provider_config_validation_retry_attempts_too_high(self):
        """Test ProviderConfig rejects retry_attempts > 10."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(name="test", retry_attempts=11)

        assert "retry_attempts" in str(exc_info.value)

    def test_provider_config_validation_backoff_base_too_low(self):
        """Test ProviderConfig rejects backoff_base < 0.1."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(name="test", backoff_base=0.05)

        assert "backoff_base" in str(exc_info.value)

    def test_provider_config_validation_backoff_base_too_high(self):
        """Test ProviderConfig rejects backoff_base > 60.0."""
        with pytest.raises(ValidationError) as exc_info:
            ProviderConfig(name="test", backoff_base=61.0)

        assert "backoff_base" in str(exc_info.value)


class TestFlowConfig:
    """Test FlowConfig model with DAG validation."""

    def test_flow_config_simple_dag(self):
        """Test FlowConfig accepts valid simple DAG."""
        flow = FlowConfig(
            flow_id="test-flow",
            nodes={
                "brain-01": [],
                "brain-02": ["brain-01"],
                "brain-03": ["brain-02"]
            }
        )

        assert flow.flow_id == "test-flow"
        assert len(flow.nodes) == 3

    def test_flow_config_parallel_branches(self):
        """Test FlowConfig accepts parallel branches."""
        flow = FlowConfig(
            flow_id="parallel-flow",
            nodes={
                "brain-01": [],
                "brain-02": [],
                "brain-03": ["brain-01"],
                "brain-04": ["brain-02"],
                "brain-05": ["brain-03", "brain-04"]
            }
        )

        assert flow.flow_id == "parallel-flow"
        assert len(flow.nodes) == 5

    def test_flow_config_empty_nodes(self):
        """Test FlowConfig accepts empty nodes dict."""
        flow = FlowConfig(flow_id="empty-flow", nodes={})

        assert flow.flow_id == "empty-flow"
        assert flow.nodes == {}

    def test_flow_config_validation_cyclic_dependency(self):
        """Test FlowConfig rejects cyclic dependencies (A→B→A)."""
        with pytest.raises(ValidationError) as exc_info:
            FlowConfig(
                flow_id="cyclic-flow",
                nodes={
                    "brain-A": ["brain-B"],
                    "brain-B": ["brain-A"]
                }
            )

        error_msg = str(exc_info.value)
        assert "cycle" in error_msg.lower() or "cyclic" in error_msg.lower()

    def test_flow_config_validation_self_cycle(self):
        """Test FlowConfig rejects self-cycle (A→A)."""
        with pytest.raises(ValidationError) as exc_info:
            FlowConfig(
                flow_id="self-cycle-flow",
                nodes={
                    "brain-A": ["brain-A"]
                }
            )

        error_msg = str(exc_info.value)
        assert "cycle" in error_msg.lower() or "cyclic" in error_msg.lower()

    def test_flow_config_validation_complex_cycle(self):
        """Test FlowConfig rejects complex cycle (A→B→C→A)."""
        with pytest.raises(ValidationError) as exc_info:
            FlowConfig(
                flow_id="complex-cycle-flow",
                nodes={
                    "brain-A": ["brain-B"],
                    "brain-B": ["brain-C"],
                    "brain-C": ["brain-A"]
                }
            )

        error_msg = str(exc_info.value)
        assert "cycle" in error_msg.lower() or "cyclic" in error_msg.lower()

    def test_flow_config_validation_missing_dependency(self):
        """Test FlowConfig rejects reference to non-existent brain."""
        with pytest.raises(ValidationError) as exc_info:
            FlowConfig(
                flow_id="missing-dep-flow",
                nodes={
                    "brain-A": ["brain-B"]  # brain-B doesn't exist
                }
            )

        error_msg = str(exc_info.value)
        assert "brain-B" in error_msg or "dependency" in error_msg.lower()

    def test_flow_config_get_execution_order_simple(self):
        """Test get_execution_order returns valid topological sort."""
        flow = FlowConfig(
            flow_id="simple-order",
            nodes={
                "brain-01": [],
                "brain-02": ["brain-01"],
                "brain-03": ["brain-02"]
            }
        )

        order = flow.get_execution_order()

        assert len(order) == 3
        assert order.index("brain-01") < order.index("brain-02")
        assert order.index("brain-02") < order.index("brain-03")

    def test_flow_config_get_execution_order_parallel(self):
        """Test get_execution_order handles parallel branches."""
        flow = FlowConfig(
            flow_id="parallel-order",
            nodes={
                "brain-01": [],
                "brain-02": [],
                "brain-03": ["brain-01", "brain-02"],
                "brain-04": ["brain-03"]
            }
        )

        order = flow.get_execution_order()

        assert len(order) == 4
        # brain-01 and brain-02 must come before brain-03
        assert order.index("brain-01") < order.index("brain-03")
        assert order.index("brain-02") < order.index("brain-03")
        # brain-03 must come before brain-04
        assert order.index("brain-03") < order.index("brain-04")

    def test_flow_config_get_execution_order_caching(self):
        """Test get_execution_order caches result."""
        flow = FlowConfig(
            flow_id="cache-test",
            nodes={
                "brain-01": [],
                "brain-02": ["brain-01"]
            }
        )

        order1 = flow.get_execution_order()
        order2 = flow.get_execution_order()

        # Should return same cached list (same object identity)
        assert order1 is order2

    def test_flow_config_description_default(self):
        """Test FlowConfig description defaults to empty string."""
        flow = FlowConfig(
            flow_id="test-flow",
            nodes={}
        )

        assert flow.description == ""

    def test_flow_config_description_custom(self):
        """Test FlowConfig accepts custom description."""
        flow = FlowConfig(
            flow_id="test-flow",
            nodes={},
            description="A test flow for validation"
        )

        assert flow.description == "A test flow for validation"


class TestFlowConfigEdgeCases:
    """Test edge cases for FlowConfig."""

    def test_flow_config_diamond_dependency(self):
        """Test FlowConfig handles diamond pattern (A→B, A→C, B→D, C→D)."""
        flow = FlowConfig(
            flow_id="diamond-flow",
            nodes={
                "brain-A": [],
                "brain-B": ["brain-A"],
                "brain-C": ["brain-A"],
                "brain-D": ["brain-B", "brain-C"]
            }
        )

        order = flow.get_execution_order()

        assert len(order) == 4
        assert order[0] == "brain-A"
        assert order.index("brain-B") < order.index("brain-D")
        assert order.index("brain-C") < order.index("brain-D")

    def test_flow_config_multiple_independent_chains(self):
        """Test FlowConfig with multiple independent chains."""
        flow = FlowConfig(
            flow_id="multi-chain-flow",
            nodes={
                "chain1-A": [],
                "chain1-B": ["chain1-A"],
                "chain2-A": [],
                "chain2-B": ["chain2-A"],
                "chain2-C": ["chain2-B"]
            }
        )

        order = flow.get_execution_order()

        assert len(order) == 5
        # Verify chain 1 order
        assert order.index("chain1-A") < order.index("chain1-B")
        # Verify chain 2 order
        assert order.index("chain2-A") < order.index("chain2-B")
        assert order.index("chain2-B") < order.index("chain2-C")


class TestDependencyResolver:
    """Test DependencyResolver service for wave building."""

    @pytest.fixture
    def mock_brain_registry(self, mocker):
        """Create mock brain registry with available brains."""
        registry = mocker.Mock()
        registry.list_brains.return_value = [
            "brain-01", "brain-02", "brain-03", "brain-04", "brain-05"
        ]
        return registry

    @pytest.mark.asyncio
    async def test_resolve_simple_linear_flow(self, mock_brain_registry):
        """Test resolving simple linear flow (A→B→C)."""
        from mastermind_cli.orchestrator.dependency_resolver import DependencyResolver

        flow = FlowConfig(
            flow_id="linear-flow",
            nodes={
                "brain-01": [],
                "brain-02": ["brain-01"],
                "brain-03": ["brain-02"]
            }
        )

        resolver = DependencyResolver(mock_brain_registry)
        graph = await resolver.resolve(flow)

        assert graph.total_brains == 3
        assert len(graph.levels) == 3  # Each brain in its own wave
        assert graph.levels[0].brain_ids == ["brain-01"]
        assert graph.levels[1].brain_ids == ["brain-02"]
        assert graph.levels[2].brain_ids == ["brain-03"]
        assert graph.max_parallelism == 1

    @pytest.mark.asyncio
    async def test_resolve_parallel_branches(self, mock_brain_registry):
        """Test resolving flow with parallel branches."""
        from mastermind_cli.orchestrator.dependency_resolver import DependencyResolver

        flow = FlowConfig(
            flow_id="parallel-flow",
            nodes={
                "brain-01": [],
                "brain-02": [],
                "brain-03": ["brain-01"],
                "brain-04": ["brain-02"],
                "brain-05": ["brain-03", "brain-04"]
            }
        )

        resolver = DependencyResolver(mock_brain_registry)
        graph = await resolver.resolve(flow)

        assert graph.total_brains == 5
        assert len(graph.levels) == 3

        # Wave 0: brain-01 and brain-02 (no deps)
        wave_0_brains = set(graph.levels[0].brain_ids)
        assert wave_0_brains == {"brain-01", "brain-02"}

        # Wave 1: brain-03 and brain-04 (depend on wave 0)
        wave_1_brains = set(graph.levels[1].brain_ids)
        assert wave_1_brains == {"brain-03", "brain-04"}

        # Wave 2: brain-05 (depends on wave 1)
        assert graph.levels[2].brain_ids == ["brain-05"]

        assert graph.max_parallelism == 2

    @pytest.mark.asyncio
    async def test_resolve_diamond_pattern(self, mock_brain_registry):
        """Test resolving diamond pattern (A→B, A→C, B→D, C→D)."""
        from mastermind_cli.orchestrator.dependency_resolver import DependencyResolver

        flow = FlowConfig(
            flow_id="diamond-flow",
            nodes={
                "brain-01": [],
                "brain-02": ["brain-01"],
                "brain-03": ["brain-01"],
                "brain-04": ["brain-02", "brain-03"]
            }
        )

        resolver = DependencyResolver(mock_brain_registry)
        graph = await resolver.resolve(flow)

        assert graph.total_brains == 4
        assert len(graph.levels) == 3

        # Wave 0: brain-01
        assert graph.levels[0].brain_ids == ["brain-01"]

        # Wave 1: brain-02 and brain-03 (both depend on brain-01)
        wave_1_brains = set(graph.levels[1].brain_ids)
        assert wave_1_brains == {"brain-02", "brain-03"}

        # Wave 2: brain-04 (depends on both wave 1 brains)
        assert graph.levels[2].brain_ids == ["brain-04"]

        assert graph.max_parallelism == 2

    @pytest.mark.asyncio
    async def test_resolve_validates_brain_existence(self, mock_brain_registry):
        """Test that resolve() validates brain IDs exist in registry."""
        from mastermind_cli.orchestrator.dependency_resolver import DependencyResolver

        flow = FlowConfig(
            flow_id="invalid-brain-flow",
            nodes={
                "brain-01": [],
                "brain-99": ["brain-01"]  # brain-99 doesn't exist
            }
        )

        resolver = DependencyResolver(mock_brain_registry)

        with pytest.raises(ValueError) as exc_info:
            await resolver.resolve(flow)

        error_msg = str(exc_info.value)
        assert "brain-99" in error_msg or "not found" in error_msg.lower()

    @pytest.mark.asyncio
    async def test_resolve_empty_flow(self, mock_brain_registry):
        """Test resolving empty flow (no brains)."""
        from mastermind_cli.orchestrator.dependency_resolver import DependencyResolver

        flow = FlowConfig(flow_id="empty-flow", nodes={})

        resolver = DependencyResolver(mock_brain_registry)
        graph = await resolver.resolve(flow)

        assert graph.total_brains == 0
        assert len(graph.levels) == 0
        assert graph.max_parallelism == 0

    @pytest.mark.asyncio
    async def test_resolve_max_parallelism_calculation(self, mock_brain_registry):
        """Test max_parallelism is calculated correctly."""
        from mastermind_cli.orchestrator.dependency_resolver import DependencyResolver

        flow = FlowConfig(
            flow_id="max-parallel-flow",
            nodes={
                "brain-01": [],
                "brain-02": [],
                "brain-03": [],
                "brain-04": ["brain-01", "brain-02", "brain-03"],
                "brain-05": ["brain-04"]
            }
        )

        resolver = DependencyResolver(mock_brain_registry)
        graph = await resolver.resolve(flow)

        # Wave 0 has 3 brains in parallel
        assert graph.max_parallelism == 3
        assert len(graph.levels[0].brain_ids) == 3


class TestExecutionGraph:
    """Test ExecutionGraph model."""

    def test_execution_graph_creation(self):
        """Test ExecutionGraph model creation."""
        from mastermind_cli.types.parallel import ExecutionLevel, ExecutionGraph

        graph = ExecutionGraph(
            levels=[
                ExecutionLevel(wave_number=0, brain_ids=["brain-01", "brain-02"]),
                ExecutionLevel(wave_number=1, brain_ids=["brain-03"])
            ],
            total_brains=3,
            max_parallelism=2
        )

        assert len(graph.levels) == 2
        assert graph.total_brains == 3
        assert graph.max_parallelism == 2
        assert graph.levels[0].wave_number == 0
        assert graph.levels[1].wave_number == 1

    def test_execution_level_defaults(self):
        """Test ExecutionLevel model with defaults."""
        from mastermind_cli.types.parallel import ExecutionLevel

        level = ExecutionLevel(wave_number=0)

        assert level.wave_number == 0
        assert level.brain_ids == []


class TestFixtures:
    """Test that fixtures load correctly."""

    def test_mock_flow_yaml_fixture(self, mock_flow_yaml):
        """Test mock_flow_yaml fixture provides valid structure."""
        assert mock_flow_yaml["flow_id"] == "test-flow"
        assert len(mock_flow_yaml["nodes"]) == 5
        assert "brain-01" in mock_flow_yaml["nodes"]
        assert "brain-02" in mock_flow_yaml["nodes"]

    def test_cyclic_flow_yaml_fixture(self, cyclic_flow_yaml):
        """Test cyclic_flow_yaml fixture has cycle."""
        assert cyclic_flow_yaml["flow_id"] == "cyclic-flow"
        assert "brain-A" in cyclic_flow_yaml["nodes"]
        assert "brain-B" in cyclic_flow_yaml["nodes"]

    def test_linear_flow_yaml_fixture(self, linear_flow_yaml):
        """Test linear_flow_yaml fixture is linear."""
        assert linear_flow_yaml["flow_id"] == "linear-flow"
        assert len(linear_flow_yaml["nodes"]) == 4

    def test_diamond_flow_yaml_fixture(self, diamond_flow_yaml):
        """Test diamond_flow_yaml fixture has diamond pattern."""
        assert diamond_flow_yaml["flow_id"] == "diamond-flow"
        assert len(diamond_flow_yaml["nodes"]) == 4

    def test_empty_flow_yaml_fixture(self, empty_flow_yaml):
        """Test empty_flow_yaml fixture has no nodes."""
        assert empty_flow_yaml["flow_id"] == "empty-flow"
        assert len(empty_flow_yaml["nodes"]) == 0

    def test_provider_configs_load(self, provider_configs):
        """Test provider_configs fixture loads from YAML."""
        assert len(provider_configs) >= 2  # At least notebooklm and claude

        # Check notebooklm exists
        notebooklm = next((p for p in provider_configs if p.name == "notebooklm"), None)
        assert notebooklm is not None
        assert notebooklm.max_concurrent_calls == 2

        # Check claude exists
        claude = next((p for p in provider_configs if p.name == "claude"), None)
        assert claude is not None
        assert claude.max_concurrent_calls == 10

    def test_notebooklm_provider_fixture(self, notebooklm_provider):
        """Test notebooklm_provider fixture has correct values."""
        assert notebooklm_provider.name == "notebooklm"
        assert notebooklm_provider.max_concurrent_calls == 2
        assert notebooklm_provider.retry_attempts == 3
        assert notebooklm_provider.backoff_base == 1.0

    def test_claude_provider_fixture(self, claude_provider):
        """Test claude_provider fixture has correct values."""
        assert claude_provider.name == "claude"
        assert claude_provider.max_concurrent_calls == 10
        assert claude_provider.retry_attempts == 3
        assert claude_provider.backoff_base == 1.0
