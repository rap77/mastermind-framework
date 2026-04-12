# MasterMind Framework v2.1 — Session 2026-03-20 Phase 06 Brain Consultation

**Type:** project-context
**Date:** 2026-03-20

## Key Discovery: Orquestador-Driven Architecture Resolves Brain-07 Concerns

**Critical Learning:** Brain-07 inicialmente RECHAZÓ Phase 06 basado en premisa INCORRECTA de "24 cerebros siempre activos + 24 WebSockets concurrentes". Tras aclaración del usuario, cambió a CONDITIONAL APPROVAL (8.5/10).

**Arquitectura Validada:**
- Orquestador (brain-08) decide QUÉ cerebros interactúan (3-6 típicos)
- Solo cerebros ACTIVOS se destacan con neones/animaciones
- NICHOS como unidades de progressive disclosure (Software/Marketing/Master)
- WebSocket lifecycle manejado por Orquestador (connect/disconnect según necesidad)

## MM CLI Protocol Learned

**Patrón correcto para consultar brains técnicos:**
```bash
cd /home/rpadron/proy/mastermind
export $(cat .env | grep -v '^#' | xargs) && cd apps/api && uv run mm orchestrate run "[BRIEF]" --brains [BRAIN_IDS] --use-mcp --parallel
```

**Nota:** El `.env` está en la raíz, pero el CLI se ejecuta desde `apps/api`. Por eso se usa `cd apps/api` después de cargar el `.env`.

## Notebook IDs (Software Development Niche)

| Brain | ID | Domain |
|-------|-----|---------|
| brain-02 UX Research | ea006ece-00a9-4d5c-91f5-012b8b712936 | UX Research |
| brain-04 Frontend | 85e47142-0a65-41d9-9848-49b8b5d2db33 | Frontend |
| brain-05 Backend | c6befbbc-b7dd-4ad0-a677-314750684208 | Backend |
| brain-06 QA/DevOps | 74cd3a81-1350-4927-af14-c0c4fca41a8e | QA/DevOps |
| brain-07 Evaluator | d8de74d6-7028-44ed-b4d5-784d6a9256e6 | Growth/Data (Critical) |

## Momento 2-3 Workflow Validated

**Workflow Mente Maestra para Phase Planning:**
1. Momento 1: discuss-phase (UX) — Captura QUÉ quiere el usuario
2. Momento 2: Brains técnicos (Frontend/Backend/QA/UX) — CÓMO implementarlo
3. Momento 3: Brain-07 evalúa TODO el conjunto — APROBAR o iterar
4. → /gsd:plan-phase N

**Resultado:** Brain-07 aprobó con 4 condiciones no-bloqueantes (todas sobre Orquestador/Framework, fuera de Phase 06 scope).

## Phase 06 Status

**Current:** Ready for planning
**Next Command:** `/gsd:plan-phase 06 --skip-research`
**Context Files Created:** 6 (CONTEXT-FINAL + 5 BRAIN-XX-CONTEXT.md)
**Handoff:** .planning/phases/06-command-center/.continue-here.md
