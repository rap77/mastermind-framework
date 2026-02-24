---
source_id: "FUENTE-709"
brain: "brain-software-07-growth-data"
niche: "software-development"
title: "Checklist de Evaluación por Cerebro — Compilación Interna"
author: "MasterMind Framework (auto-generated)"
expert_id: "N/A"
type: "internal_compilation"
language: "es"
generated_from: "evaluation-criteria.md de cada cerebro (01-06)"
skills_covered: ["HR1", "HR2", "HR3", "HR4", "HR5", "HR6"]
version: "1.0.0"
last_updated: "2026-02-23"
changelog:
  - "v1.0.0: Template inicial — se auto-genera con mastermind brain compile-radar --brain 07"
status: "template"
distillation_date: "2026-02-23"
distillation_quality: "template_only"
loaded_in_notebook: false
auto_generated: true
generate_command: "mastermind brain compile-radar --brain 07"
---

# FUENTE-709: Checklist de Evaluación por Cerebro

## Propósito

Este documento es generado automáticamente por el CLI. Compila los criterios de evaluación de cada cerebro (01-06) en un solo checklist que el Cerebro #7 usa como referencia rápida para saber QUÉ VERIFICAR en el output de cada cerebro.

**Comando para regenerar:** `mastermind brain compile-radar --brain 07`

**Cuándo regenerar:** Cada vez que se actualice el evaluation-criteria de cualquier cerebro.

---

## Checklist por Cerebro

### Cerebro #1 — Product Strategy

> *Fuente: docs/software-development/01-product-strategy-brain/evaluation-criteria.md*

- [ ] ¿Define problema claro y validado con evidencia?
- [ ] ¿Identifica persona/audiencia específica (no "todos")?
- [ ] ¿OKRs con Key Results numéricos y basados en outcomes?
- [ ] ¿Evaluó los 4 riesgos de discovery (valor, usabilidad, factibilidad, viabilidad)?
- [ ] ¿Propuesta de valor diferenciada vs alternativas?
- [ ] ¿Incluye suposiciones marcadas como hipótesis?
- [ ] ¿Tiene análisis de escenario de fallo (pre-mortem)?
- [ ] ¿Aplica frameworks con profundidad, no solo los menciona?

### Cerebro #2 — UX Research

> *Fuente: docs/software-development/02-ux-research-brain/evaluation-criteria.md*

- [ ] ¿Se habló con usuarios reales? ¿Cuántos?
- [ ] ¿Los usuarios son del segmento correcto?
- [ ] ¿Se usaron story-based interviews (no leading questions)?
- [ ] ¿Los insights están respaldados por citas de usuarios, no por interpretación?
- [ ] ¿El Opportunity Solution Tree tiene al menos 3 niveles?
- [ ] ¿Las oportunidades priorizadas tienen evidencia de impacto?
- [ ] ¿Se consideraron sesgos de los propios investigadores?

### Cerebro #3 — UI/UX Design

> *Fuente: docs/software-development/03-ui-design-brain/evaluation-criteria.md*

- [ ] ¿El diseño sigue un design system consistente?
- [ ] ¿La jerarquía visual prioriza claridad sobre estética?
- [ ] ¿Se consideró accesibilidad (contraste, tamaños, screen readers)?
- [ ] ¿Los flujos principales requieren mínimos pasos?
- [ ] ¿Se prototiparon y testearon con usuarios?
- [ ] ¿El diseño responde a los insights del Cerebro #2?
- [ ] ¿Los edge cases están diseñados (estados vacíos, errores, loading)?

### Cerebro #4 — Frontend Development

> *Fuente: docs/software-development/04-frontend-brain/evaluation-criteria.md*

- [ ] ¿La performance es aceptable? (LCP < 2.5s, FID < 100ms, CLS < 0.1)
- [ ] ¿La implementación respeta el diseño del Cerebro #3?
- [ ] ¿Hay responsive design para mobile/tablet/desktop?
- [ ] ¿La accesibilidad implementada (ARIA labels, keyboard nav)?
- [ ] ¿Los componentes son reutilizables y consistentes?
- [ ] ¿Hay error boundaries y manejo de estados de carga?
- [ ] ¿El bundle size es razonable para el tipo de app?

### Cerebro #5 — Backend Development

> *Fuente: docs/software-development/05-backend-brain/evaluation-criteria.md*

- [ ] ¿La arquitectura escala para el volumen esperado?
- [ ] ¿Hay single points of failure (SPOF)?
- [ ] ¿Los endpoints tienen rate limiting y validación de input?
- [ ] ¿La base de datos tiene índices y queries optimizados?
- [ ] ¿Hay logging y monitoring para diagnóstico de problemas?
- [ ] ¿La autenticación y autorización son robustas?
- [ ] ¿Los datos sensibles están encriptados at rest y in transit?
- [ ] ¿La API tiene documentación (OpenAPI/Swagger)?

### Cerebro #6 — QA & DevOps

> *Fuente: docs/software-development/06-qa-devops-brain/evaluation-criteria.md*

- [ ] ¿Hay tests? ¿Qué cobertura? (mínimo 70% para core)
- [ ] ¿Los tests cubren happy path Y edge cases?
- [ ] ¿El deployment es automatizado (CI/CD)?
- [ ] ¿Hay rollback strategy si algo falla en producción?
- [ ] ¿Hay monitoring y alertas configuradas?
- [ ] ¿Los environments están separados (dev/staging/prod)?
- [ ] ¿Hay runbook para incidentes comunes?
- [ ] ¿Se definieron SLOs (Service Level Objectives)?

---

## Cómo Usa el #7 este Checklist

1. Recibe output del Cerebro X
2. Consulta la sección correspondiente de este documento
3. Verifica cada item del checklist contra el output
4. Items faltantes se reportan en el evaluation-report
5. Items faltantes críticos pueden causar REJECT directamente

**Nota:** Este checklist es el radar superficial. La evaluación profunda usa las evaluation-matrices de `skills/evaluator/evaluation-matrices/`.
