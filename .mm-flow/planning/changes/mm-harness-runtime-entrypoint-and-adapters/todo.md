# Todo — mm-harness-runtime-entrypoint-and-adapters

## Execution Checklist

- [x] T1: Tighten the objective package and define the CLI contract
⏱️ **Estimate**: N/A | **Actual**: 0s | **Deviation**: — | **Progress**: 3/3 (100%)
📊 **Avg/subtask**: 0s | **ETA**: done

  - [x] T1.1: Review current harness constraints, adapters, and rollout risks
  - [x] T1.2: Rewrite the package with explicit CLI/adapters/compatibility decisions and the planned `objective-context-check` gate
  - [x] T1.3: Validate the tightened package with contract-check
  - depends_on: none
  - validation: `python3 .mm-flow/commands/mm/discover-contract-check.py --objective mm-harness-runtime-entrypoint-and-adapters`
- [x] T2: Implement the neutral `mm` entrypoint
⏱️ **Estimate**: N/A | **Actual**: 0s | **Deviation**: — | **Progress**: 3/3 (100%)
📊 **Avg/subtask**: 0s | **ETA**: done
  - [x] T2.1: Create the neutral CLI entrypoint and dispatch contract
  - [x] T2.2: Wire the supported subcommands to core handlers
  - [x] T2.3: Validate help/dispatch behavior and targeted tests
  - depends_on: T1
  - validation: `python3 -m unittest tests.unit.test_mm_discover_workflow && python3 -m unittest tests.unit.test_mm_complete_task_handler_regressions && ./bin/mm --help`
- [x] T3: Align adapters and add cross-runtime smoke coverage
⏱️ **Estimate**: N/A | **Actual**: 0s | **Deviation**: — | **Progress**: 3/3 (100%)
📊 **Avg/subtask**: 0s | **ETA**: done
  - [x] T3.1: Verify Claude wrappers remain thin compatibility adapters
  - [x] T3.2: Add documentation/tests for shell-Codex-Claude usage and mention the planned `objective-context-check` step
  - [x] T3.3: Refresh handoff with the next harness objective and rerun final validation
  - depends_on: T2
  - validation: `python3 -m unittest tests.unit.test_mm_discover_workflow && python3 -m unittest tests.unit.test_mm_complete_task_handler_regressions && python3 .claude/commands/mm/complete-task-handler.py --help && ./bin/mm complete-task --help`
