"""
Dependency Resolver for parallel execution scheduling.

This module implements wave-based execution planning using topological sorting.
Brains are grouped into waves where each wave contains independent brains that
can execute concurrently.
"""

from typing import Dict, List, Any

from mastermind_cli.types.parallel import FlowConfig, ExecutionGraph, ExecutionLevel


class DependencyResolver:
    """Resolves dependencies and creates execution waves for parallel execution.

    This service takes a validated FlowConfig and produces an ExecutionGraph
    that groups brains into waves. Brains in the same wave have no dependencies
    on each other and can run in parallel.

    Example:
        >>> resolver = DependencyResolver(brain_registry)
        >>> graph = await resolver.resolve(flow_config)
        >>> for level in graph.levels:
        ...     print(f"Wave {level.wave_number}: {level.brain_ids}")
    """

    def __init__(self, brain_registry: Any) -> None:
        """Initialize resolver with brain registry.

        Args:
            brain_registry: Brain registry instance with list_brains() method
        """
        self.registry = brain_registry

    async def resolve(self, flow: FlowConfig) -> ExecutionGraph:
        """Resolve flow dependencies into execution waves.

        This method:
        1. Gets topological order from the flow
        2. Groups brains into waves based on dependency depth
        3. Validates all brain IDs exist in the registry
        4. Returns an ExecutionGraph with wave structure

        Args:
            flow: Validated FlowConfig with DAG structure

        Returns:
            ExecutionGraph with waves grouped by dependency level

        Raises:
            ValueError: If a brain ID in the flow doesn't exist in the registry
        """
        # Validate all brain IDs exist in registry
        available_brains = set(self.registry.list_brains())
        flow_brains = set(flow.nodes.keys())

        unknown_brains = flow_brains - available_brains
        if unknown_brains:
            raise ValueError(
                f"Brain IDs not found in registry: {sorted(unknown_brains)}. "
                f"Available brains: {sorted(available_brains)}"
            )

        # Get topological order from flow
        execution_order = flow.get_execution_order()

        # Build wave structure
        wave_assignment: Dict[str, int] = {}  # brain_id -> wave_number
        dependency_depth: Dict[str, int] = {}  # brain_id -> max dependency depth

        for brain_id in execution_order:
            dependencies = flow.nodes.get(brain_id, [])

            if not dependencies:
                # No dependencies = wave 0
                dependency_depth[brain_id] = 0
            else:
                # Find maximum depth of dependencies
                max_dep_depth = max(
                    dependency_depth.get(dep, 0) for dep in dependencies
                )
                dependency_depth[brain_id] = max_dep_depth + 1

            # Assign to wave (0-indexed)
            wave_assignment[brain_id] = dependency_depth[brain_id]

        # Group brains by wave number
        waves: Dict[int, List[str]] = {}
        for brain_id, wave_num in wave_assignment.items():
            if wave_num not in waves:
                waves[wave_num] = []
            waves[wave_num].append(brain_id)

        # Sort waves by number and sort brain IDs within each wave
        sorted_waves = []
        for wave_num in sorted(waves.keys()):
            brain_ids = sorted(waves[wave_num])
            sorted_waves.append(
                ExecutionLevel(wave_number=wave_num, brain_ids=brain_ids)
            )

        # Calculate max parallelism (largest wave size)
        max_parallelism = max((len(wave.brain_ids) for wave in sorted_waves), default=0)

        return ExecutionGraph(
            levels=sorted_waves,
            total_brains=len(flow.nodes),
            max_parallelism=max_parallelism,
        )
