# Todo — pgvector-schema-langsmith-foundation-paralelo

<!-- topology-source: tasks.md -->

## Execution Checklist

- [x] T1: Verify the existing Phase 20 foundation
  - [x] T1.1: Run the focused Phase 20 unit tests for foundation verification and LangSmith instrumentation.
  - [x] T1.2: Generate the credential-free foundation report and compare its checks with archived tasks 20.01 through 20.25.
  - depends_on: None
  - validation: uv run pytest tests/unit/test_rag_foundation_verify.py tests/unit/test_rag_langsmith.py | uv run python -m mastermind_cli.rag.foundation_verify

- [x] T2: Reconcile the canonical Phase 20 roadmap state
  - [x] T2.1: Update the Phase 20 status in the canonical v3.2 roadmap from pending to complete using T1 evidence.
  - [x] T2.2: Validate the reconciled package with the objective discovery contract check.
  - depends_on: T1
  - validation: Review the Phase 20 row and objective package against T1 evidence. | /mm:discover-contract-check --objective pgvector-schema-langsmith-foundation-paralelo

- [x] T3: Prepare the reconciled objective for archival
  - [x] T3.1: Confirm the reconciled requirements, design, task plan, and validation evidence are complete.
  - [x] T3.2: Verify required archive artifacts exist and the lifecycle can close the objective after T3 completes.
  - depends_on: T2
  - validation: /mm:complete-task T3 --brief | /mm:archive-objective --objective pgvector-schema-langsmith-foundation-paralelo --summary-only
