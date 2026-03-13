---
source_id: "FUENTE-M11-008"
brain: "brain-marketing-11-analytics"
niche: "marketing-digital"
title: "Cohort Analysis: The Most Important Analytics Framework for Growth"
author: "Andrew Chen"
expert_id: "EXP-M11-008"
type: "blog_series"
language: "en"
year: 2021
isbn: null
url: "https://andrewchen.com/cohort-analysis/"
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

habilidad_primaria: "Cohort analysis para retención, growth y producto"
habilidad_secundaria: "Retention curves, engagement loops, acquisition quality measurement"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — Andrew Chen (a16z, ex-Uber Growth) es la referencia en growth analytics. Su framework de cohort analysis y retention curves es estándar para medir la salud real de un producto o e-commerce."
---

# FUENTE-M11-008: Cohort Analysis (Andrew Chen)

## Tesis Central

> **"El análisis de cohortes es el detector de mentiras de los negocios digitales. Las métricas agregadas pueden mostrar crecimiento mientras el negocio se destruye internamente. Las cohortes muestran la verdad: si cada nueva generación de usuarios es mejor, igual, o peor que la anterior."**

---

## 1. Principios Fundamentales

### Qué es una cohorte y por qué importa

Una cohorte es un grupo de usuarios que comparten una característica en un momento específico:
- **Cohorte de adquisición:** Todos los usuarios que se registraron en enero 2024
- **Cohorte de comportamiento:** Todos los usuarios que compraron más de 3 veces en Q1
- **Cohorte de canal:** Todos los usuarios adquiridos vía paid social

**Por qué el análisis de cohortes es superior a métricas agregadas:**

```
Ejemplo: Una empresa tiene 1,000 usuarios activos cada mes durante 6 meses.
Parece estable, ¿verdad?

Cohorte Jan: 500 usuarios → retención mes 6: 20% (100 usuarios)
Cohorte Feb: 500 usuarios → retención mes 5: 30% (150 usuarios)
...

En realidad, la retención está MEJORANDO, pero el churn de cohortes viejas
lo oculta en las métricas agregadas.
```

*Fuente: Chen, "Cohort Analysis 101" (andrewchen.com, 2021)*

### La Retention Curve

El análisis más importante en cualquier producto digital:

```
Retention (%)
100% |
 80% |█
 60% |  █
 40% |    █
 20% |      █ █ █ _ _ _ _ _ (FLATTENS = product-market fit)
  0% |_________________________
     Day0 Day7 Day14 Day30 Day90 Day180 Day365
```

**Interpretación:**
- **Curva que llega a cero:** Producto sin product-market fit
- **Curva que se aplana:** Producto con PMF — hay usuarios que se quedan permanentemente
- **Qué nivel de retención es bueno:** Depende del vertical (ver benchmarks)

*Fuente: Chen, "Retention Curves" (andrewchen.com, 2021)*

---

## 2. Frameworks y Metodologías

### Framework: Retention Benchmarks por Vertical

Benchmarks de Day 30 retention (Chen + datos de industria):

| Vertical | Good | Great | Best in class |
|----------|------|-------|---------------|
| **Consumer app** | 25% | 35% | 45%+ |
| **E-commerce** | 15% | 25% | 35%+ |
| **SaaS B2B** | 60% | 75% | 85%+ |
| **Social** | 30% | 40% | 50%+ |
| **Gaming** | 20% | 30% | 40%+ |

*Fuente: Chen, "Retention Benchmarks" (andrewchen.com, 2022)*

### Framework: Cohort Quality Analysis

Más allá de retención, analizar si las cohortes nuevas son mejores o peores en valor:

```sql
-- Cohort Revenue Analysis en BigQuery/SQL
SELECT
  DATE_TRUNC(first_purchase_date, MONTH) as cohort_month,
  DATE_DIFF(purchase_date, first_purchase_date, MONTH) as months_since_first,
  SUM(revenue) / COUNT(DISTINCT user_id) as revenue_per_user
FROM orders
GROUP BY 1, 2
ORDER BY 1, 2
```

Visualizado como heatmap: cada fila = cohorte, cada columna = mes desde adquisición.

*Fuente: Chen, "Cohort Revenue Analysis" (andrewchen.com, 2021)*

### Framework: Acquisition Quality Score

Chen propone medir no solo cuántos usuarios trae cada canal, sino qué calidad tienen:

```
Quality Score = (30-day Retention × ARPU) / CAC

Canal A: 25% retention × €50 ARPU / €30 CAC = Score 41.6
Canal B: 40% retention × €80 ARPU / €60 CAC = Score 53.3

Canal B es mejor aunque tenga CAC más alto.
```

*Fuente: Chen, "Acquisition Quality" (andrewchen.com, 2022)*

---

## 3. Modelos Mentales

### "El crecimiento que esconde mal retention no es sostenible"

Muchas startups crecen en usuarios mientras el churn destruye la base. El "leaky bucket" — el cubo agujerado — es la metáfora de Chen: no importa cuánta agua eches si el cubo pierde agua por el fondo.

*Fuente: Chen, "The Leaky Bucket" (andrewchen.com, 2020)*

### "D1/D7/D30 como sistema de alerta temprana"

Los tres KPIs de retention que hay que monitorear como semáforo:
- **D1 (Day 1 Retention):** ¿El usuario volvió al día siguiente? (onboarding quality)
- **D7 (Day 7):** ¿Formó un hábito de la primera semana?
- **D30 (Day 30):** ¿Se convirtió en usuario habitual?

Si D1 < 25% en consumer, hay un problema de onboarding urgente.

*Fuente: Chen, "D1/D7/D30 Framework" (andrewchen.com, 2021)*

---

## 4. Criterios de Decisión

### Qué cohorte analizar primero

- **Si hay churn alto reciente:** Cohorte de adquisición (¿los nuevos usuarios son peores?)
- **Si hay caída en revenue:** Cohorte de valor (¿los mejores clientes se están yendo?)
- **Si se cambió el modelo de precios:** Cohorte pre/post-cambio
- **Si se lanzó nueva feature:** Cohorte de usuarios que la adoptaron vs. los que no

*Fuente: Chen, "Cohort Selection Guide" (andrewchen.com, 2022)*

---

## 5. Anti-patrones

### Anti-patrón: Solo mirar DAU/MAU sin cohortes

DAU (Daily Active Users) y MAU pueden crecer mientras la retención cae. Las métricas agregadas ocultan la descomposición interna del negocio.

*Fuente: Chen, "Vanity Metrics" (andrewchen.com, 2020)*

### Anti-patrón: Comparar cohortes de distintos tamaños directamente

Una cohorte de 100 usuarios tiene mayor varianza estadística que una de 10,000. Comparar tasas de retención sin considerar el tamaño de muestra lleva a conclusiones erróneas.

*Fuente: Chen, "Statistical Significance in Cohorts" (andrewchen.com, 2021)*

### Anti-patrón: Cohortes sin segmentación

El análisis de cohortes agregado oculta que algunas cohortes de cierto canal, geografía o plan de precio retienen mucho mejor. Segmentar las cohortes por las variables más relevantes del negocio.

*Fuente: Chen, "Cohort Segmentation" (andrewchen.com, 2022)*
