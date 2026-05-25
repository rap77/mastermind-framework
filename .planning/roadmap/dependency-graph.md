# Objective Dependency Graph

## Edges

- `project-state-mvp` -> `backend-service-boundary-for-agents`
- `project-state-mvp` -> `artifact-versioning-and-lineage`
- `project-state-mvp` has no declared prerequisites
- `project-state-mvp` -> `postgres-hybrid-data-model`
- `project-state-mvp` -> `engineering-doctrine-layer`
- `project-state-mvp` -> `token-cost-quality-telemetry`
- `project-state-mvp` -> `collaboration-rbac`
- `project-state-mvp` -> `dashboard-realtime`
- `window-scheduler` has no declared prerequisites
- `window-scheduler` -> `context-window-management`
- `postgres-hybrid-data-model` -> `context-projection`
- `project-state-mvp` -> `context-projection`
- `backend-service-boundary-for-agents` -> `rust-control-plane-hardening`
- `rust-control-plane` has no declared prerequisites
- `observability-real-time-hub` has no declared prerequisites
- `knowledge-distillation` has no declared prerequisites
- `knowledge-ingestion-manual` has no declared prerequisites
- `multi-channel-gateway` has no declared prerequisites
- `pgvector-schema-langsmith-foundation-paralelo` has no declared prerequisites
- `project-state-mvp` -> `task-time-and-estimation`
- `rag-evaluation-gate` has no declared prerequisites
- `rag-pilot-brain-1-only` has no declared prerequisites
- `rag-scale-out-brains-2-7` has no declared prerequisites
- `vertical-slice` has no declared prerequisites

## Recommended next active objective

- `postgres-hybrid-data-model`
