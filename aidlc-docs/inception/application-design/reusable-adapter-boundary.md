---
source_id: "reusable-adapter-boundary-v1"
brain: "brain-orchestrator-adapter"
title: "Reusable Adapter Boundary for the Unified Harness"
author: "MasterMind team"
type: "spec"
distillation_quality: "complete"
---

# Reusable Adapter Boundary — Unified Harness + Memory

## Purpose

Define the minimum surface a project must expose to be plugged into the
unified MasterMind harness + memory runtime. The boundary is intentionally
thin: another repo should be able to copy a small set of files and
configuration values without forking the harness, memory, or bridge cores.

## What is shared (do NOT copy)

The following pieces live in the shared runtime and are consumed via the
adapter; another project only references them:

- `HarnessCore` (`apps/api/mastermind_cli/orchestrator/runtime_contracts/core.py`)
- `StatelessCoordinator` (`apps/api/mastermind_cli/orchestrator/stateless_coordinator.py`)
- `MemoryRuntimeWriter` + `MemoryRuntimeAdapter` (`apps/api/mastermind_cli/orchestrator/runtime_contracts/memory_runtime_adapter.py`)
- `MemoryService` + `MemoryStore` (`apps/api/mastermind_cli/memory_layer/`)
- `HarnessRunExecutor` (`apps/api/mastermind_cli/mm_flow/harness_run_executor.py`)
- `PlanningBridge` (`apps/api/mastermind_cli/mm_flow/planning_bridge.py`)

## What is project-specific (copy / adapt)

A new project must provide:

1. **`aidlc-docs/aidlc-state.md`** with a `## Project Manifest` section
   containing at least:
   - `project_name`, `canonical_scope`
   - `source_of_truth_ai_dlc: true`, `source_of_truth_planning: true`
   - `active_objective`, `active_uow`
   - `project_root` (absolute path or `${workspaceFolder}`)
   - `operational_layer`, `design_layer`, `memory_layer`, `harness_layer`
   - Optional: `adapter_name`, `bridge_contract`

2. **`.planning/HANDOFF-CURRENT.md`** with at least:
   - `## Next recommended objective` section (operational intent)
   - `## Next command` section (next concrete action)

3. **A `ProjectAdapter` instance**, configured via `ProjectAdapter.for_repo(root)`.
   The default constructor is sufficient when the project follows the standard
   `aidlc-docs/aidlc-state.md` + `.planning/HANDOFF-CURRENT.md` layout.

4. **Environment configuration** (optional but recommended):
   - `MM_MEMORY_PROJECT_ID` for explicit memory scoping
   - `MM_MEMORY_DATABASE_URL` or `DATABASE_URL` for memory persistence
   - `MM_FLOW_ORG_ID` for RLS scoping when using MM-Flow tracking

## Minimal "Hello Adapter" Template

```python
from pathlib import Path
from mastermind_cli.mm_flow.project_adapter import ProjectAdapter
from mastermind_cli.mm_flow.harness_run_executor import HarnessRunExecutor
from mastermind_cli.types.interfaces import Brief

# 1. Bind the adapter to the repo root
adapter = ProjectAdapter.for_repo(Path("/path/to/other-project"))

# 2. Validate project-specific setup
warnings = adapter.collect_warnings()
if not warnings.passed:
    raise SystemExit(f"Adapter setup failed: {[w.message for w in warnings.errors]}")

# 3. Run the harness end-to-end
executor = HarnessRunExecutor(adapter=adapter)
run = executor.execute_harness_run(
    brief=Brief(problem_statement="..."),
    brain_ids=("brain-01-product-strategy",),
    status="in_progress",
)
print(run.project_id, run.validation.passed)
```

## Boundary Guarantees

The shared runtime guarantees:

- The adapter never mutates the harness or memory cores.
- Project-specific paths are read through the adapter, never hardcoded.
- The bridge only reads/writes the project-specific handoff file.
- Memory persistence is scoped by `project_id` derived from the adapter.
- Validation and warnings are surfaced via `validate_request` /
  `collect_warnings`; the runtime does not silently ignore them.

## Boundary Non-Goals

The adapter does NOT:

- Execute project-specific business logic.
- Define or migrate planning workflows.
- Re-encode AI-DLC specs (AI-DLC remains the design source of truth).
- Encode execution policy (recovery, verification, review are core concerns).

## Verifying the Boundary

The shared test suite (`tests/unit/test_harness_run_executor.py`) provides
a multi-project isolation smoke test that runs the executor against two
distinct `tmp_path` repos and asserts that:

- Each project gets its own `project_id`.
- Each project's `.planning/HANDOFF-CURRENT.md` is updated independently.
- Cross-project state never bleeds between adapters.

A new project should re-run that smoke test against its own `tmp_path`
fixture before adopting the adapter.
