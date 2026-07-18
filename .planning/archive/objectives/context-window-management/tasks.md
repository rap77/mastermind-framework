# Tasks — context-window-management

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Use TDD for every runtime behavior change.
- The complete-task handler owns todo.md, HANDOFF-CURRENT.md,
  execution-state.json and task-progress.json after this package is synced.
- Do not run standalone builds.

## T1: Define context budget and fit contracts

### Execution Subtasks
- T1.1: Add failing unit tests for layered budget validation and canonical fit outcomes
- T1.2: Add immutable context budget and segment contracts beside the existing fit evaluator
- T1.3: Validate negative limits, required output capacity and missing capability profiles

### Purpose
Make context capacity a typed runtime input while preserving the existing
four-state fit contract.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/mastermind_cli/window_scheduler/context_fit.py`
- `apps/api/tests/unit/test_context_fit.py`

### Validation Commands
- `cd apps/api && uv run pytest -q tests/unit/test_context_fit.py`
- `cd apps/api && uv run ruff check mastermind_cli/window_scheduler/context_fit.py tests/unit/test_context_fit.py`

### Acceptance Criteria
- [x] Budget input distinguishes required, decision-critical, supporting and optional context.
- [x] Existing fit states retain deterministic semantics.
- [x] Invalid token estimates fail at the boundary.

## T2: Implement deterministic context packing

### Execution Subtasks
- T2.1: Add failing packer tests for priority ordering and optional-segment omission
- T2.2: Implement a pure packager that emits selected references and compression rationale
- T2.3: Validate that core and decision-critical segments cannot be silently discarded

### Purpose
Build the safe payload projection that decides what a candidate backend receives.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/mastermind_cli/window_scheduler/context_packager.py`
- `apps/api/tests/unit/test_context_packager.py`

### Validation Commands
- `cd apps/api && uv run pytest -q tests/unit/test_context_packager.py tests/unit/test_context_fit.py`

### Acceptance Criteria
- [x] Packing order is core, decisions, required artifacts, memory, optional history.
- [x] Optional segments are omitted only with explicit rationale.
- [x] Critical loss returns a blocked or compression-required result.

## T3: Gate backend switches by context safety

### Execution Subtasks
- T3.1: Add failing scheduler tests for clean, compression-required and blocked candidate fits
- T3.2: Compose context-fit and packing verdicts into the existing switch decision boundary
- T3.3: Preserve checkpoint references and switch rationale for context-safe resume

### Purpose
Prevent scheduler policy from selecting a backend that cannot safely carry the
task context.

### Depends On
T2

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/mastermind_cli/window_scheduler/service.py`
- `apps/api/mastermind_cli/window_scheduler/policy.py`
- `apps/api/tests/unit/test_window_scheduler_policy.py`
- `apps/api/tests/unit/test_window_scheduler_service.py`

### Validation Commands
- `cd apps/api && uv run pytest -q tests/unit/test_window_scheduler_policy.py tests/unit/test_window_scheduler_service.py`

### Acceptance Criteria
- [x] `unsafe_fit` and `does_not_fit` do not authorize an automatic switch.
- [x] Compression-required switches carry an explicit strategy and checkpoint reference.
- [x] Availability and risk policies remain independent inputs.

## T4: Validate context-safe continuity

### Execution Subtasks
- T4.1: Add an integration scenario covering fit, packing, switch gate and resume references
- T4.2: Run context-fit and scheduler regressions with ruff and mypy checks
- T4.3: Reconcile canonical status and operator handoff with the validated evidence

### Purpose
Prove that context management preserves continuity across a safe backend switch.

### Depends On
T3

### Parallelizable
no

### Files / Areas Likely Touched
- `apps/api/tests/integration/test_context_safe_switch.py`
- `docs/canonical/20-CONTEXT-WINDOW-MANAGEMENT-ARCHITECTURE.md`
- `.planning/changes/context-window-management/`

### Validation Commands
- `cd apps/api && uv run pytest -q tests/integration/test_context_safe_switch.py tests/unit/test_context_fit.py tests/unit/test_context_packager.py`
- `cd apps/api && uv run ruff check mastermind_cli/window_scheduler tests/unit/test_context_fit.py tests/unit/test_context_packager.py`
- `cd apps/api && uv run mypy mastermind_cli/window_scheduler`
- `python3 .claude/commands/mm/discover-contract-check.py --objective context-window-management`

### Acceptance Criteria
- [x] A clean fit, compression-required fit and blocked fit are demonstrated end-to-end.
- [x] Resume payload preserves checkpoint, objective, decision references and next step.
- [x] Canonical status and handoff cite the final validation evidence.
