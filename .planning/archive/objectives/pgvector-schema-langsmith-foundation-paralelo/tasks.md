# Tasks — pgvector-schema-langsmith-foundation-paralelo

## Execution Rules
- Execute tasks in dependency order unless parallelization is explicitly safe.
- Update this file and the handoff when a task is completed or blocked.
- Each task must declare purpose, dependencies, likely file touchpoints, validation commands, and acceptance criteria.

## T1: Verify the existing Phase 20 foundation

### Purpose
Confirm the historical Phase 20 completion record still matches the current
pgvector and LangSmith implementation.

### Depends On
None

### Parallelizable
no

### Files / Areas Likely Touched
- apps/api/mastermind_cli/rag/foundation_verify.py
- apps/api/tests/unit/test_rag_foundation_verify.py
- apps/api/tests/unit/test_rag_langsmith.py
- .planning/archive/legacy/root-tasks/todo.md

### Validation Commands
- uv run pytest tests/unit/test_rag_foundation_verify.py tests/unit/test_rag_langsmith.py
- uv run python -m mastermind_cli.rag.foundation_verify

### Acceptance Criteria
- [x] The focused verification report passes all pgvector and LangSmith checks.
- [x] The Phase 20 unit tests pass without credentials or external services.
- [x] The historical task list is confirmed as the source of the reconciled scope.

### Execution Subtasks
- T1.1: Run the focused Phase 20 unit tests for foundation verification and LangSmith instrumentation.
- T1.2: Generate the credential-free foundation report and compare its checks with archived tasks 20.01 through 20.25.

## T2: Reconcile the canonical Phase 20 roadmap state

### Purpose
Mark the v3.2 Phase 20 roadmap entry complete after T1 verifies that the
foundation remains present.

### Depends On
T1

### Parallelizable
no

### Files / Areas Likely Touched
- .planning/ROADMAP-v3.2.md
- .planning/changes/pgvector-schema-langsmith-foundation-paralelo/requirements.md
- .planning/changes/pgvector-schema-langsmith-foundation-paralelo/design.md

### Validation Commands
- Review the Phase 20 row and objective package against T1 evidence.
- /mm:discover-contract-check --objective pgvector-schema-langsmith-foundation-paralelo

### Acceptance Criteria
- [x] `.planning/ROADMAP-v3.2.md` no longer labels Phase 20 as pending.
- [x] The package records that no runtime implementation is required.
- [x] The objective contract check passes after the reconciliation.

### Execution Subtasks
- T2.1: Update the Phase 20 status in the canonical v3.2 roadmap from pending to complete using T1 evidence.
- T2.2: Validate the reconciled package with the objective discovery contract check.

## T3: Prepare the reconciled objective for archival

### Purpose
Confirm that the reconciliation evidence and generated objective projections are
ready for the archive lifecycle to close the objective.

### Depends On
T2

### Parallelizable
no

### Files / Areas Likely Touched
- .planning/changes/pgvector-schema-langsmith-foundation-paralelo/
- .planning/HANDOFF-CURRENT.md

### Validation Commands
- /mm:complete-task T3 --brief
- /mm:archive-objective --objective pgvector-schema-langsmith-foundation-paralelo --summary-only

### Acceptance Criteria
- [x] Root tasks are completed through MM lifecycle handlers.
- [x] The objective package has all required artifacts and no pending work.
- [x] The archive lifecycle reports that the objective is eligible for closure.

### Execution Subtasks
- T3.1: Confirm the reconciled requirements, design, task plan, and validation evidence are complete.
- T3.2: Verify required archive artifacts exist and the lifecycle can close the objective after T3 completes.
