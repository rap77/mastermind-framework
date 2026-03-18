# TEST-03: Good Brief - StudySync v2 (Iterado)

> **Tipo de Test:** Validation Only
> **Veredicto Esperado:** APPROVE (score: 80-100)
> **Cerebros Involucrados:** #1 (Product Strategy) → #7 (Evaluator)
> **Características:**
> - Problema claro y específico
> - Evidencia de demanda real (entrevistas, datos, experimentos)
> - Métricas accionables con baseline
> - Pre-mortem estructurado
> - Análisis de competencia profundo
> - Timeline realista con buffer
> - Unit economics validados
> - Go-to-market strategy detallada

---

## Contexto: Segunda Iteración

Este brief es la **segunda iteración** basada en feedback del Brain #7. La versión inicial (v1) fue rechazada con score 45/100 por:
- Evidencia insuficiente
- Sin validación de willingness to pay
- Competencia mal analizada

Esta versión (v2) incorpora todo el feedback.

---

## El Problema

**Estudiantes universitarios (18-24 años) en España necesitan coordinar trabajos grupales**, pero las herramientas actuales no están diseñadas para contextos académicos.

### Jobs-to-be-Done

1. **Coordinar tareas** sin spammar al grupo
2. **Hacer seguimiento** de quién hace qué
3. **Reunirse virtualmente** con agenda clara
4. **Entregar proyectos** con versionado simple
5. **Comunicarse** sin mezclar canales (WhatsApp personal vs académico)

### Pain Points (validados con 45 entrevistas)

| Pain Point | Frecuencia | Severidad (1-5) |
|------------|------------|-----------------|
| "No sé quién hace qué" | 89% | 4.7 |
| "El grupo es desorganizado" | 82% | 4.5 |
| "Usamos WhatsApp y se pierde todo" | 78% | 4.3 |
| "Alguien siempre no entrega" | 71% | 4.8 |
| "No tenemos buen lugar para reunirnos" | 64% | 3.9 |
| "No sé cómo contactar a un compañero" | 53% | 3.5 |

### Impacto

- **24% de proyectos** reciben calificación más baja por problemas de coordinación (no de contenido)
- **Stress promedio:** 7.2/10 durante semanas de entrega
- **Horas perdidas:** 6.8h/estudiante por proyecto en coordinación ineficiente

---

## Audiencia

### Primaria (Beachhead Market)
**Estudiantes de ingeniería/business en universidades públicas de Madrid**
- Tamaño: ~45,000 estudiantes
- Característica: Muchos proyectos grupales por semestre (4-6)
- Pain agudo: Primero/segundo año (menos experiencia organizándose)

### Secundaria (Expansion)
**Resto de estudiantes universitarios en España**
- Tamaño: ~800,000 estudiantes
- Expansión: Año 2 después de validar en beachhead

### Persona: María (22)

- **Quién:** Estudiante de 3er año de Ingeniería Informática, UPM
- **Situación:** 5 asignaturas con proyectos grupales este semestre
- **Pain:** "Perdí las 24 horas antes de una entrega porque una compañera no avisó que no iba a hacer su parte"
- **Motivación:** "Quiero pasar las asignaturas pero sin estrés innecesario"
- **Tech savviness:** Media-alta (usa Discord, Notion, pero le parecen complicados para esto)

---

## Evidencia de Demanda

### 1. Entrevistas (n=45)

**Método:** 30 min semiestructuradas, grabadas y transcritas

**Key insights:**
- 91% prefiere una app dedicada sobre WhatsApp (demasiado ruido)
- 87% está dispuesta a pagar si resuelve el problema "realmente"
- 76% ha tenido al menos un proyecto "roto" por falta de comunicación

**Quotes:**
> *"Si existe algo que me ahorre el estrés de la semana de entrega, pago sin dudar"* — Alberto, 21

> *"WhatsApp es un infierno. Me llegan 50 mensajes y no sé cuáles son importantes"* — Laura, 23

> *"Necesito saber quiénes están en el grupo y cómo contactarlos rápido"* — Diego, 19

### 2. Survey cuantitativo (n=312)

| Pregunta | Resultado |
|----------|-----------|
| ¿Usas WhatsApp para grupos académicos? | 94% |
| ¿Es eficaz? | 23% |
| ¿Estarías dispuesto a usar una app dedicada? | 89% |
| ¿Cuánto pagarías por semestre? | €5-10: 34%, €10-15: 41%, €15+: 25% |
| ¿Cuántos proyectos grupales tienes? | Media: 4.2/semestre |

### 3. Landing Page Test (n=1,200 visitas)

- **Conversión a email:** 18.4% (221 emails captados)
- **Click en "demo":** 34%
- **Tiempo en página:** 2:34 min (promedio)
- **Bounce rate:** 42%

### 4. Wizard of Oz Test (n=12 grupos)

**Experimento:** Usamos Notion + WhatsApp manual simulando la app

**Resultados:**
- 10/12 grupos completaron el proyecto con éxito (vs 6/12 en control)
- Satisfaction score: 8.2/10
- 9/12 grupos dijeron "lo usarían en el futuro"
- **Learning:** Las features más valiosas son (1) asignación de tareas, (2) recordatorios automáticos

### 5. Competitor Deep Dive

| Tool | % que lo usa | Satisfaction (1-10) | Pain principal |
|------|--------------|---------------------|-----------------|
| WhatsApp | 94% | 4.2 | Demasiado ruido |
| Discord | 31% | 6.8 | Curva de aprendizaje |
| Notion | 18% | 7.1 | Demasiado complejo |
| Google Workspace | 67% | 6.3 | No diseñado para grupos académicos |
| Trello | 9% | 7.5 | No incluye chat |

**Gap identificado:** Ninguna herramienta combina (a) gestión de tareas + (b) chat académico + (c) contexto universitario

### 6. Willingness to Pay (Validado)

**Método:** Van Westendorp Price Sensitivity

**Resultados:**
- **Precio óptimo:** €12/semestre
- **Precio máximo aceptable:** €18/semestre
- **Precio mínimo de calidad:** €8/semestre

**Unit Economics (post-experimento):**
- **CAC estimado:** €4.50 (organic: campus ambassadors)
- **LTV (2 años):** €48 (4 semestres × €12)
- **LTV/CAC:** 10.7x ✅

---

## La Solución: StudySync

**StudySync es una app diseñada específicamente para trabajos grupales universitarios.**

### Core Features

1. **Workspace por proyecto** (invitar por código o email universitario)
2. **Tareas con deadlines** y asignación clara
3. **Chat integrado** (no más WhatsApp mezclado)
4. **Directorio de grupo** (quién es quién y cómo contactar)
5. **Recordatorios automáticos** (24h antes, 1h antes de deadline)
6. **Entrega de archivos** con versionado simple
7. **Calendar de eventos** (reuniones, deadlines)

### Diferenciadores

| Feature | EstudioSync | Competencia |
|---------|-------------|-------------|
| Contexto académico | ✅ Específico para uni | ❌ Genérico |
| Onboarding simple | ✅ < 2 min | ❌ Complejo |
| Integración universidad | ✅ Email uni, calendar | ❌ No |
| Pricing | ✅ Por semestre | ❌ Mensual (caro para estudiantes) |
| Modo offline | ✅ Sync when back online | ❌ No siempre |

### Anti-features (lo que NO haremos)

- ❌ Videoconferencia (usar Zoom/Google Meet existentes)
- ❌ Edición colaborativa de docs (usar Google Docs)
- ❌ Gamificación compleja (distraction)
- ❌ Social network (no es el objetivo)

---

## Modelo de Negocio

### Pricing

| Plan | Precio | Límites |
|------|--------|---------|
| **Free** | €0 | 1 proyecto activo, 5 miembros max |
| **Semestre** | €12 | Proyectos ilimitados |
| **Grupo** | €40 | Hasta 10 miembros (€4/persona) |

### Unit Economics (Target)

| Métrica | Valor |
|---------|-------|
| CAC | €4.50 |
| ARPU (primer año) | €12 |
| LTV (2 años) | €48 |
| LTV/CAC | 10.7x |
| Payback period | < 2 meses |
| Gross margin | >85% (SaaS) |

### Revenue Model (Proyección Año 1)

| Mes | Usuarios pagos | MRR |
|-----|----------------|-----|
| M1 | 100 | €1,200 |
| M3 | 500 | €6,000 |
| M6 | 2,000 | €24,000 |
| M12 | 8,000 | €96,000 |

**Assumptions conservadoras:**
- 15% conversión free → paid
- 80% retención semestre a semestre
- 0.3 viral coefficient (referidos)

---

## Métricas de Éxito

### Primeros 30 días (Post-Launch)

| Métrica | Meta | Nota |
|---------|------|------|
| Signups | 500 | Beachhead market (UPM) |
| DAU/MAU | ≥25% | Engagement mínimo |
| Activación (% que crea 1er proyecto) | ≥60% | Aha! moment |
| Retención D7 | ≥40% | Baseline SaaS |
| Retención D30 | ≥25% | Viabilidad |
| Conversión free→paid | ≥10% | Validación monetización |

### 90 días

| Métrica | Meta | Nota |
|---------|------|------|
| MAU | 2,000 | Expansión a 3 universidades |
| MRR | €12,000 | Unit economics positivo |
| NPS | ≥40 | Salud del producto |
| Referral rate | ≥20% | Crecimiento orgánico |

### 12 meses

| Métrica | Meta |
|---------|------|
| MAU | 10,000 |
| MRR | €100,000 |
| Universidades | 10 |
| Churn mensual | <5% |

---

## Go-to-Market Strategy

### Fase 1: Beachhead (Meses 1-3)

**Target:** 3 facultades de ingeniería en Madrid (UPM, UC3M, URJC)

**Tácticas:**
1. **Campus Ambassadors** (6 estudiantes, €200/mes)
   - Responsabilidad: Presentar app en clases, organizar eventos
   - Meta: 100 signups/mes por ambassador

2. **Profesors partnership**
   - Presentar app a profesores con proyectos grupales
   - Incentivo: Reporting de participación de estudiantes

3. **Flyers en campus** (periódico de resultados)
   - QR code → Landing page → Email capture

4. **WhatsApp communities** (estudiantes de cada facultad)
   - Promoción orgánica por estudiantes

**Meta:** 500 usuarios pagos al final de mes 3

### Fase 2: Expansión Madrid (Meses 4-6)

**Target:** Todas las facultades de Madrid

**Tácticas:**
1. **Student discounts** (10% off si vienen de referral)
2. **Facebook/Instagram Ads** (target: estudiantes 18-24, Madrid)
3. **Partnerships con delegaciones de estudiantes**

**Meta:** 2,000 usuarios pagos al final de mes 6

### Fase 3: Nacional (Meses 7-12)

**Target:** Top 10 universidades de España

**Tácticas:**
1. **Content marketing** (blog sobre productividad estudiantil)
2. **SEO** (keywords: "trabajos grupales", "productividad estudio")
3. **PR** (medios universitarios)

**Meta:** 8,000 usuarios pagos al final de mes 12

---

## Tecnología

### Stack MVP

| Componente | Tecnología | Por qué |
|------------|------------|---------|
| **Frontend** | React Native | iOS + Android con 1 codebase |
| **Backend** | Supabase | Auth, DB, Realtime, Storage incluidos |
| **Push** | OneSignal | Free tier suficiente |
| **Analytics** | Mixpanel | Event tracking simple |
| **Payments** | RevenueCat | Subscription management |
| **Email** | Resend | Transactional emails |

### Costos Mensuales (Estimado)

| Servicio | Costo |
|----------|-------|
| Supabase Pro | €25 |
| OneSignal | €0 (free tier) |
| Mixpanel | €0 (free tier hasta 100k events) |
| RevenueCat | €0 (free tier hasta $10k/mo revenue) |
| Resend | €5 |
| **Total** | **€30/mes** |

---

## Timeline

### Desarrollo

| Fase | Duración | Hitos | Risk Buffer |
|------|----------|-------|-------------|
| **Design completo** | 3 semanas | Figma + user tests (n=8) | +20% |
| **Development MVP** | 8 semanas | Features core funcionales | +25% |
| **Beta testing** | 2 semanas | 50 usuarios reales | +50% (mayor incertidumbre) |
| **Bug fixing + polish** | 1 semana | Lista para App Store | +20% |
| **Launch** | 1 semana | Submission + approval | +100% (App Store impredecible) |

**Total base:** 15 semanas
**Total con buffers:** 19.5 semanas (~4.5 meses)

**Baselines:**
- Apps similares: 3-6 meses (según indie hackers)
- Team: 1 dev full-time + diseñador part-time
- Tech stack conocido (React Native + Supabase)

### Milestones

- **Mes 2:** Beta lista, 50 usuarios test
- **Mes 3:** Soft launch (UPM solamente)
- **Mes 4:** Hard launch (Madrid completa)
- **Mes 6:** Expansión nacional
- **Mes 12:** 10 universidades, €100k MRR

---

## Pre-Mortem: ¿Qué podría fallar?

### Escenario 1: No conseguimos usuarios (Probabilidad: 30%)

**Señales:**
- <50 signups en primer mes
- Landing page conversion <5%
- Ambassadors no consiguen presentaciones

**Mitigation:**
- Si M1 <50 signups → Pivot a B2B (vender a universidades)
- Si conversion <5% → Rediseñar landing page con nuevo messaging
- Si ambassadors fallan → Cambiar a Facebook Ads

### Escenario 2: Usuarios no pagan (Probabilidad: 25%)

**Señales:**
- Conversión free→paid <5% (vs 10% target)
- Churn primer mes >40%

**Mitigation:**
- Introducir trial de 7 días (vs free limitado)
- Reducir precio a €8/semestre
- Aumentar valor perceived con más features

### Escenario 3: Competencia reacciona (Probabilidad: 15%)

**Señales:**
- WhatsApp lanza feature de "groups for projects"
- Notion lanza "student plan" con academic features

**Mitigation:**
- Diferenciación por integración universitaria (no es copiable rápidamente)
- Partnership exclusivas con universidades

### Escenario 4: Tech no escala (Probabilidad: 10%)

**Señales:**
- Supabase crashes con >1k concurrent users
- Push notifications delays >5min

**Mitigation:**
- Migrar a backend propio (Node.js + PostgreSQL)
- Cambiar de OneSignal a Firebase Cloud Messaging

### Escenario 5: Seasonality mata retention (Probabilidad: 20%)

**Señales:**
- 80% churn después de exámenes
- No reactivan en semestre siguiente

**Mitigation:**
- Features para "entre semestres" (planificación, buscar compañeros)
- Gamificación light para mantener engagement

---

## Competencia (Análisis Profundo)

### Directa

| Competidor | Fortalezas | Debilidades | Nuestra respuesta |
|------------|------------|-------------|-------------------|
| WhatsApp | Todos lo usan | Ruido, sin contexto | Mensaje por proyecto, archive automático |
| Discord | Voice + text | Curva de aprendizaje | Onboarding <2min, UI simple |
| Notion | Flexible | Demasiado complejo | Templates pre-hechos |
| Trello | Visual | Sin chat | Chat integrado + tareas |

### Indirecta

| Competidor | Por qué no es amenaza |
|------------|----------------------|
| Google Workspace | No diseñado para grupos académicos específicos |
| Slack | Demasiado caro para estudiantes ($8/user/mes) |
| Microsoft Teams | Requiere licencia institucional |

### Moat (defensa)

1. **Data network effect:** Más usuarios = mejor matching de compañeros
2. **Integración universitaria:** Calendarios académicos, email .edu
3. **Pricing por semestre:** Alineado con ciclo académico (vs mensual)
4. **Simplicidad:** <2 min onboarding vs complejidad de Notion

---

## Riesgos y Mitigation

| Riesgo | Probabilidad | Impacto | Mitigation |
|--------|--------------|---------|------------|
| CAC más alto que estimado | 30% | Alto | Reducir spend en ads, focus en organic |
| Churn >30% en primer mes | 25% | Alto | Onboarding mejorado, features de retención |
| App Store reject | 15% | Medio | Seguir guidelines a rajatabla |
| Competencia lanza feature similar | 20% | Medio | Moat por integración universitaria |
| Seasonality extrema | 40% | Medio | Features para "entre semestres" |

---

## Análisis de Viabilidad

### Market Size (TAM/SAM/SOM)

| | Estudiantes | ARPU | Revenue |
|--|-------------|------|---------|
| **TAM** (España, todos uni) | 800,000 | €12/año | €9.6M |
| **SAM** (Madrid, grandes) | 200,000 | €12/año | €2.4M |
| **SOM** (Año 1, 10 uni) | 80,000 | €12/año | €960k |

**Nota:** SOM es 80k estudiantes pero target es 8k pagos (10% penetración) = €96k ARR

### Unit Economics Check

✅ **LTV/CAC > 3** (10.7x)
✅ **Payback < 12 meses** (2 meses)
✅ **Gross margin > 80%** (85%)
✅ **CAC < 1/3 LTV** (€4.50 vs €48)

---

## Próximos Pasos Inmediatos

1. **Landing page mejorada** (basada en learnings de v1)
2. **100 entrevistas más** para validar features prioritarias
3. **Figma completo** con user testing
4. **Decisión final** (go/no-go) basada en:
   - Conversión landing page >15%
   - Willingness to pay confirmado
   - Unit economics validados

---

**NOTA PARA EL EVALUADOR:**

Este brief demuestra:

**✅ Problem clarity:** Jobs-to-be-done definidos, pain points cuantificados
**✅ Evidence depth:** Entrevistas (n=45), surveys (n=312), landing page test, Wizard of Oz
**✅ Competitive analysis:** Tablas con fortalezas/debilidades y respuesta estratégica
**✅ Actionable metrics:** DAU/MAU, retención, conversión (no vanity metrics)
**✅ Pre-mortem:** 5 escenarios de fallo con probabilidades y mitigation
**✅ Financial validation:** TAM/SAM/SOM, unit economics, LTV/CAC
**✅ GTM strategy:** Fases claras con tácticas específicas y métricas
**✅ Timeline realistic:** Baselines de apps similares, buffers incluidos
**✅ Risks identified:** Matriz con probabilidad/impacto/mitigation

**Score esperado:** 85-95 (APPROVE)
**Confidence level:** Alta (basada en datos, no asumptions)
