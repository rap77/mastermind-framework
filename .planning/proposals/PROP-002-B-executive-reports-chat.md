---
id: PROP-002-B
title: "Executive Reports Chat — Mobile-First Financial & KPI Queries"
status: CONDITIONAL_APPROVAL
priority: P2
category: Feature
effort: M
updated: 2026-04-06
part_of: PROP-002-v2 (Multi-Channel Orchestrator)
brain_evaluations:
  brain-01: CONDITIONAL_APPROVAL
  brain-02: CONDITIONAL_APPROVAL
  brain-04: CONDITIONAL_APPROVAL
  brain-05: CONDITIONAL_APPROVAL
  brain_07: DEFERRED_UNTIL_A
final_verdict: CONDITIONAL_APPROVAL
consensus: Valid use case BUT low frequency (1x/month) — Email alerts FIRST, WhatsApp later
confidence: 55%
next_condition: "PROP-002-A (Migration) validates demand → THEN reconsider"
---

# Propuesta: Executive Reports Chat

## Problema Identificado

**Caso de uso:** CEO necesita información financiera URGENTE antes de reunión con inversores/gerencia.

**Problema actual:**
- Dashboard NO es mobile-first
- Requiere abrir laptop, loguearse, navegar 4 pantallas
- "Dame el dato YA" toma 5-10 minutos
- Reunión en 15 minutos → estrés

**Solución:**
- WhatsApp query: "Envíame reporte de gastos del mes"
- Respuesta en segundos: Reporte ejecutivo formateado
- Mobile, asíncrono, fuera del dashboard

## Por qué es Mobile-Only (no Chat-Only)

Este caso NO es "chat-only superpower" porque:
- **Email alerts también sirven** (mismo valor, diferente canal)
- **SMS alerts también sirven** (pero más caros)
- **Push notifications también sirven** (requieren app)

**Chat es conveniente PERO no único.**

## Casos de Uso

### Caso 1: Reporte Financiero Urgente

```
Contexto: CEO en Uber, 15 min antes de reunión
Input (WhatsApp): "Envíame gastos del mes"

Output (WhatsApp):
"📊 Reporte de Gastos — Abril 2026

Total: $15,430
├── Marketing: $5,200 (33.7%)
├── Infraestructura: $4,100 (26.6%)
├── Salarios: $4,500 (29.2%)
└── Otros: $1,630 (10.5%)

📈 vs mes anterior: +8.2%
⚠️ Alerta: Marketing está 15% sobre presupuesto

[Ver dashboard completo → link]"

Time to value: 10 segundos (vs 5-10 minutos en dashboard)
```

### Caso 2: KPIs Ejecutivos

```
Input: "¿Cuál es el MRR actual?"

Output:
"💰 MRR — Abril 2026

MRR: $42,590
📈 vs mes anterior: +12.3%
🎯 Target: $50,000
📊 Gap: $7,410 (85.2% del target)

Top 3 planes:
├── Enterprise: $25,000 (58.7%)
├── Business: $12,500 (29.3%)
└── Starter: $5,090 (11.9%)
"
```

### Caso 3: Alertas Críticas

```
Input: "¿Hay problemas en producción?"

Output:
"🚨 Production Status — NOW

❌ 1 incidente activo:
├── API Gateway: 503 errors ↑ 300%
├── Started: 5 min ago
└── Team notified: @devops

✅ Systems operational:
├── Database: OK
├── Redis: OK
└── Workers: OK"
```

## Target Users

| Role | Frecuencia | Pain Point | Value Prop |
|------|-----------|------------|------------|
| **CEO** | 1-4x/mes (reuniones) | "No tengo laptop en el momento" | "Tengo el dato en segundos por WhatsApp" |
| **CFO** | 1-2x/mes (board meetings) | "Necesito número exacto YA" | "Número exacto + contexto vs anterior" |
| **VP Marketing** | 1-2x/mes (reviews) | "¿Cuánto gastamos este mes?" | "Desglose por categoría + alertas" |

## Contexto

- **Proyecto:** MasterMind v3.0 — Enterprise agent orchestration platform
- **Stack:** Next.js 16 + React 19 + Python FastAPI + Rust Control Plane
- **Referencia:** Paperclip NO tiene reportes ejecutivos mobile
- **Competencia:** Dashboards existentes NO son mobile-first

## Scope MVP (v3.0)

### Incluye

✅ **Email alerts FIRST (Phase 1)**
   - Scheduled reports (daily/weekly/monthly)
   - Trigger-based alerts (KPI thresholds)
   - Mobile-friendly HTML emails

✅ **3 templates de reportes:**
   - Financial Summary (gastos, ingresos)
   - KPIs Ejecutivos (MRR, churn, LTV)
   - System Health (uptime, errors, performance)

✅ **Role-Based Filtering**
   - CEO: Todo
   - VP: Solo su área
   - Manager: Resumen ejecutivo

### No incluye (Phase 2+)

❌ WhatsApp integration (Phase 2 — only if email validates demand)
❌ Ad-hoc queries (Phase 2)
❌ Interactive chat (Phase 3)
❌ Voice responses (Phase 4+)

## Success Metrics

### Phase 1 (Email Alerts)

| Métrica | Target | ¿Cómo medir? |
|---------|--------|--------------|
| **Open rate** | 60%+ | Email tracking |
| **Click rate** | 20%+ | Link tracking |
| **Forward rate** | 10%+ | "Share with team" |
| **Unsubscribe rate** | <5% | Email preferences |
| **Satisfaction** | 4.0+/5.0 | Post-send survey |

### Business Impact

| Métrica | Baseline | Target | ROI |
|---------|----------|--------|-----|
| **Time to insight** | 5-10 min | <30 sec | **90% reduction** |
| **Stress before meetings** | High | Low | Qualitative |
| **Decision speed** | Days | Hours | Competitive advantage |

## Open Questions

1. **Frequency validation:** ¿Es REALMENTE 1x/mes? ¿O menos?
2. **Email vs WhatsApp:** ¿Prefieren email programado o WhatsApp on-demand?
3. **Format preference:** ¿PDF? ¿HTML? ¿Plain text?
4. **Delivery timing:** ¿Qué día/hora? ¿Timezones?

## Dependencies

| Dependencia | Estado | Nota |
|-------------|--------|------|
| PROP-002-A (Migration) | ⏸️ Bloqueante | Validar chat demand FIRST |
| Report generation engine | ✅ EXISTS | AnalyticsService (Phase 14) |
| Email service | ❌ No iniciado | SendGrid/AWS SES/Postmark |
| WhatsApp Business API | ❌ No iniciado | Phase 2 only |

## Technical Considerations

### Email Template (HTML)

```html
<!DOCTYPE html>
<html>
<body>
  <h1>📊 Reporte de Gastos — Abril 2026</h1>

  <table>
    <tr><td>Total:</td><td>$15,430</td></tr>
    <tr><td>Marketing:</td><td>$5,200 (33.7%)</td></tr>
    <tr><td>Infraestructura:</td><td>$4,100 (26.6%)</td></tr>
    <tr><td>Salarios:</td><td>$4,500 (29.2%)</td></tr>
    <tr><td>Otros:</td><td>$1,630 (10.5%)</td></tr>
  </table>

  <p>📈 vs mes anterior: <strong>+8.2%</strong></p>
  <p>⚠️ <strong>Alerta:</strong> Marketing está 15% sobre presupuesto</p>

  <a href="https://dashboard.mastermind.io/reports/expenses">
    Ver dashboard completo →
  </a>
</body>
</html>
```

### Scheduled Reports (Cron)

```python
# Python (FastAPI background tasks)
@app.on_event("startup")
async def schedule_executive_reports():
    scheduler.add_job(
        send_executive_report,
        "cron",
        day=1,  # 1st of month
        hour=8,  # 8 AM
        args=["financial", user_id]
    )
```

## Roadmap

```
Phase 0 (1 week): Validation
├── Interview 5 CEOs/CFOs
├── Ask: "¿Cómo obtenés info financiera hoy?"
├── Ask: "¿Prefieres email programado o WhatsApp on-demand?"
└── Decision: Go/No-Go based on demand

Phase 1 (2 weeks): Email Alerts
├── Implement 3 report templates
├── Email service integration (SendGrid/SES)
├── Scheduled reports (daily/weekly/monthly)
├── Role-based filtering
└── Target: Validate utility FIRST

Phase 2 (IF Phase 1 validates): WhatsApp Integration
├── WhatsApp Business API setup
├── On-demand queries via WhatsApp
├── Response caching (same query = cached response)
└── Target: Mobile-first users

Phase 3 (Future): Interactive Chat
├── Follow-up questions: "¿Desglose por campaña?"
├── Drill-down capabilities
└── AI-powered insights
```

## Brain Evaluations Summary

### Brain #1 (Product Strategy) — 🔶 55%
✅ **Lo mejor:** Caso de uso válido
⚠️ **Falta:** Evidencia de frecuencia real
🚨 **Peligro:** 1x/mes = ROI bajo para infraestructura de chat
💭 **Sugerencia:** Email FIRST, WhatsApp AFTER

### Brain #2 (UX Research) — 🔶 60%
✅ **Lo mejor:** Mobile-first alineado con LATAM
⚠️ **Falta:** ¿Prefieren email o WhatsApp?
💭 **Sugerencia:** A/B test email vs WhatsApp

### Brain #4 (Frontend) — 🔶 65%
✅ **Lo mejor:** Email templates simples (no chat UI needed)
⚠️ **Falta:** Responsive design para mobile
💭 **Sugerencia:** MJML for email templates

### Brain #5 (Backend) — 🔶 62%
✅ **Lo mejor:** Email service es simple (barato)
⚠️ **Falta:** Delivery timing strategy
💭 **Sugerencia:** SendGrid (velocidad) > AWS SES (complejo)

### Brain #7 (Growth) — 🔄 50%
🔄 **DEFERRED:** Priority = Migration Analysis (PROP-002-A)
✅ **Rationale:** Low frequency = low ROI
⚠️ **Condición:** Reconsider AFTER PROP-002-A validates demand

## Final Veredict

**🔶 CONDITIONAL_APPROVAL** — 55% confidence

**Condiciones para APPROVAL:**

1. **[BLOCKER] PROP-002-A validates demand FIRST**
   - Si Migration Analysis NO valida demanda → Esta propuesta TAMPOCO tiene sentido
   - Si Migration Analysis VALIDA → Recién considerar chat infrastructure

2. **[BLOCKER] Email FIRST (Phase 1)**
   - NO WhatsApp en Phase 1
   - Validar si email programado es suficiente
   - Si email NO se usa → WhatsApp TAMPOCO se usará

3. **[CONDITION] Validate frequency with interviews**
   - Talk to 5 CEOs/CFOs
   - "¿Cuántas veces por mes necesitás esto?"
   - If <2x/month → NOT WORTH building

4. **[CONDITION] A/B test delivery channels**
   - Group A: Email programado
   - Group B: WhatsApp on-demand
   - Measure: Open rate, satisfaction, preference

**Si condiciones se cumplen:**
→ Email alerts FIRST (low cost, validate utility)
→ WhatsApp AFTER (if email validates demand)

**Si condiciones NO se cumplen:**
→ Archivar como "Nice to have but low priority"
→ Ahorro: 4-6 semanas de desarrollo

---

**Propuesta creada:** 2026-04-06
**Creado por:** Rafael Padrón (via /mm:propose)
**Estado:** DEFERRED UNTIL PROP-002-A
**Next action:** Esperar resultado de Concierge MVP (PROP-002-A)
