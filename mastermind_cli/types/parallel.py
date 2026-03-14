"""
Parallel execution types for flow configuration and task state.

This module defines Pydantic models for:
- TaskState: Enum for brain execution states
- ProviderConfig: Rate limiting configuration per API provider
- FlowConfig: DAG-based flow configuration with cycle detection
- ExecutionGraph: Wave structure for parallel execution scheduling
"""

from enum import Enum
from typing import Dict, List, Optional
from collections import deque
from pydantic import BaseModel, Field, model_validator


class TaskState(str, Enum):
    """Execution state of a brain task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    KILLED = "killed"


class ProviderConfig(BaseModel):
    """Rate limiting configuration for an API provider.

    Attributes:
        name: Provider identifier (e.g., "notebooklm", "claude")
        max_concurrent_calls: Maximum concurrent API calls (1-100)
        retry_attempts: Number of retry attempts on failure (0-10)
        backoff_base: Base for exponential backoff in seconds (0.1-60.0)
    """

    name: str = Field(..., description="Provider identifier")
    max_concurrent_calls: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum concurrent API calls"
    )
    retry_attempts: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Number of retry attempts on failure"
    )
    backoff_base: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Base for exponential backoff in seconds"
    )


class FlowConfig(BaseModel):
    """DAG-based flow configuration with cycle detection.

    This model validates that the flow graph is a valid Directed Acyclic Graph (DAG)
    using Kahn's algorithm for cycle detection. It provides topological sorting for
    execution order.

    Attributes:
        flow_id: Unique identifier for this flow
        nodes: Dictionary mapping brain_id to list of dependency brain_ids
        description: Optional description of the flow

    Example:
        >>> flow = FlowConfig(
        ...     flow_id="example-flow",
        ...     nodes={
        ...         "brain-01": [],
        ...         "brain-02": ["brain-01"],
        ...         "brain-03": ["brain-01", "brain-02"]
        ...     }
        ... )
        >>> order = flow.get_execution_order()
        >>> assert order.index("brain-01") < order.index("brain-02")
    """

    flow_id: str = Field(..., description="Unique flow identifier")
    nodes: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Brain ID to dependency list mapping"
    )
    description: str = Field(default="", description="Flow description")

    # Cache for topological sort result
    _execution_order: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_dag(self) -> "FlowConfig":
        """Validate that the graph is acyclic using Kahn's algorithm.

        Raises:
            ValueError: If a cycle is detected or dependencies reference missing nodes

        Returns:
            Self if validation passes
        """
        # Build adjacency list and in-degree count
        in_degree: Dict[str, int] = {node: 0 for node in self.nodes}
        adjacency: Dict[str, List[str]] = {node: [] for node in self.nodes}

        for node, dependencies in self.nodes.items():
            for dep in dependencies:
                # Validate dependency exists
                if dep not in self.nodes:
                    raise ValueError(
                        f"Dependency '{dep}' for node '{node}' does not exist in flow. "
                        f"Available nodes: {list(self.nodes.keys())}"
                    )

                # Build adjacency list
                adjacency[dep].append(node)

                # Increment in-degree
                in_degree[node] += 1

        # Kahn's algorithm: start with nodes that have zero in-degree
        queue: deque[str] = deque([node for node, degree in in_degree.items() if degree == 0])
        processed: List[str] = []

        while queue:
            current = queue.popleft()
            processed.append(current)

            # Reduce in-degree for neighbors
            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If not all nodes processed, there's a cycle
        if len(processed) != len(self.nodes):
            # Find nodes in the cycle
            unprocessed = [node for node in self.nodes if node not in processed]
            raise ValueError(
                f"Cyclic dependency detected in flow '{self.flow_id}'. "
                f"Nodes involved in cycle: {unprocessed}. "
                f"Total nodes: {len(self.nodes)}, processed: {len(processed)}."
            )

        return self

    def get_execution_order(self) -> List[str]:
        """Return topological sort of brain IDs for execution order.

        This method caches the result to avoid recomputing the sort on multiple calls.
        Uses Kahn's algorithm to produce a valid topological ordering.

        Returns:
            List of brain IDs in topological order (dependencies before dependents)
        """
        # Return cached result if available
        if self._execution_order is not None:
            return self._execution_order

        # Build adjacency list and in-degree count
        in_degree: Dict[str, int] = {node: 0 for node in self.nodes}
        adjacency: Dict[str, List[str]] = {node: [] for node in self.nodes}

        for node, dependencies in self.nodes.items():
            for dep in dependencies:
                adjacency[dep].append(node)
                in_degree[node] += 1

        # Kahn's algorithm
        queue: deque[str] = deque([node for node, degree in in_degree.items() if degree == 0])
        result: List[str] = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in adjacency[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Cache and return
        self._execution_order = result
        return result


class ExecutionLevel(BaseModel):
    """A single wave/level in the execution graph.

    Brains in the same level have no dependencies on each other and can run in parallel.

    Attributes:
        wave_number: Zero-based wave number (0 = first wave)
        brain_ids: List of brain IDs that can execute in this wave
    """

    wave_number: int = Field(..., ge=0, description="Wave number (0-indexed)")
    brain_ids: List[str] = Field(
        default_factory=list,
        description="Brain IDs that can execute in this wave"
    )


class ExecutionGraph(BaseModel):
    """Wave structure for parallel execution scheduling.

    This graph groups brains into waves where each wave contains independent brains
    that can execute concurrently. Brains in wave N only depend on brains in waves 0..N-1.

    Attributes:
        levels: List of execution waves in order
        total_brains: Total number of brains in the flow
        max_parallelism: Maximum number of brains running concurrently (largest wave size)
    """

    levels: List[ExecutionLevel] = Field(
        default_factory=list,
        description="Execution waves in order"
    )
    total_brains: int = Field(..., ge=0, description="Total brains in flow")
    max_parallelism: int = Field(..., ge=0, description="Maximum concurrent brains")
