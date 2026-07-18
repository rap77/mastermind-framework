# DR-013 — Adaptive Delivery Core and Domain Adapters

## 1. Decision Metadata

- **Decision ID:** DR-013
- **Date:** 2026-07-14
- **Status:** Approved
- **Related project:** MasterMind
- **Related capability:** Cross-Domain Delivery
- **Related objective:** `adaptive-delivery-harness-runtime`

## 2. Problem Statement

El término Implementation Harness actual asume código y no representa delivery
de marketing, finanzas u otros dominios. Copiar AI-DLC Construction completo al
core también filtraría stages, artifacts y herramientas específicas de software.

## 3. Options Considered

### Option A — Implementation Harness exclusivo de software

- **Benefits:** mapping directo a código y tests
- **Risks:** obliga a crear otro supervisor por dominio
- **Rejected:** duplica unidades, dependencies, gates, evidence y acceptance

### Option B — AI-DLC Construction como core universal

- **Benefits:** workflow maduro y detallado
- **Risks:** vocabulario de code, NFR, infrastructure y build en todos los nichos
- **Rejected:** confunde invariantes con implementación de software

### Option C — Adaptive Delivery core más domain adapters

- **Benefits:** unit loop universal, especialización versionada y reuse real
- **Risks:** exige contracts estrictos y adapter conformance tests
- **Selected:** mantiene un core pequeño sin perder profundidad por dominio

## 4. Final Decision

MasterMind implementará `adaptive-delivery-lead` como único Role Harness
primario. El core gobernará DeliveryUnits, route planning, plan-before-production,
unit verification, integration acceptance, assurance, recovery y persistence.

AI-DLC conservará Inception y macro lifecycle. Su Construction se ejecutará por
el profile `aidlc-construction` del `software-delivery` adapter. MM-flow seguirá
siendo el control plane operacional.

## 5. Consequences

- Implementation Harness queda como alias conceptual de compatibilidad software
- domain producers se resuelven como adapter capabilities, no segundo role
- approval strict de AI-DLC vive en su profile, no hardcoded en el core
- Build and Test requiere evidencia real, no instruction artifacts solamente
- Operations queda como handoff hasta existir un harness operacional
- otros dominios pueden adoptar el core sin vocabulario de software

## 6. Reversal Conditions

Revisar si:

- los dominios no comparten unit/dependency/evidence/acceptance semantics
- el adapter contract requiere excepciones core frecuentes
- AI-DLC cambia Construction de forma incompatible con el profile versionado

## 7. Links / Artifacts

- `docs/canonical/114-ADAPTIVE-DELIVERY-HARNESS-RUNTIME-CONTRACT.md`
- `docs/canonical/115-SOFTWARE-DELIVERY-DOMAIN-ADAPTER.md`
- `.planning/changes/adaptive-delivery-harness-runtime/`
- `.planning/changes/software-delivery-domain-adapter/`

## Key Learnings:

1. Delivery es universal; code generation es una realización de dominio.
2. AI-DLC y MM-flow tienen ownership complementario, no competitivo.
3. Un adapter debe cambiar vocabulario y capabilities sin cambiar el core.
