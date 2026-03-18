# TEST-02: Borderline Brief - HabitFlow v1

> **Tipo de Test:** Validation Only
> **Veredicto Esperado:** CONDITIONAL (score: 60-79)
> **Cerebros Involucrados:** #1 (Product Strategy) → #7 (Evaluator)
> **Características:**
> - Problema definido pero sin profundidad suficiente
> - Evidencia presente pero limitada
> - Métricas mezcladas (algunas accionables, otras vanity)
> - Análisis de competencia básico
> - Timeline sin baseline histórico
> - Sin pre-mortem estructurado

---

## El Problema

Los profesionales que trabajan desde casa luchan por mantener hábitos saludables. La falta de estructura del entorno remoto hace difícil:
- Recordar cuándo tomar descansos
- Mantener rutinas de ejercicio
- Hidratarse regularmente
- Dormir lo suficiente

Estos problemas generan:
- Burnout (76% de trabajadores remotos reportan síntomas)
- Baja productividad después de las 14:00
- Problemas de salud a largo plazo

## Audiencia

**Profesionales knowledge workers de 25-40 años** que trabajan remoto ≥3 días por semana.

**Segmentación:**
- 60% Tech/Software
- 25% Creative/Marketing
- 15% Consultores/Freelancers

**Pain points identificados:**
- "Pierdo la noción del tiempo" (89%)
- "Olvido hidratarme" (76%)
- "No tengo rutina clara" (71%)

## Evidencia de Demanda

### Entrevistas (15 usuarios)

> *"Trabajo 8 horas seguidas y al final me doy cuenta de que no comí nada"* — Ana, 29, Dev

> *"Empecé a poner alarmas pero las ignoraba. Necesito algo más inteligente"* — Carlos, 34, PM

> *"El problema no es recordar, es motivarme. Sé que tengo que hacer ejercicio pero no lo hago"* — María, 27, Designer

### Datos de mercado

- Apps de productividad: $49B market size (CAGR 12%)
- Wellness apps: 220M+ downloads en 2024
- 58% de trabajadores remotos usan alguna app de rutina

### Survey propio (n=87)

| Problema | % que lo reporta |
|----------|------------------|
| Olvidar descansos | 89% |
| Deshidratación | 76% |
| Falta de rutina | 71% |
| Dolor físico (espalda) | 64% |
| Sobretrabajo | 58% |

## Competencia

| App | Enfoque | Limitación |
|-----|---------|------------|
| Notion | Productividad general | Demasiado complejo para hábitos simples |
| Forest | Gamificación | Solo para focus, no para hábitos de salud |
| Habitica | Gamificación completa | Curva de aprendizaje alta |
| Drink Water | Hábito único | Solo hidratación |
| Stretchly | Descansos | Solo para pantalla, no personalizado |

**Nuestra diferencia:** Hábitos contextualizados + inteligencia + simplicidad

## La Solución

**HabitFlow** es una app que:

1. **Detecta tu contexto** (reunión, focus time, descanso)
2. **Sugiere micro-hábitos** relevantes al momento
3. **Se adapta** a tu comportamiento real
4. **Te motiva** con progreso visible

**Features iniciales:**
- Recordatorios inteligentes (no fijos)
- Tracker de hábitos con streaks
- Integración con calendar (respetar reuniones)
- Insights semanales
- Modo "deep work" (silenciar todo)

## Modelo de Negocio

**Freemium:**
- **Gratis:** 3 hábitos, insights básicos
- **Premium ($4.99/mes):** Hábitos ilimitados, insights avanzados, integraciones
- **Team ($9.99/user/mes):** Leaderboard team, challenges grupales

## Métricas de Éxito

### Primeros 3 meses (post-launch)

| Métrica | Meta |
|---------|------|
| Downloads | 5,000 |
| DAU/MAU | ≥30% |
| Retención D7 | ≥40% |
| Retención D30 | ≥20% |
| Conversión a premium | ≥3% |
| NPS | ≥40 |

### 6 meses

| Métrica | Meta |
|---------|------|
| MAU | 20,000 |
| MRR | $3,000 |
| Viral coefficient (K-factor) | ≥0.5 |

## Tecnología

**MVP:**
- **Frontend:** React Native (iOS primero)
- **Backend:** Supabase (auth + database + realtime)
- **Push:** OneSignal
- **Analytics:** Mixpanel

**Post-MVP:**
- Android
- Apple Watch
- Slack integration

## Timeline

| Fase | Duración | Hitos |
|------|----------|-------|
| **Discovery adicional** | 2 semanas | 10 entrevistas más + landing page test |
| **Design MVP** | 3 semanas | Figma completo + user tests |
| **Development** | 6 semanas | iOS app funcional |
| **Beta testing** | 2 semanas | 50 usuarios, feedback loops |
| **Launch** | 1 semana | App Store submission |
| **Post-launch** | 4 semanas | Iteración basada en datos |

**Total:** ~4 meses hasta launch

**Baselines para estimación:**
- Apps similares: 3-6 meses desarrollo
- Team size: 1 full-time dev + part-time designer
- Risk buffer: 20% sobre estimaciones

## Adquisición Inicial

**Canal 1:** Product Hunt + IndieHackers
**Canal 2:** Twitter/X (build in public)
**Canal 3:** Comunidades de remote work (Slack/Discord)
**Canal 4:** SEO (keywords: "remote work habits")

**Meta:** 500 early adopters en primer mes

---

## Riesgos

1. **Acquisition cost:** Si CPC es alto, puede ser costoso
2. **Retention:** Si la app no se sticky, churn será alto
3. **Competition:** Notion podría agregar esto como feature

## Next Steps para validación adicional

1. **Landing page test** → Medir interés real (email capture)
2. **Wizard of Oz test** → Validar si el problema es real con manual approach
3. **Competitor deep dive** → Entender por qué apps similares no lo resolvieron

---

**NOTA PARA EL EVALUADOR:** Este brief tiene PUNTOS POSITIVOS y PUNTOS A MEJORAR:

**✅ Positivo:**
- Problema claramente definido
- Evidencia cuantitativa (surveys, datos de mercado)
- Segmentación de audiencia
- Análisis de competencia con tabla comparativa
- Métricas accionables mezcladas (DAU/MAU, retención)
- Timeline con baseline (aunque básico)
- Riesgos identificados

**⚠️ A mejorar:**
- Sin pre-mortem estructurado (¿qué podría fallar?)
- Métricas vanity mezcladas ("downloads" sin contexto)
- Timeline sin buffer para contingencias
- Sin análisis de unit economics (CAC vs LTV)
- Evidencia de demanda limitada (15 entrevistas, 87 surveys)
- Sin consideración de switching costs desde apps existentes
- Análisis de competencia superficial (no se estudian sus fortalezas)
- Sin pruebas de hipótesis clave (¿la gente quiere otra app?)
- Go-to-market strategy básica
- Sin consideration de seasonality (lanzamiento vs vacaciones)

**Score esperado:** 60-75 (CONDITIONAL)
**Feedback esperado:** "Validar problemas X, Y, Z antes de continuar"
