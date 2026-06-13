# Objective Roadmap

_Generated: 2026-06-12T21:41:19_

## Recommended next objective

- `project-state-mvp`
- Why: ready now, highest deterministic priority (40), unlocks 9 downstream objective(s).

## Status summary

- Active: 1
- Planned/blocked: 7
- Done: 45

| Rank | Objective | Status | Ready Now | Gate | Priority | Recommended | MVP | Dependencies | Why it matters | Evidence |
|---:|---|---|---|---|---:|---|---|---|---|---|
| 1 | `project-state-mvp` | active | yes | n/a | 40 | yes | yes | — | Structured planning package already exists. | .mm-flow/planning/changes/project-state-mvp |
| 2 | `backend-service-boundary-for-agents` | planned | yes | n/a | 95 | no | yes | project-state-mvp | Captured in canonical implementation docs. | docs/canonical/34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md |
| 3 | `postgres-hybrid-data-model` | planned | yes | n/a | 92 | no | yes | project-state-mvp | Captured in canonical implementation docs. | docs/canonical/27-POSTGRES-HYBRID-DATA-MODEL.md |
| 4 | `engineering-doctrine-layer` | planned | yes | n/a | 86 | no | yes | project-state-mvp | Captured in canonical implementation docs. | docs/canonical/22-ENGINEERING-DOCTRINE-LAYER.md |
| 5 | `token-cost-quality-telemetry` | planned | yes | n/a | 84 | no | yes | project-state-mvp | Captured in canonical implementation docs. | docs/canonical/25-TOKEN-COST-AND-QUALITY-TELEMETRY.md |
| 6 | `collaboration-rbac` | planned | yes | n/a | 82 | no | yes | project-state-mvp | Captured in canonical implementation docs. | docs/canonical/23-COLLABORATION-AND-RBAC-MODEL.md |
| 7 | `dashboard-realtime` | planned | yes | n/a | 78 | no | yes | project-state-mvp | Captured in canonical implementation docs. | docs/canonical/33-DASHBOARD-REALTIME-EVENTS.md |
| 8 | `artifact-versioning-and-lineage` | planned | yes | n/a | 40 | no | yes | project-state-mvp | Captured in canonical implementation docs. | docs/canonical/26-ARTIFACT-VERSIONING-AND-LINEAGE.md |
| 9 | `window-scheduler` | done | no | n/a | 76 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/window-scheduler, docs/canonical/16-WINDOW-SCHEDULER-ARCHITECTURE.md, docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md |
| 10 | `context-window-management` | done | no | n/a | 74 | no | yes | window-scheduler | Structured planning package already exists. | .mm-flow/planning/archive/objectives/context-window-management, docs/canonical/20-CONTEXT-WINDOW-MANAGEMENT-ARCHITECTURE.md |
| 11 | `context-projection` | done | no | n/a | 72 | no | yes | postgres-hybrid-data-model, project-state-mvp | Structured planning package already exists. | .mm-flow/planning/archive/objectives/context-projection, docs/canonical/28-CONTEXT-PROJECTION-STRATEGY.md |
| 12 | `rust-control-plane-hardening` | done | no | n/a | 70 | no | yes | backend-service-boundary-for-agents | Structured planning package already exists. | .mm-flow/planning/archive/objectives/rust-control-plane-hardening, docs/canonical/44-RUST-CONTROL-PLANE-HARDENING-PLAN.md |
| 13 | `rust-control-plane` | done | no | n/a | 68 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/rust-control-plane |
| 14 | `observability-real-time-hub` | done | no | n/a | 66 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/observability-real-time-hub |
| 15 | `knowledge-distillation` | done | no | n/a | 62 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/knowledge-distillation |
| 16 | `knowledge-ingestion-manual` | done | no | n/a | 60 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/knowledge-ingestion-manual |
| 17 | `multi-channel-gateway` | done | no | n/a | 58 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/multi-channel-gateway |
| 18 | `pgvector-schema-langsmith-foundation-paralelo` | done | no | n/a | 56 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/pgvector-schema-langsmith-foundation-paralelo |
| 19 | `task-time-and-estimation` | done | no | n/a | 55 | no | yes | project-state-mvp | Structured planning package already exists. | .mm-flow/planning/archive/objectives/task-time-and-estimation, docs/canonical/24-TASK-TIME-AND-ESTIMATION-MODEL.md |
| 20 | `rag-evaluation-gate` | done | no | n/a | 54 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/rag-evaluation-gate |
| 21 | `rag-pilot-brain-1-only` | done | no | n/a | 53 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/rag-pilot-brain-1-only |
| 22 | `rag-scale-out-brains-2-7` | done | no | n/a | 52 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/rag-scale-out-brains-2-7 |
| 23 | `vertical-slice` | done | no | n/a | 50 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/vertical-slice |
| 24 | `mastermind-cli` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mastermind-cli |
| 25 | `mm-flow-cli` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-flow-cli |
| 26 | `mm-harness-active-objective-coordination` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-active-objective-coordination |
| 27 | `mm-harness-context-intake-and-canonicalization` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-context-intake-and-canonicalization |
| 28 | `mm-harness-exception-authoring-drift-reduction` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-exception-authoring-drift-reduction |
| 29 | `mm-harness-exception-authoring-workflow` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-exception-authoring-workflow |
| 30 | `mm-harness-exception-command-bundle-metadata` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-exception-command-bundle-metadata |
| 31 | `mm-harness-exception-delegated-command-scopes` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-exception-delegated-command-scopes |
| 32 | `mm-harness-exception-expiration-metadata` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-exception-expiration-metadata |
| 33 | `mm-harness-exception-named-bundle-references` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-exception-named-bundle-references |
| 34 | `mm-harness-exception-replace-preview` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-exception-replace-preview |
| 35 | `mm-harness-exception-replace-workflow` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-exception-replace-workflow |
| 36 | `mm-harness-exception-update-workflow` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-exception-update-workflow |
| 37 | `mm-harness-gap-archive-auto-sync` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gap-archive-auto-sync |
| 38 | `mm-harness-gap-dedupe-and-priority` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gap-dedupe-and-priority |
| 39 | `mm-harness-gap-discover-auto-sync` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gap-discover-auto-sync |
| 40 | `mm-harness-gap-objective-lifecycle-sync` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gap-objective-lifecycle-sync |
| 41 | `mm-harness-gap-promotion-assistant` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gap-promotion-assistant |
| 42 | `mm-harness-gap-registry-and-promotion` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gap-registry-and-promotion |
| 43 | `mm-harness-gap-registry-ui` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gap-registry-ui |
| 44 | `mm-harness-gap-registry-ui-triage` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gap-registry-ui-triage |
| 45 | `mm-harness-gate-aware-roadmap-reranking` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gate-aware-roadmap-reranking |
| 46 | `mm-harness-gate-blocked-roadmap-fallback` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-gate-blocked-roadmap-fallback |
| 47 | `mm-harness-lifecycle-gate-integration` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-lifecycle-gate-integration |
| 48 | `mm-harness-multi-active-exception-metadata` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-multi-active-exception-metadata |
| 49 | `mm-harness-multi-active-exception-runtime-recognition` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-multi-active-exception-runtime-recognition |
| 50 | `mm-harness-objective-context-check` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-objective-context-check |
| 51 | `mm-harness-roadmap-activation-gate-awareness` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-roadmap-activation-gate-awareness |
| 52 | `mm-harness-runtime-entrypoint-and-adapters` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-runtime-entrypoint-and-adapters |
| 53 | `mm-harness-unblock-priority-heuristics` | done | no | n/a | 40 | no | yes | — | Structured planning package already exists. | .mm-flow/planning/archive/objectives/mm-harness-unblock-priority-heuristics |
