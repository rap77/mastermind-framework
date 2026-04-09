---
id: PROP-002-C
title: "Assisted Planning Chat — 'Quiero hacer X' → Agent Architecture"
status: CONDITIONAL_APPROVAL
priority: P3
category: Feature
effort: M
updated: 2026-04-06
part_of: PROP-002-v2 (Multi-Channel Orchestrator)
brain_evaluations:
  brain-01: CONDITIONAL_APPROVAL
  brain-02: CONDITIONAL_APPROVAL
  brain-04: CONDITIONAL_APPROVAL
  brain-05: CONDITIONAL_APPROVAL
  brain_07: DEFERRED_UNTIL_A_AND_B
final_verdict: CONDITIONAL_APPROVAL
consensus: Interesting use case BUT frequency UNKNOWN — Templates FIRST, chat LATER
confidence: 50%
next_condition: "PROP-002-A AND PROP-002-B validate demand → THEN reconsider"
---

# Propuesta: Assisted Planning Chat

## Problema Identificado

**Caso de uso:** Manager NO técnico quiere automatizar un proceso pero no sabe cómo.

**Problema actual:**
- Barrera de entrada: "¿Qué agentes necesito?"
- Conocimiento fragmentado: "¿Qué puede hacer MasterMind?"
- Trial-and-error: Crear agentes por ensayo y error = semanas de aprendizaje

**Solución:**
- Query: "Quiero automatizar facturación electrónica"
- Response: "Para esto necesito 3 agentes: invoice-generator, email-sender, webhook-receiver"
- Time to value: 30 segundos (vs 2-3 horas de investigación)

## Por qué es Borderline (no claramente chat-only)

Este caso PUEDE ser resuelto por alternatives:
- **Templates también sirven** — Documentación/guía paso a paso
- **Interactive wizard también sirve** — Form con preguntas
- **Chat es NATURAL** pero NO ÚNICO

**Chat añade valor PERO puede reemplazarse por alternatives más simples.**

## Casos de Uso

### Caso 1: Automatización de Facturación

```
Input: "Quiero automatizar facturación electrónica"

Output:
"🎯 Plan de Automatización — Facturación Electrónica

Para esto necesito crear 3 agentes:

1. **invoice-generator**
   └── Genera facturas en formato AFIP

2. **email-sender**
   └── Envía facturas a clientes por email

3. **webhook-receiver**
   └── Recibe notificaciones de pago

Conexión:
webhook-receiver → invoice-generator → email-sender

¿Querés que los cree ahora? (responde 'sí')

[Ver documentación → link]
[Ver ejemplos similares → link]"

Time to value: 30 segundos (vs 2-3 horas de investigación)
```

### Caso 2: Sincronización de Inventarios

```
Input: "Quiero sincronizar stock entre mi e-commerce y ERP"

Output:
"🎯 Plan de Automatización — Sync de Stock

Agentes necesarios:

1. **ecommerce-inventory-listener**
   └── Escucha cambios en e-commerce (Shopify/WooCommerce)

2. **erp-connector**
   └── Conecta a ERP y actualiza stock

3. **inventory-reconciler**
   └── Detecta discrepancias y alerta

Conexión:
ecommerce-listener → erp-connector → reconciler

⚠️ Consideraciones:
├── ¿Tu e-commerce tiene webhooks? (Shopify sí, WooCommerce requiere plugin)
└── ¿Tu ERP tiene API? (SAP es complejo, uno simple es más fácil)

¿Necesitas ayuda con algún paso?"

[Ver template de sync → link]
```

### Caso 3: Onboarding de Empleados

```
Input: "Quiero automatizar onboarding de nuevos empleados"

Output:
"🎯 Plan de Automatización — Employee Onboarding

Flujo recomendado:

1. **hris-listener** — Escucha nuevo empleado en HRIS
2. **email-welcomer** — Envía email de bienvenida
3. **slack-enroller** — Crea cuenta en Slack
4. **github-provisioner** — Crea cuenta en GitHub
5. **notion-creator** — Crea página en Notion

Conexión:
hris-listener → [email, slack, github, notion]

⏱️ Time: Automatiza ~2 horas de trabajo manual

¿Querés que los cree ahora?"

[Ver template de onboarding → link]
```

## Target Users

| Role | Frecuencia | Pain Point | Value Prop |
|------|-----------|------------|------------|
| **Manager NO técnico** | ¿? | "No sé qué agentes crear" | "Chat me dice el plan en segundos" |
| **Consultor** | 5-10 clientes/mes | "Cada cliente quiere algo diferente" | "Reutilizar planes previos" |
| **CTO de startup** | One-time (setup) | "Quiero automatizar TODO rápido" | "Roadmap en minutos" |

## Contexto

- **Proyecto:** MasterMind v3.0 — Enterprise agent orchestration platform
- **Stack:** Next.js 16 + React 19 + Python FastAPI + Rust Control Plane
- **Referencia:** Paperclip NO tiene planning asistido
- **Competencia:** Zapier/Make tienen "templates" PERO NO chat interactivo

## Scope MVP (v3.0)

### Incluye

✅ **Template Library FIRST (Phase 1)**
   - 10 templates documentados (Markdown)
   - Categorizados: Facturación, Sync, Onboarding, Marketing, etc.
   - Searchable via Command+K

✅ **Template Generator**
   - Editor simple de templates
   - Export/import de templates

✅ **Usage Analytics**
   - ¿Qué templates se usan más?
   - ¿Qué templates se abandonan?

### No incluye (Phase 2+)

❌ Chat interactivo (Phase 2 — only if templates validate demand)
❌ AI-powered suggestions (Phase 3)
❌ Auto-creation de agentes (Phase 3)

## Success Metrics

### Phase 1 (Templates)

| Métrica | Target | ¿Cómo medir? |
|---------|--------|--------------|
| **Template usage** | 100+ uses/mes | Template access logs |
| **Unique users** | 30+ users/mes | User count |
| **Completion rate** | 70%+ | "Used this template" events |
| **Satisfaction** | 4.0+/5.0 | Post-use survey |
| **Time savings** | >1 hora ahorrad | Survey self-report |
| **Repeat usage** | 30%+ usan >1 template | Return user rate |

### Business Impact

| Métrica | Baseline | Target | ROI |
|---------|----------|--------|-----|
| **Time to first agent** | 2-3 horas | 15 min | **90% reduction** |
| **Support tickets** | 20/mes | <5/mes | **75% reduction** |
| **User activation** | 40% | 70% | **75% increase** |

## Open Questions

1. **Frequency validation:** ¿Con qué frecuencia un Manager NO técnico crea workflows?
2. **Template vs Chat:** ¿Prefieren copiar template o chat interactivo?
3. **Knowledge gaps:** ¿Qué problemas NO están cubiertos en templates?
4. **Follow-up needs:** ¿Necesitan preguntar más después del plan inicial?

## Dependencies

| Dependencia | Estado | Nota |
|-------------|--------|------|
| PROP-002-A (Migration) | ⏸️ Bloqueante | Validar chat demand FIRST |
| PROP-002-B (Executive) | ⏸️ Bloqueante | Validar mobile demand FIRST |
| Template engine | ❌ No iniciado | Markdown → HTML |
| Wizard UI | ❌ No iniciado | Form component |
| Chat infrastructure | ❌ No iniciado | Phase 2 only |

## Technical Considerations

### Template Format (Markdown)

```markdown
# Template: Facturación Electrónica

## Descripción
Automatiza generación y envío de facturas en formato AFIP.

## Agentes Necesarios

### 1. invoice-generator
**Rol:** Generador
**Input:** Orden de compra (webhook)
**Output:** Factura PDF (AFIP)
**Config:**
```yaml
afip_certificate: /path/to/cert.pem
afip_environment: production
```

### 2. email-sender
**Rol:** Notificador
**Input:** Factura PDF
**Output:** Email al cliente

### 3. webhook-receiver
**Rol:** Trigger
**Input:** Notificación pago (AFIP)
**Output:** Evento "payment received"

## Conexión (DAG)
```
webhook-receiver → invoice-generator → email-sender
```

## Consideraciones
- Requiere certificado AFIP
- Email template configurable
- Webhook debe ser público

## Ver también
- Template: Sync de Stock
- Documentación: Agentes tipo "Generator"
```

### Template Search (Command+K)

```typescript
// templates/search.ts
interface Template {
  id: string
  title: string
  category: string
  description: string
  content: string // Markdown
}

export async function searchTemplates(query: string): Promise<Template[]> {
  const all = await loadTemplates()
  return all.filter(t =>
    t.title.includes(query) ||
    t.category.includes(query) ||
    t.description.includes(query)
  )
}
```

## Roadmap

```
Phase 0 (1 week): Validation
├── Interview 5 managers NO técnicos
├── Ask: "¿Cómo automatizan procesos hoy?"
├── Ask: "¿Prefieren copiar template o chat?"
└── Decision: Go/No-Go based on demand

Phase 1 (2 weeks): Template Library
├── Create 10 templates (Markdown)
├── Template search (Command+K)
├── Usage analytics
├── NO chat yet (validate templates FIRST)
└── Target: All users

Phase 2 (IF Phase 1 validates): Chat Interface
├── "Quiero hacer X" → Template recommendation
├── Follow-up questions: "¿Necesitas ayuda?"
├── AI-powered suggestions (LLM)
└── Target: Power users

Phase 3 (Future): Auto-Creation
├── "¿Querés que los cree ahora?"
├── Automatically create agents from template
└── One-command automation
```

## Brain Evaluations Summary

### Brain #1 (Product Strategy) — 🔶 50%
✅ **Lo mejor:** Reduce barrera de entrada
⚠️ **Falta:** Evidencia de frecuencia real
🚨 **Peligro:** Templates pueden ser suficientes (chat es overkill)
💭 **Sugerencia:** Templates FIRST, chat AFTER

### Brain #2 (UX Research) — 🔶 55%
✅ **Lo mejor:** Natural language = bajo aprendizaje
⚠️ **Falta:** ¿Prefieren chat o templates?
💭 **Sugerencia:** A/B test templates vs chat

### Brain #4 (Frontend) — 🔶 60%
✅ **Lo mejor:** Templates = Markdown (simple)
⚠️ **Falta:** Search UI para templates
💭 **Sugerencia:** Command+K integration FIRST

### Brain #5 (Backend) — 🔶 58%
✅ **Lo mejor:** Template engine = simple
⚠️ **Falta:** Versioning de templates
💭 **Sugerencia:** Git-based template storage

### Brain #7 (Growth) — 🔄 45%
🔄 **DEFERRED:** Lowest priority de los 3 casos
✅ **Rationale:** Frequency UNKNOWN + templates son alternativa simple
⚠️ **Condición:** Reconsider AFTER A y B validate demand

## Final Veredict

**🔶 CONDITIONAL_APPROVAL** — 50% confidence

**Condiciones para APPROVAL:**

1. **[BLOCKER] PROP-002-A AND PROP-002-B validate demand FIRST**
   - Si chat NO valida demanda en casos A y B → Este caso TAMPOCO justifica chat infra
   - Si casos A y B VALIDAN → Recién considerar chat para este caso

2. **[BLOCKER] Templates FIRST (Phase 1)**
   - NO chat en Phase 1
   - Validar si templates son suficientes
   - Si templates NO se usan → Chat TAMPOCO se usará

3. **[CONDITION] Validate frequency with interviews**
   - Talk to 5 managers NO técnicos
   - "¿Cuántas veces por mes automatizás procesos?"
   - If <1x/month → NOT WORTH building chat

4. **[CONDITION] A/B test templates vs chat**
   - Group A: Solo templates (Markdown)
   - Group B: Templates + Chat
   - Measure: Usage, satisfaction, completion

**Si condiciones se cumplen:**
→ Templates FIRST (low cost, validate utility)
→ Chat AFTER (if templates validate demand)

**Si condiciones NO se cumplen:**
→ Archivar como "Nice to have but low priority"
→ Ahorro: 4-6 semanas de desarrollo

---

**Propuesta creada:** 2026-04-06
**Creado por:** Rafael Padrón (via /mm:propose)
**Estado:** DEFERRED UNTIL PROP-002-A AND PROP-002-B
**Next action:** Esperar resultado de Concierge MVP (PROP-002-A) y Email Alerts (PROP-002-B)
