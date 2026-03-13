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
