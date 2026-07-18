# Requirements — domain-security-assurance-plane

## Problem / Purpose

MasterMind tiene un baseline AI-DLC y una capability `policy-security`, pero no
dispone de profiles por dominio, threat/control evidence, readiness veto ni un
lifecycle auditable de risk acceptance.

El objetivo es implementar una Security Assurance Plane reusable por onboarding
y otros harnesses, adaptable a software, marketing, finanzas y futuros nichos.

## Stakeholders / Users

- maintainers y operadores de MasterMind
- security, compliance y risk reviewers
- owners de proyectos adoptados
- domain adapters y execution harnesses
- usuarios afectados por incidentes o exposición de datos

## Scope

- SecurityProfile versionado
- baseline + domain + project + jurisdiction composition
- asset/data classification y threat records
- security fields en Gap Registry
- control evidence verification
- readiness veto
- risk treatment y acceptance con expiry
- domain overlay registry
- persistence, lineage y behavioral cases

## Out of Scope

- reemplazar herramientas SAST/DAST o auditores externos
- ofrecer interpretación legal autónoma
- implementar todos los overlays regulatorios posibles
- almacenar secrets o raw sensitive evidence
- ejecutar remediaciones dentro del verifier
- certificar formalmente compliance

## Non-negotiables

- policy, profile y verifier permanecen separados
- critical/high findings controlan readiness
- checks no ejecutados no aprueban
- risk acceptance requiere human authority y expiry
- regulatory rules requieren source version y jurisdiction
- security gaps viven en Gap Registry, no en backlog paralelo
- evidence nunca incluye secretos ni payloads sensibles
- domain overlays no modifican el core

## Functional Requirements

- [x] Componer SecurityProfile con precedencia determinista.
- [x] Clasificar assets, actors, data y trust boundaries.
- [x] Registrar threats, controls y evidence requirements.
- [x] Ejecutar assurance passes con stop rules.
- [x] Aplicar readiness veto según severity y treatment.
- [x] Persistir risk acceptance y reabrirlo al expirar.
- [x] Resolver domain overlays por adapter/jurisdiction.
- [x] Producir SecurityReadinessVerdict estructurado.

## Objective-level Acceptance Criteria

- [x] Software, marketing y finance profiles producen overlays distintos.
- [x] Critical/high findings bloquean según policy.
- [x] Medium acceptance exige owner, approval y expiry.
- [x] Unperformed evidence no produce compliance.
- [x] Sources obsoletas o contradictorias escalan.
- [x] Security history y remediation lineage son consultables.
- [x] Existing generic harness routing permanece compatible.
- [x] Canonical status refleja evidencia real de implementación.
