# Pure Function Architecture - Migration Guide

**MasterMind Framework v2.0**

This guide explains how to migrate from v1.x (stateful coordinator) to v2.0 (pure function architecture).

---

## Table of Contents

1. [What Changed](#what-changed)
2. [Why This Change](#why-this-change)
3. [Migration Steps](#migration-steps)
4. [Code Examples](#code-examples)
5. [Breaking Changes](#breaking-changes)
6. [FAQ](#faq)

---

## What Changed

### Before (v1.x) - Stateful Architecture

```python
# Global coordinator with shared state
coordinator = Coordinator(formatter=formatter, use_mcp=True)
coordinator.state["brief"] = brief
coordinator.state["results"] = {}

# Brains access shared state
class ProductStrategyBrain:
    def execute(self, brief, orchestrator):
        # ❌ Accesses shared state
        orchestrator.state["results"]["previous"] = ...
        return strategy
```

**Problems:**
- ❌ Multi-user conflicts (race conditions)
- ❌ MCP rate limiting (concurrent requests)
- ❌ Hidden dependencies (state sharing)
- ❌ Hard to test (global state)

### After (v2.0) - Pure Function Architecture

```python
# Per-request coordinator (stateless)
coordinator = StatelessCoordinator(config=config)
results = await coordinator.execute_flow(brief, brain_ids)

# Brains are pure functions
def brain_product_strategy(
    brain_input: BrainInput,
    mcp_client: MCPClient
) -> ProductStrategy:
    # ✅ No state access
    knowledge = mcp_client.query_notebooklm(...)
    return ProductStrategy(...)
```

**Benefits:**
- ✅ Multi-user safe (no shared state)
- ✅ MCP sequential (wave-based execution)
- ✅ Explicit dependencies (function parameters)
- ✅ Easy to test (pure functions)

---

## Why This Change

### Problem #1: Multi-User Race Conditions

**v1.x Code:**
```python
# Two users run flows simultaneously
user1_coordinator.orchestrate(brief1)
user2_coordinator.orchestrate(brief2)  # ❌ Overwrites user1's state!
```

**v2.0 Solution:**
```python
# Each request gets NEW coordinator instance
coordinator1 = StatelessCoordinator(config)  # Isolated
coordinator2 = StatelessCoordinator(config)  # Isolated
```

### Problem #2: MCP Rate Limiting

**v1.x Code:**
```python
# All brains execute in parallel → rate limit
async def execute_all_brains(brain_list):
    tasks = [execute_brain(b) for b in brain_list]
    await asyncio.gather(*tasks)  # ❌ 7 concurrent MCP calls!
```

**v2.0 Solution:**
```python
# Wave-based execution: sequential waves, parallel within wave
async def execute_flow(brain_ids):
    waves = resolve_dependencies(brain_ids)  # brain-1 → [brain-2, brain-3]
    for wave in waves:
        await asyncio.gather(*wave)  # ✅ Only 2-3 concurrent calls
```

---

## Migration Steps

### Step 1: Update Environment Variables

**Add API key authentication:**

```bash
# Generate API key (one-time)
mm auth create-key

# Set in environment
export MM_API_KEY="mmsk_your_api_key_here"

# Add to .bashrc/.zshrc for persistence
echo 'export MM_API_KEY="mmsk_your_api_key"' >> ~/.bashrc
```

### Step 2: Update CLI Usage

**Before (v1.x):**
```bash
mm orchestrate run --flow full_product "Build a CRM"
```

**After (v2.0):**
```bash
mm orchestrate run --brains brain-01-product-strategy,brain-02-ux-research "Build a CRM"
```

### Step 3: Update Custom Brain Code

**Before (v1.x):**
```python
class MyBrain:
    def execute(self, brief: str, orchestrator: Coordinator):
        # Access shared state
        context = orchestrator.state.get("context", {})
        results = orchestrator.state.get("results", {})

        # Store output in shared state
        orchestrator.state["results"]["my_brain"] = {"status": "done"}
        return {"output": "result"}
```

**After (v2.0):**
```python
from mastermind_cli.types.interfaces import BrainInput, MyOutput
from mastermind_cli.orchestrator.mcp_integration import MCPIntegration

def brain_my_function(
    brain_input: BrainInput,
    mcp_client: MCPIntegration
) -> MyOutput:
    # All dependencies via function parameters
    context = brain_input.additional_context.get("context", {})

    # Query MCP if needed
    knowledge = mcp_client.query_notebook(
        brain_id=1,
        query=brain_input.brief.problem_statement
    )

    # Return output model (no side effects)
    return MyOutput(
        output="result",
        generated_at=datetime.now(timezone.utc)
    )
```

### Step 4: Update Integration Code

**Before (v1.x):**
```python
from mastermind_cli.orchestrator import Coordinator

coordinator = Coordinator(formatter=formatter, use_mcp=True)
result = coordinator.orchestrate(
    brief="My brief",
    flow="full_product",
    parallel=True
)
```

**After (v2.0):**
```python
from mastermind_cli.orchestrator.stateless_coordinator import (
    StatelessCoordinator,
    CoordinatorConfig
)
from mastermind_cli.orchestrator.mcp_integration import MCPIntegration

# Create NEW coordinator per request
mcp_client = MCPIntegration(use_mcp=True)
config = CoordinatorConfig(mcp_client=mcp_client)
coordinator = StatelessCoordinator(config)

from mastermind_cli.types.interfaces import Brief
brief = Brief(problem_statement="My brief")

results = await coordinator.execute_flow(
    brief=brief,
    brain_ids=["brain-01-product-strategy", "brain-02-ux-research"]
)
```

---

## Code Examples

### Example 1: Simple Brain Execution

```python
import asyncio
from mastermind_cli.types.interfaces import Brief
from mastermind_cli.orchestrator.stateless_coordinator import (
    StatelessCoordinator,
    CoordinatorConfig
)
from mastermind_cli.orchestrator.mcp_integration import MCPIntegration

async def main():
    # Create config
    mcp_client = MCPIntegration(use_mcp=True)
    config = CoordinatorConfig(mcp_client=mcp_client)

    # Create brief
    brief = Brief(
        problem_statement="Build a CRM for small businesses",
        context="B2B SaaS, 10-50 employees",
        constraints=["Web-based", "< $10k/month"]
    )

    # Create coordinator (per-request)
    coordinator = StatelessCoordinator(config)

    # Execute flow
    results = await coordinator.execute_flow(
        brief=brief,
        brain_ids=["brain-01-product-strategy"]
    )

    # Access results
    strategy = results["brain-01-product-strategy"]
    print(f"Positioning: {strategy.positioning}")
    print(f"Target Audience: {strategy.target_audience}")

asyncio.run(main())
```

### Example 2: Multi-Brain Flow

```python
async def multi_brain_flow():
    config = CoordinatorConfig(mcp_client=MCPIntegration(use_mcp=True))
    coordinator = StatelessCoordinator(config)

    brief = Brief(problem_statement="Build a project management tool")

    # Execute multiple brains (wave-based)
    results = await coordinator.execute_flow(
        brief=brief,
        brain_ids=[
            "brain-01-product-strategy",
            "brain-02-ux-research",
            "brain-03-ui-design",
            "brain-04-frontend",
            "brain-05-backend"
        ]
    )

    # Access all results
    for brain_id, output in results.items():
        print(f"\n{brain_id}:")
        print(f"  {output.model_dump_json(indent=2)}")
```

### Example 3: Legacy Brain Wrapper

```python
from mastermind_cli.compatibility.legacy_wrapper import LegacyBrainAdapter

# Your v1.x brain (stateful)
class MyLegacyBrain:
    def execute(self, brief: str, orchestrator):
        # Old implementation
        return {"result": "value"}

# Wrap it to work as pure function
adapter = LegacyBrainAdapter(
    legacy_brain_class=MyLegacyBrain,
    output_model=MyOutputModel
)

# Use as pure function
from mastermind_cli.types.interfaces import BrainInput
brain_input = BrainInput(brief=Brief(problem_statement="Test"))
output = adapter(brain_input, mcp_client=mcp_client)
```

---

## Breaking Changes

| Change | v1.x | v2.0 |
|--------|------|------|
| **API Key** | Optional | **Required** (`MM_API_KEY`) |
| **Coordinator** | Global singleton | Per-request instance |
| **Brain signature** | `execute(self, brief, orchestrator)` | `brain_func(input, mcp_client) → Output` |
| **State access** | `orchestrator.state["key"]` | Use `BrainInput.additional_context` |
| **Result storage** | `orchestrator.state["results"]` | Return value from function |
| **Parallel flag** | `--parallel` | Automatic (wave-based) |
| **Flow flag** | `--flow full_product` | `--brains brain-01,brain-02,...` |

---

## FAQ

### Q: Do I need to rewrite all my custom brains?

**A:** No! Use the `LegacyBrainAdapter` wrapper:

```python
from mastermind_cli.compatibility.legacy_wrapper import LegacyBrainAdapter

adapter = LegacyBrainAdapter(
    legacy_brain_class=YourOldBrain,
    output_model=YourOutputModel
)
# Now works as pure function
```

### Q: Why is API key required now?

**A:** Multi-user safety requires authentication. API keys ensure:
- Each user's executions are isolated
- Rate limiting per user
- Audit trail for compliance

### Q: Can I still use `--flow` flag?

**A:** No, but you can specify brains explicitly:
```bash
# v1.x
mm orchestrate run --flow full_product "Brief"

# v2.0
mm orchestrate run --brains brain-01,brain-02,brain-03,brain-04,brain-05,brain-06,brain-07 "Brief"
```

### Q: What happened to `--parallel` flag?

**A:** Wave-based parallelism is now automatic. Brains execute:
- **Sequentially** across dependency waves
- **In parallel** within each wave

This prevents MCP rate limiting while maximizing throughput.

### Q: How do I test my brains now?

**A:** Pure functions are easier to test:

```python
def test_brain_product_strategy():
    # Arrange
    brain_input = BrainInput(
        brief=Brief(problem_statement="Test")
    )
    mock_mcp = Mock()
    mock_mcp.query_notebooklm.return_value = "Mock response"

    # Act
    output = brain_product_strategy(brain_input, mock_mcp)

    # Assert
    assert isinstance(output, ProductStrategy)
    assert output.positioning is not None
```

No need to mock coordinator state!

---

## Need Help?

- 📖 **Architecture docs:** `docs/ARCHITECTURE.md`
- 🔄 **Backward compatibility:** `docs/BACKWARD_COMPATIBILITY.md`
- 🐛 **Report issues:** GitHub Issues
- 💬 **Discussions:** GitHub Discussions

---

**Last updated:** v2.0 (2026-03-14)
