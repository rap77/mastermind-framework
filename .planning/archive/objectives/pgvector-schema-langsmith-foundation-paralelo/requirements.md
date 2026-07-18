# Requirements — pgvector-schema-langsmith-foundation-paralelo

## Problem / Purpose
Phase 20 was historically marked complete, but the active objective catalog still
selected it as pending. Reconcile the planning ledger with the existing pgvector
and LangSmith foundation without reimplementing completed runtime behavior.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Verify the existing Phase 20 foundation against its historical acceptance markers:
  pgvector schema and HNSW index, asyncpg similarity search, runtime dependencies,
  LangSmith tracing, and the OEC baseline utility.
- Correct the canonical v3.2 roadmap status for Phase 20 when that evidence passes.
- Archive the reconciled objective through the existing planning lifecycle.

## Out of Scope
- No new pgvector schema, embedding provider, RAG retrieval, or LangSmith runtime
  implementation; those are already present.
- No database migration execution, external LangSmith calls, or changes to secrets.
- No manual edits to generated objective progress artifacts.

## Non-negotiables
- Keep validation offline and credential-free.
- Preserve the existing fail-soft LangSmith behavior.
- Use lifecycle handlers, rather than manual ledger edits, for task progress and
  objective archival.

## Objective-level Acceptance Criteria
- [ ] The focused foundation verification and its Phase 20 unit coverage pass.
- [ ] The historical Phase 20 completion evidence is recorded in this package.
- [ ] `.planning/ROADMAP-v3.2.md` marks Phase 20 complete rather than pending.
- [ ] The objective is archived through the planning lifecycle without manually
  editing generated progress artifacts.
