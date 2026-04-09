---
id: PROP-002-A
title: "Migration Analysis Chat — N8N/Zapier/Make → MasterMind Agents"
status: CONDITIONAL_APPROVAL
priority: P1
category: Feature
effort: M
updated: 2026-04-06
part_of: PROP-002-v2 (Multi-Channel Orchestrator)
brain_evaluations:
  brain-01: CONDITIONAL_APPROVAL
  brain-02: CONDITIONAL_APPROVAL
  brain-04: CONDITIONAL_APPROVAL
  brain-05: CONDITIONAL_APPROVAL
  brain_07: APPROVED_WITH_CONDITIONS
final_verdict: CONDITIONAL_APPROVAL
consensus: All brains agree — this is the ONLY real chat-only superpower, requires Concierge MVP FIRST
confidence: 75%
next_condition: "Concierge MVP (1 week) — 3-5 LATAM clients"
---

# Propuesta: Migration Analysis Chat

## Problema Identificado

**Caso de uso REAL de onboarding:** Implementadores quieren migrar flujos existentes desde N8N/Zapier/Make a MasterMind.

**Problema actual:**
- Analizar manualmente un workflow de N8N toma **semanas**
- Requiere entender cada nodo, conexión, credencial
- Propenso a errores humanos
- Alta fricción durante onboarding → churn

**Solución:**
- Compartir JSON exportado de N8N/Zapier/Make
- Agente analiza y recomienda qué agentes crear
- Reduce **weeks → minutes**

## Por qué es Chat-Only Superpower

Command+K, dashboards, reportes NO pueden hacer esto porque:
- **Input complejo:** Archivo JSON con 100+ nodos
- **Análisis sintáctico:** Mapear nodos a agentes requiere entender N8N structure
- **Síntesis experta:** No es solo "mostrar datos", es **traducir** un lenguaje a otro

## Casos de Uso

### Caso 1: N8N → MasterMind

```
Input: JSON exportado de N8N (1,000+ nodos posibles)
Output:
├── "He detectado 3 nodos principales:"
│   ├── Webhook (trigger) → Agent: webhook-receiver
│   ├── HTTP Request → Agent: api-client
│   └── Code (JavaScript) → Agent: script-executor
├── "Recomendación: Crear 3 agentes conectados en DAG"
└── "¿Querés que los cree ahora? (responde 'sí')"

Value: 2 semanas de análisis manual → 5 minutos de chat
```

### Caso 2: Zapier → MasterMind

```
Input: ZIP exportado de Zapier
Output:
├── "Tu flujo de Zapier tiene 5 steps:"
│   ├── Trigger: New Email → Agent: email-listener
│   ├── Action: Create Google Doc → Agent: doc-creator
│   └── Filter: Only if attachment → Agent: content-filter
├── "En MasterMind esto sería:"
└── DAG: email-listener → content-filter → doc-creator

Value: 1 semana de análisis manual → 3 minutos de chat
```

### Caso 3: Make (Integromat) → MasterMind

```
Input: Scenario export JSON
Output: Análisis + recomendación de agentes

Value: Same pattern — hours → minutes
```

## Target Users

| Role | Frecuencia | Pain Point | Value Prop |
|------|-----------|------------|------------|
| **Implementador** | One-time por cliente | "Analizar 100 workflows es imposible" | "Analicé 100 en 2 horas" |
| **DevOps Consultant** | Recurrente (5-10 clientes/mes) | "N8N es legado, quiero migrar todo" | "Migración enterprise en días, no meses" |
| **CTO de startup** | One-time (migración inicial) | "No tengo tiempo para aprender N8N" | "Chat me dice qué hacer en minutos" |

## Contexto

- **Proyecto:** MasterMind v3.0 — Enterprise agent orchestration platform
- **Stack:** Next.js 16 + React 19 + Python FastAPI + Rust Control Plane
- **Referencia:** Paperclip NO tiene esta funcionalidad
- **Competencia:** N8N/Zapier/Make NO tienen "migrate to another platform" feature

## Scope MVP (v3.0)

### Incluye

✅ **N8N Analysis ONLY** (Phase 1)
   - Input: JSON export
   - Output: Lista de agentes + recomendación de DAG
   - Format: WhatsApp + Dashboard chat

✅ **File Upload**
   - Drag-drop JSON
   - Validación client-side (max 10MB)
   - Web Worker para parsing (no bloquear UI)

✅ **Role-Based Security**
   - Technical users pueden ver análisis completo
   - Manager users ven resumen ejecutivo

✅ **Authentication**
   - Phone number → user mapping (WhatsApp)
   - JWT (dashboard chat)

### No incluye (Phase 2+)

❌ Zapier analysis (Phase 2)
❌ Make analysis (Phase 2)
❌ Auto-creation de agentes (Phase 2)
❌ Historical migration data (Phase 2)

## Success Metrics

### Phase 1 (v3.0)

| Métrica | Target | ¿Cómo medir? |
|---------|--------|--------------|
| **Adopción** | 20+ implementadores usan en primer mes | Unique user count |
| **Análisis completados** | 50+ workflows analizados | Analysis logs |
| **Time savings** | >90% users reportan >2 horas ahorradas | Post-analysis survey |
| **Satisfacción** | 4.5+/5.0 | Post-analysis survey |
| **Recurring use** | 30%+ usan >1 vez | Return user rate |

### Business Impact

| Métrica | Baseline | Target | ROI |
|---------|----------|--------|-----|
| **Onboarding time** | 2 semanas | 2 horas | **91% reduction** |
| **Churn during onboarding** | 40% | <10% | **75% reduction** |
| **Migration win rate** vs N8N | N/A | 60% | Competitive advantage |

## Open Questions

1. **N8N schema changes:** ¿Qué pasa si N8N cambia su formato de export?
2. **Edge cases:** ¿Qué pasa si el JSON está corrupto?
3. **Large workflows:** ¿JSON de 50MB+? ¿Cómo manejar?
4. **Error handling:** ¿Si el análisis falla, qué le decimos al usuario?

## Dependencies

| Dependencia | Estado | Nota |
|-------------|--------|------|
| Rust Control Plane | ⏸️ Phase 15 | Orquestador corre en Rust |
| PostgreSQL | ⏸️ Phase 15 | Para persistencia de análisis |
| WhatsApp Business API | ❌ No iniciado | Requiere setup |
| N8N schema knowledge | ✅ Documentación pública | JSON format is documented |

## Technical Considerations

### N8N JSON Format

```json
{
  "nodes": [
    {
      "parameters": { "path": "webhook" },
      "type": "n8n-nodes-base.webhook",
      "name": "Webhook",
      "position": [250, 300]
    },
    {
      "parameters": { "method": "GET", "url": "https://api.example.com" },
      "type": "n8n-nodes-base.httpRequest",
      "name": "HTTP Request",
      "position": [450, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{ "node": "HTTP Request", "type": "main", "index": 0 }]]
    }
  }
}
```

### Analysis Logic

```python
class N8NAnalyzer:
    NODE_TYPE_TO_AGENT = {
        "n8n-nodes-base.webhook": "webhook-receiver",
        "n8n-nodes-base.httpRequest": "api-client",
        "n8n-nodes-base.code": "script-executor",
        # ... 50+ mappings
    }

    def analyze_workflow(self, n8n_json: dict) -> MigrationPlan:
        agents = []
        connections = []

        for node in n8n_json["nodes"]:
            agent_type = self.NODE_TYPE_TO_AGENT.get(node["type"])
            if agent_type:
                agents.append(AgentSpec(
                    name=agent_type,
                    config=node["parameters"]
                ))

        for source, targets in n8n_json["connections"].items():
            for target in targets:
                connections.append(Connection(
                    from_agent=source,
                    to_agent=target["node"]
                ))

        return MigrationPlan(agents=agents, connections=connections)
```

## Roadmap

```
Phase 0 (1 week): Concierge MVP
├── Manual analysis via Slack/Discord
├── 3-5 LATAM clients share N8N JSONs
├── Measure: ¿Used? ¿Time savings? ¿Would pay?
└── Go/No-Go: ≥40% "very disappointed" if removed

Phase 1 (2 weeks): CLI Standalone
├── `mm migrate analyze n8n-export.json`
├── Output: List of agents + DAG recommendation
├── NO WhatsApp yet (validate utility first)
└── Target: Technical users (implementers)

Phase 2 (2 weeks): Dashboard Chat
├── Embedded chat in War Room
├── File upload UI (drag-drop)
├── Real-time analysis streaming
└── Target: All users

Phase 3 (2 weeks): WhatsApp Integration
├── Send N8N JSON via WhatsApp
├── Receive analysis on mobile
└── Target: Mobile-first users

Phase 4 (Future): Auto-Creation
├── "¿Querés que los cree ahora? (responde 'sí')"
├── Automatically create agents
└── One-command migration
```

## Brain Evaluations Summary

### Brain #1 (Product Strategy) — 🔶 75%
✅ **Lo mejor:** Único chat-only superpower REAL
⚠️ **Falta:** Validación de demanda LATAM
🚨 **Peligro:** One-time use por cliente = baja frecuencia
💭 **Sugerencia:** Concierge MVP FIRST

### Brain #2 (UX Research) — 🔶 70%
✅ **Lo mejor:** Jakob's Law + mobile-first
⚠️ **Falta:** Descubribilidad strategy
💭 **Sugerencia:** First-run message con ejemplo de N8N export

### Brain #4 (Frontend) — 🔶 72%
✅ **Lo mejor:** Web Worker para parsing (no bloquear UI)
⚠️ **Falta:** File upload component spec
💭 **Sugerencia:** React-virtuoso para workflows grandes (100+ nodos)

### Brain #5 (Backend) — 🔶 74%
✅ **Lo mejor:** PostgreSQL BYTEA para 10MB JSONs
⚠️ **Falta:** Safe JSON parsing (size/depth limits)
💭 **Sugerencia:** S3 para 50MB+ workflows (Phase 2+)

### Brain #7 (Growth) — ✅ 80%
✅ **Winner:** PRIORIDAD sobre otros casos
✅ **Rationale:** Valor REAL, diferenciación clara, ROI medible
⚠️ **Condición:** Concierge MVP mandatory

## Final Veredict

**🔶 CONDITIONAL_APPROVAL** — 75% confidence

**Condiciones para APPROVAL:**

1. **[BLOCKER] Concierge MVP (1 week) FIRST**
   - 3-5 LATAM clients share N8N JSONs
   - Manual analysis via Slack/Discord
   - ≥40% "very disappointed if removed" → BUILD

2. **[BLOCKER] Validate technical feasibility**
   - Parse 10 real N8N exports
   - Confirm schema stability
   - Document edge cases

3. **[CONDITION] Start with CLI (Phase 1)**
   - NO WhatsApp in Phase 1
   - Validate utility with technical users
   - WhatsApp = Phase 3 (only if CLI validates)

**Si Concierge MVP pasa:**
→ Crear `PROP-002-A-implementation-plan.md`
→ Roadmap: CLI → Dashboard → WhatsApp → Auto-creation

**Si Concierge MVP falla:**
→ Archivar como "Validated need but insufficient demand"
→ Ahorro: 6-8 semanas de desarrollo

---

**Propuesta creada:** 2026-04-06
**Creado por:** Rafael Padrón (via /mm:propose)
**Estado:** READY FOR CONCIERGE MVP
**Next action:** Ejecutar Phase 0 (1 week manual test)
