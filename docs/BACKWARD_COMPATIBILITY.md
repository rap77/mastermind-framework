# Backward Compatibility - Legacy Brains in v2.0

**MasterMind Framework v2.0**

This guide explains how v1.x brains continue to work in v2.0 without modification.

---

## Overview

**Key Principle:** "No breaking changes for existing brains."

v2.0 introduces a **Legacy Wrapper** that allows v1.x brains to work seamlessly with the new pure function architecture.

---

## The Challenge

### v1.x Brains Were Stateful

```python
class ProductStrategyBrain:
    """v1.x brain - stateful design."""
    def __init__(self):
        self.global_state = {}  # ❌ Shared across requests

    def execute(self, brief: str, orchestrator: Coordinator):
        # Access shared orchestrator state
        orchestrator.state["results"]["previous"] = ...

        # Access global state
        self.global_state["count"] += 1

        return {"positioning": "...", "features": [...]}
```

**Problems with v1.x design:**
- ❌ Shared global state
- ❌ Access to orchestrator state
- ❌ Side effects during execution
- ❌ Not multi-user safe

### v2.0 Requires Pure Functions

```python
def brain_product_strategy(
    brain_input: BrainInput,
    mcp_client: MCPClient
) -> ProductStrategy:
    """v2.0 brain - pure function."""
    # ✅ No state access
    # ✅ No side effects
    # ✅ Input → Output only
    return ProductStrategy(...)
```

---

## The Solution: Legacy Wrapper

The `LegacyBrainAdapter` wraps v1.x brains to make them behave as pure functions.

### How It Works

```
┌─────────────────────────────────────────────────────┐
│  v2.0 Pure Function Architecture                  │
│                                                     │
│  StatelessCoordinator.execute_flow()               │
│       │                                             │
│       ▼                                             │
│  ┌──────────────────────────────────────────┐      │
│  │ LegacyBrainAdapter (Wrapper)            │      │
│  │                                          │      │
│  │ 1. Creates LOCAL orchestrator          │      │
│  │ 2. Calls v1.x brain.execute()          │      │
│  │ 3. Converts dict → Pydantic model      │      │
│  │ 4. Returns model (no side effects)     │      │
│  └──────────────────────────────────────────┘      │
│       │                                             │
│       ▼                                             │
│  v1.x Brain (isolated per request)                 │
└─────────────────────────────────────────────────────┘
```

### Key Design Decisions

**1. Local Orchestrator per Call**

Each wrapped brain gets its own isolated orchestrator:

```python
def __call__(self, brain_input: BrainInput, mcp_client: MCPClient):
    # Create LOCAL orchestrator (not shared)
    local_orchestrator = Coordinator(
        formatter=None,
        use_mcp=True,
        enable_logging=False  # Reduce overhead
    )

    # Call legacy brain with LOCAL orchestrator
    result = self.legacy_brain.execute(
        brief=brain_input.brief.problem_statement,
        orchestrator=local_orchestrator  # ISOLATED
    )

    # Return Pydantic model
    return self.output_model(**result)
```

**2. Dict → Model Conversion**

v1.x brains return dicts. v2.0 requires Pydantic models:

```python
# v1.x returns dict
{"positioning": "...", "features": [...]}

# Wrapper converts to model
ProductStrategy(
    positioning="...",
    features=[...],
    generated_at=datetime.now()
)
```

---

## Usage Examples

### Example 1: Wrapping a Single Legacy Brain

```python
from mastermind_cli.compatibility.legacy_wrapper import LegacyBrainAdapter
from mastermind_cli.types.interfaces import ProductStrategy

# Your v1.x brain
class OldProductStrategyBrain:
    def execute(self, brief: str, orchestrator):
        # Old implementation (stateful)
        orchestrator.state["phase"] = "strategy"
        return {
            "positioning": f"Strategy for: {brief}",
            "target_audience": "Small businesses",
            "key_features": ["Feature 1"],
            "success_metrics": ["Metric 1"],
            "risks": []
        }

# Wrap it
adapter = LegacyBrainAdapter(
    legacy_brain_class=OldProductStrategyBrain,
    output_model=ProductStrategy
)

# Use as pure function
from mastermind_cli.types.interfaces import BrainInput
brain_input = BrainInput(
    brief=Brief(problem_statement="Build a CRM")
)

mcp_client = MCPIntegration(use_mcp=False)
output = adapter(brain_input, mcp_client=mcp_client)

# Output is ProductStrategy model
print(output.positioning)  # "Strategy for: Build a CRM"
```

### Example 2: Registering in Brain Registry

```python
# In your brain registry or brain_functions.py
from mastermind_cli.compatibility.legacy_wrapper import LegacyBrainAdapter

# Create adapter instance
product_strategy_adapter = LegacyBrainAdapter(
    legacy_brain_class=OldProductStrategyBrain,
    output_model=ProductStrategy
)

# Register as brain function
def get_brain_function(brain_id: str):
    if brain_id == "brain-01-product-strategy":
        return product_strategy_adapter  # Returns pure function
    # ... other brains
```

### Example 3: Multiple Legacy Brains

```python
# Wrap all legacy brains
legacy_adapters = {
    "brain-01-product-strategy": LegacyBrainAdapter(
        legacy_brain_class=OldProductStrategyBrain,
        output_model=ProductStrategy
    ),
    "brain-02-ux-research": LegacyBrainAdapter(
        legacy_brain_class=OldUXResearchBrain,
        output_model=UXResearch
    ),
    "brain-03-ui-design": LegacyBrainAdapter(
        legacy_brain_class=OldUIDesignBrain,
        output_model=UIDesign
    ),
}

# Use in flow
results = await coordinator.execute_flow(
    brief=brief,
    brain_ids=list(legacy_adapters.keys())
)
```

---

## Migration Path

### Phase 1: Wrap (Immediate)

Wrap all v1.x brains with `LegacyBrainAdapter`:

```python
# Zero code changes to brains
adapters = {
    brain_id: LegacyBrainAdapter(
        legacy_brain_class=OldBrain,
        output_model=NewModel
    )
    for brain_id, OldBrain, NewModel in LEGACY_BRAINS
}
```

**Benefits:**
- ✅ Works immediately
- ✅ No brain code changes
- ✅ Pure function interface

### Phase 2: Test (Short-term)

Run integration tests with wrapped brains:

```python
@pytest.mark.asyncio
async def test_legacy_brain_in_flow():
    adapter = LegacyBrainAdapter(
        legacy_brain_class=OldProductStrategyBrain,
        output_model=ProductStrategy
    )

    coordinator = StatelessCoordinator(config)
    results = await coordinator.execute_flow(
        brief=Brief(problem_statement="Test"),
        brain_ids=["brain-01-product-strategy"]
    )

    assert "brain-01-product-strategy" in results
    assert isinstance(results["brain-01-product-strategy"], ProductStrategy)
```

### Phase 3: Migrate (Long-term)

Gradually convert v1.x brains to pure functions:

```python
# Before (v1.x wrapped)
class OldProductStrategyBrain:
    def execute(self, brief, orchestrator):
        return {...}

# After (v2.0 pure function)
def brain_product_strategy(
    brain_input: BrainInput,
    mcp_client: MCPClient
) -> ProductStrategy:
    # Pure implementation
    knowledge = mcp_client.query_notebooklm(...)
    return ProductStrategy(...)
```

---

## Limitations & Caveats

### 1. Performance Overhead

Wrapper creates local orchestrator per call (~5-10ms overhead).

**Mitigation:** For high-throughput scenarios, migrate to pure functions.

### 2. State Isolation

Wrapper creates isolated state per call. Legacy brains that rely on **persistent** global state won't work.

**Example of incompatible pattern:**
```python
class BadBrain:
    count = 0  # ❌ Class-level state (not isolated)

    def execute(self, brief, orchestrator):
        BadBrain.count += 1  # Won't work as expected
        return {"count": BadBrain.count}
```

**Fix:** Use instance state or migrate to pure function.

### 3. Orchestrator Features

Some v1.x orchestrator features may not be available:

- `orchestrator.state["plan"]` → Use `brain_input.additional_context`
- `orchestrator.iteration_count` → Pass via metadata
- `orchestrator.rejection_count` → Pass via metadata

---

## Best Practices

### ✅ DO: Use Wrapper for Immediate Compatibility

```python
adapter = LegacyBrainAdapter(
    legacy_brain_class=MyOldBrain,
    output_model=MyNewModel
)
```

### ✅ DO: Plan Migration to Pure Functions

```python
# Gradual migration
MIGRATION_PLAN = {
    "phase1": ["brain-01"],  # Migrate in Phase 1
    "phase2": ["brain-02", "brain-03"],  # Migrate in Phase 2
    "phase3": ["brain-04", "brain-05", "brain-06"]  # Migrate in Phase 3
}
```

### ❌ DON'T: Modify Legacy Brains for Wrapper

The wrapper should work without modifying legacy brain code.

### ❌ DON'T: Rely on Persistent State in Legacy Brains

Each wrapper call is isolated. Don't rely on state persisting across calls.

---

## Testing Wrapped Brains

### Unit Test

```python
def test_legacy_adapter():
    adapter = LegacyBrainAdapter(
        legacy_brain_class=OldProductStrategyBrain,
        output_model=ProductStrategy
    )

    brain_input = BrainInput(
        brief=Brief(problem_statement="Test")
    )
    mock_mcp = Mock()
    mock_mcp.query_notebooklm.return_value = "Mock"

    output = adapter(brain_input, mock_mcp)

    # Verify output is correct model type
    assert isinstance(output, ProductStrategy)
    assert output.positioning is not None
```

### Integration Test

```python
@pytest.mark.asyncio
async def test_legacy_brain_in_coordinator():
    # Register wrapped brain
    from mastermind_cli.orchestrator.brain_functions import register_brain

    adapter = LegacyBrainAdapter(
        legacy_brain_class=OldProductStrategyBrain,
        output_model=ProductStrategy
    )
    register_brain("brain-01-product-strategy", adapter)

    # Execute through coordinator
    coordinator = StatelessCoordinator(config)
    results = await coordinator.execute_flow(
        brief=Brief(problem_statement="Test"),
        brain_ids=["brain-01-product-strategy"]
    )

    # Verify it works
    assert "brain-01-product-strategy" in results
```

---

## Troubleshooting

### Issue: "AttributeError: 'Coordinator' object has no attribute 'state'"

**Cause:** Legacy brain trying to access `orchestrator.state`.

**Solution:**
1. Check wrapper is creating `Coordinator` correctly
2. Ensure legacy brain uses `orchestrator.state` dict

### Issue: "ValidationError: Field required"

**Cause:** Legacy brain returning dict missing required fields.

**Solution:** Add missing fields to legacy brain output:
```python
return {
    "positioning": "...",
    "generated_at": datetime.now()  # ✅ Add required field
}
```

### Issue: Wrapper returns wrong model type

**Cause:** Output model doesn't match dict structure.

**Solution:** Ensure output model fields match dict keys:
```python
# Legacy returns
{"positioning": "...", "features": [...]}

# Model must have same fields
class ProductStrategy(BaseModel):
    positioning: str  # ✅ Matches
    features: list    # ✅ Matches
```

---

## Need Help?

- 📖 **Migration guide:** `docs/PURE_FUNCTION_MIGRATION.md`
- 🧪 **Test examples:** `tests/integration/test_pure_function_arch.py`
- 🐛 **Report issues:** GitHub Issues

---

**Last updated:** v2.0 (2026-03-14)
