# Requirements — adaptive-onboarding-harness-runtime

## Problem / Purpose

MasterMind necesita adoptar ideas, repositorios y proyectos en cualquier estado
y dominio. AI-DLC Discovery cubre intención humana de software; MM-flow cubre
reconciliación y planning operacional. Ninguno por separado supervisa current
state, target state, multi-pass gaps, delegated completion y reassessment entre
nichos.

El objetivo es implementar `project-adoption-lead` como harness supervisor
universal con adapters de dominio y security assurance obligatoria.

## Stakeholders / Users

- owners de proyectos e iniciativas
- maintainers y operadores de MasterMind
- domain experts y approvers
- agentes que ejecutan work waves
- equipos que adoptan proyectos externos

## Scope

- onboarding modes greenfield, brownfield, completion, rescue, audit,
  continuation y migration
- universal current/target state contracts
- evidence inventory
- multi-pass Gap Registry loop
- readiness classification
- execution-wave planning, delegation y reassessment
- Domain Adapter Contract y registry
- security profile/veto integration
- Software Onboarding Adapter contract seam y test fixture
- persistence, lineage, handoff y core-promotion candidates

## Out of Scope

- implementar Software, Marketing o Finance adapters completos
- ejecutar todo trabajo dentro de onboarding
- reemplazar domain execution harnesses
- crear un nuevo project-management system
- certificar compliance
- forzar reverse engineering o entrevistas si no aportan valor
- activar este objective mientras otro siga activo sin decisión explícita

## Non-negotiables

- core domain-agnostic; reglas específicas viven en adapters
- onboarding supervisa y delega; no es executor universal
- current state se basa en evidencia, no en declaraciones solamente
- target state define completion antes de planificar gaps
- cada pass tiene rúbrica y stop rule
- security assurance controla readiness
- gaps tienen evidence, owner y acceptance criteria
- un único objective activo por default
- handoff permite reanudación sin chat history

## Functional Requirements

- [ ] Clasificar mode y domain con rationale.
- [ ] Versionar CurrentStateSnapshot y TargetStateDefinition.
- [ ] Inventariar evidencia con source/confidence.
- [ ] Detectar y deduplicar gaps en pasadas especializadas.
- [ ] Calcular readiness sin promediar blockers.
- [ ] Crear waves dependency-ready y delegarlas a harnesses.
- [ ] Reassess por delta después de cada wave.
- [ ] Resolver adapters por contrato y capability availability.
- [ ] Integrar SecurityProfile y security veto.
- [ ] Validar el Software Onboarding Adapter contract con un fixture sin implementar el adapter productivo.
- [ ] Persistir artifacts, gaps, verdicts, decisions y checkpoints.

## Objective-level Acceptance Criteria

- [ ] El core procesa casos greenfield, brownfield, completion y audit.
- [ ] Dos pasadas sin gaps materiales nuevos detienen el loop.
- [ ] Gaps críticos bloquean readiness.
- [ ] Execution waves usan harnesses especializados.
- [ ] Reassessment actualiza por delta y conserva lineage.
- [ ] El adapter fixture prueba AI-DLC/MM-flow ownership; la implementación queda en `software-onboarding-domain-adapter`.
- [ ] Adapter ausente o capability faltante produce blocked/escalated explícito.
- [ ] Security assurance se aplica a cada wave relevante.
- [ ] Project state y planning permiten reanudación.
- [ ] Existing harness routes permanecen compatibles.
