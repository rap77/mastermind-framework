# Files Index - Session 2026-03-13

## Pure Function Architecture Files

### Core Interfaces
- **`mastermind_cli/types/interfaces.py`** (378 lines)
  - Brief, BrainInput, ProductStrategy, UXResearch, etc.
  - All Pydantic v2 models for type-safe brain communication

### Pure Functions
- **`mastermind_cli/orchestrator/brain_functions.py`** (340 lines)
  - `brain_01_product_strategy()` - Pure function for Product Strategy brain
  - `brain_02_ux_research()` - Pure function for UX Research brain
  - `brain_07_growth_data()` - Pure function for Growth/Data evaluator
  - `brain_08_master_interviewer()` - Pure function for Master Interviewer
  - `get_brain_function(brain_id)` - Registry lookup

### Stateless Coordinator
- **`mastermind_cli/orchestrator/stateless_coordinator.py`** (330 lines)
  - `CoordinatorConfig` - Frozen dataclass for immutable config
  - `StatelessCoordinator.execute_flow()` - Main orchestration entry point
  - Wave-based parallelism with asyncio.TaskGroup
  - Multi-user safe by design (no shared state)

### Registry Integration
- **`mastermind_cli/brain_registry.py`** (MODIFIED)
  - Added `BrainRegistry` class with `list_brains()` method
  - Maps numeric IDs to string IDs for DependencyResolver

## Tests

### Brain Functions Tests
- **`tests/unit/test_brain_functions.py`** (13 tests passing)
  - Pure function behavior validation
  - Pydantic model validation
  - MCP integration tests

### Coordinator Tests
- **`tests/unit/test_stateless_coordinator.py`** (10/13 tests passing)
  - Stateless behavior validation
  - Multi-user safety tests
  - Wave resolution tests

## Key Patterns to Reference

### Pure Function Signature
```python
def brain_XX_name(
    brain_input: BrainInput,
    mcp_client: MCPClient
) -> OutputModel:
    """
    Pure function: input → output, no state access.
    NO self.state access. NO global variables.
    """
```

### Coordinator Usage
```python
coordinator = create_stateless_coordinator(mcp_client)
results = await coordinator.execute_flow(
    brief=Brief(problem_statement="..."),
    brain_ids=["brain-01-product-strategy", "brain-02-ux-research"]
)
```
