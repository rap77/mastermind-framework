# TEST-MARKETING-04: B2B SaaS Retention & Email Marketing Strategy

> **Tipo de Test:** Retention + Email Marketing + Lifecycle
> **Nicho:** Marketing Digital (16 cerebros M1-M16)
> **Veredicto Esperado:** APPROVE con retention-first mindset
> **Cerebros Involucrados:** M1 (Strategy), M9 (Email), M10 (Retention), M11 (Analytics), M13 (Ops), M15 (Community), M16 (Evaluator)
> **Complejidad:** Media-Alta - Retención es más difícil que adquisición

---

## El Brief (Usuario)

Tenemos un SaaS B2B de email marketing automation para pequeñas empresas (10-100 employees).

**Modelo:**
- **Precio:** $99/mes (up to 5,000 contacts)
- **Billing:** Annual upfront con discount (más común)
- **Avg contract value:** $1,080/year
- **MRR:** $108k (1,000 customers paying)
- **Churn rate:** 5% monthly (¡ALTO! = 60% annual churn)
- **LTV:** ~$1,800 (solo 18 meses avg lifespan)

**Problema principal:** Churn muy alto. Perdemos 50 customers/mes pero solo ganamos 40 nuevos.

**Análisis de churn:**
- 40% no usa el producto después del onboarding (setup complexity)
- 30% "no getting value" (envían pocos emails, no ven resultados)
- 20% price sensitivity (downgrade to cheaper tools o in-house)
- 10% out of business / acquired

**Lo que tenemos:**
- **Email:** Solo monthly newsletter (open rate 15%, click rate 2%)
- **In-app:** Nulo (no messages, prompts, nada)
- **Customer success:** 1 CSM para 1,000 customers (impossible)
- **Community:** Facebook Group con 200 members (ghost town)

**Datos de engagement:**
- 30% de customers log in weekly (activos)
- 50% log in monthly (riesgo de churn)
- 20% no log in por 2+ meses (alto riesgo)

**Objetivos:**
1. Reducir churn de 5% a 3% monthly
2. Aumentar engagement (30% weekly → 50% weekly)
3. Identificar customers en riesgo antes de churn

**Preguntas:**
- ¿Qué email sequences crear?
- ¿Cómo segmentamos para enviar mensajes relevantes?
- ¿Qué métricas predictivas de churn?
- ¿Invertimos en customer success team o herramientas?

---

## Resultados Esperados

### Cerebro M1 (Strategy) debe establecer:
- ✅ Retención es NORTH STAR (no acquisition)
- ✅ Segmentation strategy por health score (green/yellow/red)
- ✅ Resource allocation: CS team vs tools vs automation
- ✅ Quick wins: low-hanging fruit para reducir churn rápido

### Cerebro M9 (Email) debe diseñar sequences:
- ✅ **Onboarding sequence** (días 1-30): Setup completion, time to value
- ✅ **Activation sequence** (días 31-60): First campaign sent, early wins
- ✅ **Nurture sequence** (meses 3-12): Best practices, case studies, tips
- ✅ **Win-back sequence** (risk customers): "We miss you", oferta, survey
- ✅ **Churn prevention** (predictive): Intervención basada en signals

### Cerebro M10 (Retention) debe crear:
- ✅ Lifecycle strategy (onboarding → activation → adoption → expansion → renewal)
- ✅ Health score model (engagement + usage + NPS + payments)
- ✅ Early warning system (qué indicators preceden churn?)
- ✅ Playbook por health tier (green: nurture; yellow: intervene; red: save)

### Cerebro M11 (Analytics) debe implementar:
- ✅ Cohort analysis por month of signup (¿getting worse or better?)
- ✅ Feature usage correlation (¿qué features predicen retention?)
- ✅ Churn prediction model (machine learning o rules-based)
- ✅ Engagement scoring (logins, emails sent, features used)
- ✅ North Star metric: % customers who sent campaign in last 30 days

### Cerebro M13 (Ops) debe integrar:
- ✅ CRM sync (customer health en Salesforce/HubSpot)
- ✅ Automated triggers (health score changes → email/CSM outreach)
- ✅ Data pipeline (product usage → analytics → actions)
- ✅ Tech stack: email tool + in-app + analytics + CRM unified

### Cerebro M15 (Community) debe revitalizar:
- ✅ Community strategy (Facebook Group → Slack/Discord?)
- ✅ User-generated content strategy (customer spotlights)
- ✅ Events (webinars, office hours, training sessions)
- ✅ Advocacy program (referral incentives, case studies)

### Cerebro M16 (Evaluator) debe cuestionar:
- ✅ ¿Onboarding es el root cause? (40% churn por complexity)
- ✅ ¿Product tiene fundamental retention problem? (o es marketing/CS issue?)
- ✅ ¿Pricing model correcto? (annual upfront puede ser barrier)
- ✅ ¿1 CSM para 1,000 customers es viable? (need automation + tiering)

---

## Métricas de Éxito del Test

| Métrica | Esperado | Mínimo Aceptable |
|---------|----------|------------------|
| **Email sequences** | 5+ sequences diseñadas | 3+ sequences |
| **Health score** | Modelo definido | Al menos criterios explícitos |
| **Churn prediction** | Early warning system | Mención de signals |
| **Segmentation** | 3+ segments identificados | Al menos 2 (active/risk) |
| **In-app strategy** | Propuesto (critical) | Mencionado |
| **Community revival** | Plan para ghost town | Al menos acknowledge |
| **Evaluator score** | 80+ | 70+ |

---

## Gaps Esperados (Acceptable)

⚠️ **Producto onboarding no mencionado** - M16 debe señalar (40% churn root cause)
⚠️ **In-app messaging faltante** - M13/M9 deben recomendar
⚠️ **NPS surveys no mencionados** - M11 debe sugerir
⚠️ **Customer tiering faltante** - M1 debe recomendar (no todos customers son iguales)

---

## Anti-patrones que DEBEN ser detectados:

❌ **Solo más emails:** Enviar más sin entender por qué no usan el producto
❌ **Universal messaging:** Same content para todos (segmentación crítica)
❌ **Reactividad:** Esperar a que cancelen para intervenir (demasiado tarde)
❌ **Sin product feedback:** No saber qué features faltan o son confusas
❌ **Descuentos blanket:** Offer discount para retener (short-term fix, long-term problem)
❌ **Ignorar onboarding:** La mayoría del churn pasa en primeros 90 días
❌ **CS team sin herramientas:** 1 CSM para 1,000 customers sin automation es impossible

---

## Notas para el Tester

Este test valida que el orquestador:
1. Identifique que ONBOARDING es root cause de 40% del churn
2. Recomiende in-app messaging (critical para SaaS retention)
3. Use health scores para priorizar CSM time (triage)
4. Combine email + in-app + community (multi-channel retention)
5. Mida cohort retention (¿getting better over time?)

**Resultado esperado:** Estrategia retention-first con onboarding optimization, health scoring, multi-channel lifecycle marketing, y early warning system.
