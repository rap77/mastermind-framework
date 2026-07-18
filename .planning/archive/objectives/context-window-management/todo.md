# Todo — context-window-management

<!-- topology-source: tasks.md -->

## Execution Checklist

- [x] T1: Define context budget and fit contracts
  - [x] T1.1: Add failing unit tests for layered budget validation and canonical fit outcomes
  - [x] T1.2: Add immutable context budget and segment contracts beside the existing fit evaluator
  - [x] T1.3: Validate negative limits, required output capacity and missing capability profiles
  - depends_on: None
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_context_fit.py` | `cd apps/api && uv run ruff check mastermind_cli/window_scheduler/context_fit.py tests/unit/test_context_fit.py`

- [x] T2: Implement deterministic context packing
  - [x] T2.1: Add failing packer tests for priority ordering and optional-segment omission
  - [x] T2.2: Implement a pure packager that emits selected references and compression rationale
  - [x] T2.3: Validate that core and decision-critical segments cannot be silently discarded
  - depends_on: T1
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_context_packager.py tests/unit/test_context_fit.py`

- [x] T3: Gate backend switches by context safety
  - [x] T3.1: Add failing scheduler tests for clean, compression-required and blocked candidate fits
  - [x] T3.2: Compose context-fit and packing verdicts into the existing switch decision boundary
  - [x] T3.3: Preserve checkpoint references and switch rationale for context-safe resume
  - depends_on: T2
  - validation: `cd apps/api && uv run pytest -q tests/unit/test_window_scheduler_policy.py tests/unit/test_window_scheduler_service.py`

- [x] T4: Validate context-safe continuity
  - [x] T4.1: Add an integration scenario covering fit, packing, switch gate and resume references
  - [x] T4.2: Run context-fit and scheduler regressions with ruff and mypy checks
  - [x] T4.3: Reconcile canonical status and operator handoff with the validated evidence
  - depends_on: T3
  - validation: `cd apps/api && uv run pytest -q tests/integration/test_context_safe_switch.py tests/unit/test_context_fit.py tests/unit/test_context_packager.py` | `cd apps/api && uv run ruff check mastermind_cli/window_scheduler tests/unit/test_context_fit.py tests/unit/test_context_packager.py` | `cd apps/api && uv run mypy mastermind_cli/window_scheduler` | `python3 .claude/commands/mm/discover-contract-check.py --objective context-window-management`
