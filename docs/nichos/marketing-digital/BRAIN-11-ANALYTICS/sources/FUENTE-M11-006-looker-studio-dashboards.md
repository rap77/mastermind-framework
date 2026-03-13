---
source_id: "FUENTE-M11-006"
brain: "brain-marketing-11-analytics"
niche: "marketing-digital"
title: "Marketing Dashboards with Looker Studio: From Data to Decisions"
author: "Google Looker Studio Team"
expert_id: "EXP-M11-006"
type: "guide"
language: "en"
year: 2023
isbn: null
url: "https://support.google.com/looker-studio/"
skills_covered: ["H3", "H5", "H7"]
distillation_date: "2026-03-12"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-12"
changelog:
  - version: "1.0.0"
    date: "2026-03-12"
    changes:
      - "Ficha creada con destilación completa"
status: "active"

habilidad_primaria: "Marketing dashboards con Looker Studio para reporting y decisiones"
habilidad_secundaria: "Data visualization, conectores, storytelling con datos"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — Looker Studio (ex Data Studio) es el estándar gratuito para marketing dashboards. Su integración nativa con GA4, Google Ads, Search Console y BigQuery lo convierte en la herramienta de reporting más accesible para equipos de marketing."
---

# FUENTE-M11-006: Marketing Dashboards con Looker Studio

## Tesis Central

> **"Un dashboard que nadie entiende o usa no es analytics — es decoración. El objetivo de cualquier dashboard de marketing es reducir el tiempo entre 'tenemos un problema' y 'tomamos una decisión'. Si el dashboard no acelera esa decisión, está mal diseñado."**

---

## 1. Principios Fundamentales

### Los 3 tipos de dashboards de marketing

1. **Executive Dashboard:** KPIs de negocio, tendencias mensuales, comparación vs. target
   - Audiencia: CMO, CEO, board
   - Frecuencia de revisión: Semanal/mensual
   - Máximo 5-7 KPIs

2. **Operational Dashboard:** Métricas por canal, performance de campaña, alertas
   - Audiencia: Marketing managers, analistas
   - Frecuencia: Diaria
   - Máximo 10-15 métricas

3. **Deep-Dive Report:** Análisis de causa raíz, segmentación, cohorts
   - Audiencia: Analistas, PMs
   - Frecuencia: Según necesidad
   - Sin límite de métricas (es análisis, no dashboard)

*Fuente: Looker Studio, "Dashboard Best Practices" (2023)*

### Principios de data visualization para marketing

1. **Contexto siempre:** Toda métrica necesita comparación (vs. período anterior, vs. target, vs. benchmark)
2. **Jerarquía visual:** Las métricas más importantes deben ser visualmente prominentes
3. **El tipo correcto de gráfico:**
   - Tendencia temporal → Line chart
   - Comparación entre categorías → Bar chart
   - Parte de un todo → Donut/Pie (solo si < 5 segmentos)
   - Correlación → Scatter plot
   - Distribución → Histogram

*Fuente: Looker Studio, "Visualization Guide" (2023)*

---

## 2. Frameworks y Metodologías

### Framework: El Marketing Dashboard Stack

```
LAYER 1: DATA SOURCES
├── GA4 (web analytics)
├── Google Ads / Meta Ads / LinkedIn Ads
├── Search Console (SEO)
├── CRM (HubSpot/Salesforce)
└── Custom BigQuery queries

LAYER 2: DATA BLENDING (Looker Studio)
├── Conectar fuentes múltiples
├── Crear métricas calculadas (ROAS, CPA, CLTV)
└── Filtros y segmentos compartidos

LAYER 3: DASHBOARDS
├── Executive view
├── Channel-specific views
└── Funnel analysis
```

*Fuente: Looker Studio, "Architecture Guide" (2023)*

### Framework: Marketing KPI Scorecards en Looker Studio

Estructura recomendada para scorecard ejecutivo:

```
┌─────────────────────────────────────────┐
│  Revenue Atribuido a Marketing          │
│  €125,430    ▲ +12% vs mes anterior     │
├──────────────┬──────────────────────────┤
│  ROAS        │  CPA                     │
│  4.2x ▲+0.3x│  €34.20 ▼-€2.10         │
├──────────────┼──────────────────────────┤
│  Leads       │  Conv. Rate              │
│  1,234 ▲+8% │  3.4% ▲+0.2%            │
└──────────────┴──────────────────────────┘
```

*Fuente: Looker Studio, "Scorecard Templates" (2023)*

### Conectores esenciales para marketing

| Conector | Datos | Gratuito |
|----------|-------|---------|
| GA4 | Web analytics, conversiones | ✅ |
| Google Ads | Campaña, ad group, keyword | ✅ |
| Search Console | SEO, queries, positions | ✅ |
| BigQuery | Cualquier dato custom | ✅ |
| Meta Ads | Facebook/Instagram ads | Via connector marketplace |
| HubSpot | CRM, deals, pipeline | Via connector |
| Klaviyo | Email metrics | Via connector |

*Fuente: Looker Studio, "Connector Directory" (2023)*

---

## 3. Modelos Mentales

### "El dashboard debe contar una historia"

Los mejores dashboards tienen una narrativa: ¿qué pasó esta semana? ¿por qué? ¿qué hacemos al respecto? No son colecciones de números — son respuestas a preguntas de negocio.

*Fuente: Looker Studio, "Data Storytelling" (2023)*

### "Less is more en dashboards ejecutivos"

Un dashboard con 40 métricas para el CEO es peor que ningún dashboard. La restricción de 5-7 KPIs fuerza la priorización de lo que realmente importa.

*Fuente: Looker Studio, "Executive Dashboards" (2023)*

---

## 4. Criterios de Decisión

### Looker Studio vs. Tableau vs. Power BI

| Herramienta | Cuándo elegir | Costo | Curva de aprendizaje |
|-------------|---------------|-------|---------------------|
| **Looker Studio** | Stack de Google, presupuesto limitado | Gratis | Baja |
| **Tableau** | Análisis visual avanzado, datos complejos | Alto | Media-Alta |
| **Power BI** | Stack Microsoft (Office 365, Azure) | Medio | Media |
| **Metabase** | Datos en propia DB, equipo técnico | Gratuito/self-hosted | Media |

*Fuente: Marketing analytics community benchmarks (2023)*

---

## 5. Anti-patrones

### Anti-patrón: Dashboard que tarda más de 30 segundos en cargar

Un dashboard lento no se usa. Si Looker Studio tarda > 15 segundos, optimizar: reducir rango de fechas por defecto, usar extract data sources, cachear queries pesadas.

*Fuente: Looker Studio, "Performance Optimization" (2023)*

### Anti-patrón: Una sola fuente de datos para todas las métricas

Tener revenue de Google Analytics y no validarlo contra el CRM o el sistema de facturación garantiza discrepancias que generan confusión en los reportes ejecutivos.

*Fuente: Looker Studio, "Data Accuracy" (2023)*

### Anti-patrón: Dashboards sin dueño

Un dashboard que nadie es responsable de mantener se desactualiza en semanas. Asignar un owner con tiempo dedicado a mantenerlo actualizado y relevante.

*Fuente: Looker Studio, "Dashboard Governance" (2023)*
