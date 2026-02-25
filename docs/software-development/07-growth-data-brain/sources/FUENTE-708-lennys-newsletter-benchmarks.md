---
source_id: FUENTE-708
brain: brain-software-07-growth-data
niche: software-development
title: Lenny's Newsletter — Compilación de Benchmarks de Producto
author: Lenny Rachitsky
expert_id: N/A
type: article_compilation
language: en
year: 2022-2025
isbn: N/A
url: https://www.lennysnewsletter.com/
skills_covered:
- HG4
version: 1.0.1
last_updated: '2026-02-25'
changelog:
- 'v1.0.0: Destilación inicial — benchmarks clave extraídos'
- version: 1.0.1
  date: '2026-02-25'
  changes:
  - 'Cargada en NotebookLM (Cerebro #7 Growth & Data)'
  - 'Notebook ID: d8de74d6-7028-44ed-b4d5-784d6a9256e6'
status: active
distillation_date: '2026-02-23'
distillation_quality: complete
loaded_in_notebook: true
---


# FUENTE-708: Lenny's Newsletter — Benchmarks de Producto

## Datos de la Fuente

| Campo | Valor |
|-------|-------|
| **Autor** | Lenny Rachitsky (ex-PM Airbnb) |
| **Tipo** | Compilación de artículos de newsletter |
| **URL** | https://www.lennysnewsletter.com/ |
| **Período** | 2022-2025 |
| **Formato** | Selección de artículos con datos cuantitativos |

## Habilidades que Cubre

| ID | Habilidad | Nivel de Cobertura |
|----|-----------|-------------------|
| HG4 | Benchmarks de industria | Profundo |

## Resumen Ejecutivo

Lenny Rachitsky publica la newsletter de producto más leída del mundo (+500K suscriptores). Su valor para el #7 no es su opinión sino sus datos: benchmarks verificados de retención, activación, conversión, NPS, y growth rates, recopilados de entrevistas con PMs y líderes de empresas reales. Esto le da al evaluador la capacidad de comparar métricas objetivamente en vez de aceptar cifras sin contexto.

---

## Conocimiento Destilado

### 1. Benchmarks por Tipo de Producto

#### SaaS B2B

| Métrica | Bueno | Excelente | Red Flag | Fuente |
|---------|-------|-----------|----------|--------|
| Trial-to-Paid Conversion | 15-25% | >25% | <10% | Lenny + OpenView |
| Net Revenue Retention (NRR) | 100-120% | >120% | <90% | Lenny + Bessemer |
| Logo Churn (monthly) | 2-5% | <2% | >7% | Lenny + ProfitWell |
| Time to Value | <1 día | <1 hora | >1 semana | Lenny |
| NPS | 30-50 | >50 | <0 | Delighted benchmarks |
| Activation Rate | 40-60% | >60% | <25% | Lenny + Amplitude |
| Payback Period (months) | 6-12 | <6 | >18 | Lenny + Bessemer |

#### Consumer / B2C Apps

| Métrica | Bueno | Excelente | Red Flag | Fuente |
|---------|-------|-----------|----------|--------|
| D1 Retention | 35-50% | >50% | <20% | Lenny + Amplitude |
| D7 Retention | 15-25% | >25% | <10% | Lenny + Amplitude |
| D30 Retention | 8-15% | >15% | <5% | Lenny + Amplitude |
| DAU/MAU Ratio | 20-30% | >30% (sticky) | <10% | Lenny |
| Viral Coefficient (K-factor) | 0.3-0.7 | >1.0 (viral) | <0.1 | Lenny |
| Session Duration | Varía | Varía | <30 sec | Depende de categoría |

#### Marketplace / Platform

| Métrica | Bueno | Excelente | Red Flag | Fuente |
|---------|-------|-----------|----------|--------|
| Take Rate | 10-20% | >20% | <5% | Lenny + a16z |
| Liquidity (listings → transactions) | 15-30% | >30% | <5% | Lenny |
| Supply-Side Retention (monthly) | 70-85% | >85% | <50% | Lenny |
| Demand-Side Retention (monthly) | 50-70% | >70% | <30% | Lenny |
| Time to First Transaction | <7 días | <1 día | >30 días | Lenny |

#### E-commerce / DTC

| Métrica | Bueno | Excelente | Red Flag | Fuente |
|---------|-------|-----------|----------|--------|
| Conversion Rate | 2-4% | >4% | <1% | Lenny + Shopify |
| Cart Abandonment | 60-70% | <60% | >80% | Baymard Institute |
| Repeat Purchase Rate | 25-40% | >40% | <15% | Lenny |
| LTV:CAC Ratio | 3:1 | >5:1 | <1:1 | Lenny |

### 2. Growth Rate Benchmarks por Etapa

| Etapa | Revenue Range | Growth Rate Bueno | Growth Rate Excelente |
|-------|--------------|-------------------|----------------------|
| Pre-PMF | Pre-revenue | N/A — focus on retention | N/A |
| Seed | $0 - $500K ARR | 15-20% MoM | >25% MoM |
| Series A | $500K - $2M ARR | 10-15% MoM | >20% MoM |
| Series B | $2M - $10M ARR | 7-12% MoM | >15% MoM |
| Growth | $10M - $50M ARR | 50-80% YoY | >100% YoY |
| Scale | $50M+ ARR | 30-50% YoY | >60% YoY |

### 3. PMF Indicators Consolidados

| Indicador | PMF Probable | PMF Dudoso | Fuente |
|-----------|-------------|------------|--------|
| Ellis "Very Disappointed" Survey | >40% | <25% | Sean Ellis |
| Organic/WoM as % of Acquisition | >50% | <20% | Lenny |
| Usage Frequency | >3x/semana | <1x/mes | Lenny |
| Retention Curve | Se estabiliza (flatten) | Cae a 0 | Lenny + Amplitude |
| Revenue per User (trending) | Creciente | Decreciente | Lenny |
| Time-to-Aha-Moment | <1 sesión | Nunca definido | Lenny |

### 4. Cómo Usar estos Benchmarks en Evaluación

#### Paso 1: Identificar tipo de producto
El output debe clasificar el producto: SaaS B2B, Consumer App, Marketplace, E-commerce, u otro.

#### Paso 2: Comparar contra benchmarks correspondientes
Para cada métrica mencionada en el output:
- **Above benchmark:** Verificar si es real (medido) o proyectado (estimado). Si es proyectado, ¿hay justificación?
- **At benchmark:** Aceptable pero sin ventaja competitiva. Señalar si el output lo presenta como "excelente".
- **Below benchmark:** Red flag. Exigir explicación de por qué y plan de mejora.
- **No benchmark comparison included:** CONDITIONAL — exigir que se agregue.

#### Paso 3: Verificar consistencia
Si un output dice "retención D30 del 25%" pero también dice "el producto está en pre-PMF", hay inconsistencia. D30 del 25% en consumer es excelente, incompatible con pre-PMF.

### 5. Anti-patrones en uso de métricas

| Anti-patrón | Por qué es malo | Check del #7 |
|-------------|----------------|--------------|
| Métricas vanity (signups, descargas, pageviews) | No miden valor real | Exigir métricas de activación y retención |
| Usar benchmarks de otra categoría | SaaS B2B retention ≠ Consumer app retention | Verificar que el benchmark corresponde al tipo de producto |
| Promedios sin contexto | "Retención promedio del 20%" — ¿D1? ¿D7? ¿D30? | Exigir métrica específica con horizonte temporal |
| Métricas sin tendencia | Un número aislado no dice nada. ¿Sube? ¿Baja? | Exigir datos de tendencia (mínimo 3 data points) |
| TAM como justificación | "El mercado vale $100B" no significa que capturarás ni el 0.001% | Exigir SAM y SOM con justificación |

---

## Notas de Destilación

- **Calidad de la fuente:** Alta para benchmarks cuantitativos. Fuente viva que se actualiza constantemente.
- **Actualización recomendada:** Cada 6 meses revisar benchmarks contra últimos artículos de Lenny
- **Lo que NO se extrajo:** Opiniones editoriales, recomendaciones de herramientas, entrevistas no cuantitativas
- **Complementa bien con:** FUENTE-705 (Ellis) para el proceso de growth, FUENTE-704 (Hormozi) para la value equation, FUENTE-706 (Chen) para benchmarks de network effects
