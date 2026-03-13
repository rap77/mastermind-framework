---
source_id: "FUENTE-M11-005"
brain: "brain-marketing-11-analytics"
niche: "marketing-digital"
title: "Marketing Attribution: From Last-Click to Data-Driven Models"
author: "Google Marketing Platform Team"
expert_id: "EXP-M11-005"
type: "guide"
language: "en"
year: 2023
isbn: null
url: "https://support.google.com/analytics/answer/10596866"
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

habilidad_primaria: "Attribution modeling y análisis de customer journey multi-touch"
habilidad_secundaria: "Media Mix Modeling, incrementality testing, GA4 attribution"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "CRÍTICA — Attribution es el problema central de marketing analytics. Sin un modelo de atribución correcto, los presupuestos de marketing se asignan mal. Este recurso consolida los modelos estándar y las mejores prácticas de la industria."
---

# FUENTE-M11-005: Marketing Attribution Models (Google Marketing Platform)

## Tesis Central

> **"El modelo de atribución last-click es como premiar al último kilómetro de una maratón y olvidar los 42 kilómetros anteriores. Sin atribución multi-touch, estás dando crédito equivocado y recortando los canales que más contribuyen."**

---

## 1. Principios Fundamentales

### El problema de la atribución

El customer journey moderno involucra múltiples touchpoints antes de la conversión:

```
Ejemplo típico de customer journey:
1. Ve un video de YouTube (TOFU)
2. Hace clic en un ad de Instagram (MOFU)
3. Busca en Google "mejor [producto]" (MOFU)
4. Lee reviews en blog (MOFU)
5. Recibe email de remarketing (BOFU)
6. Hace clic en Google Shopping → COMPRA
```

**La pregunta:** ¿A quién le damos crédito por la conversión?

*Fuente: Google Analytics, Attribution Overview (2023)*

### Los 6 modelos de atribución principales

| Modelo | Descripción | Ventaja | Limitación |
|--------|-------------|---------|------------|
| **Last-Click** | 100% al último canal | Simple | Ignora el journey |
| **First-Click** | 100% al primer canal | Valora awareness | Ignora la conversión |
| **Linear** | % igual a cada canal | Democrático | No refleja importancia real |
| **Time-Decay** | Más peso a canales recientes | Más realista | Subvalora TOFU |
| **Position-Based** | 40% primero + 40% último + 20% medio | Balance | Arbitrario |
| **Data-Driven** | ML aprende del comportamiento real | El más preciso | Requiere volumen de datos |

*Fuente: Google Analytics, Attribution Models (2023)*

---

## 2. Frameworks y Metodologías

### Framework: Elegir el modelo de atribución correcto

**Árbol de decisión:**

```
¿Tenés +1000 conversiones/mes?
├── SÍ → Data-Driven Attribution (GA4 nativo)
└── NO →
    ¿Tu objetivo es brand awareness?
    ├── SÍ → First-Click o Position-Based
    └── NO →
        ¿Tenés un ciclo de venta largo (>7 días)?
        ├── SÍ → Position-Based o Linear
        └── NO → Time-Decay
```

*Fuente: Google Marketing Platform, "Attribution Selection" (2023)*

### Framework: Media Mix Modeling (MMM)

Para marketing a gran escala donde el tracking individual es limitado (cookies, privacidad):

**¿Qué es MMM?**
Modelo estadístico (regresión) que correlaciona inversión por canal con ventas históricas, controlando por factores externos (estacionalidad, economía).

**Cuándo usar:**
- Presupuesto >€500K/año en medios
- Mezcla de canales online + offline
- Privacidad impide tracking granular

**Limitación:** MMM mide correlación histórica, no predice bien cambios drásticos en estrategia.

*Fuente: Google, "Marketing Mix Modeling Guide" (2022)*

### Framework: Incrementality Testing

La forma más rigurosa de medir el valor real de un canal:

1. **Geo-based holdout:** Pausar un canal en algunas geografías y comparar con las que sigue activo
2. **User-based holdout:** Controlar grupo que no ve ads vs. grupo expuesto
3. **Budget pause test:** Pausar canal por 2 semanas y medir impacto en conversiones totales

**Por qué es mejor que attribution:** Attribution mide correlación. Incrementality mide causalidad real.

*Fuente: Google Marketing Platform, "Incrementality Testing" (2022)*

---

## 3. Modelos Mentales

### "Todo modelo de atribución es incorrecto, pero algunos son útiles"

(Adaptado de George Box). Ningún modelo de atribución captura perfectamente la realidad del customer journey. La pregunta no es "¿cuál es el modelo correcto?" sino "¿cuál modelo me ayuda a tomar mejores decisiones?"

*Fuente: Google Marketing Platform, "Attribution Philosophy" (2023)*

### "El canal que cierra la venta raramente es el que la genera"

Los análisis de last-click consistentemente sobrevaloran SEM y email (canales de cierre) y subvaloran social, display y video (canales de influencia). Un modelo balanceado redistribuye crédito hacia los canales de awareness.

*Fuente: Google Analytics, "Attribution Insights" (2023)*

---

## 4. Criterios de Decisión

### Cuándo invertir en Data-Driven Attribution

- Mínimo 600 conversiones/mes (GA4 requiere este volumen)
- Ciclo de venta > 3 días (múltiples touchpoints)
- Más de 3 canales activos simultáneamente

*Fuente: Google Analytics, "DDA Requirements" (2023)*

### Attribution en cookieless world (post-3rd party cookies)

Con la eliminación de cookies de terceros (Chrome 2024):
1. **First-party data:** Medir solo con propios datos (CRM, GA4 con User ID)
2. **Enhanced Conversions:** Enviar hashed data para mejor matching
3. **Consent Mode + Modeling:** Estimar conversiones donde no hay consentimiento
4. **MMM:** Mayor relevancia como alternativa a tracking individual

*Fuente: Google, "Measurement Future" (2023)*

---

## 5. Anti-patrones

### Anti-patrón: Last-click en canales de branding

Evaluar la efectividad de YouTube Ads o display con last-click attribution garantiza que siempre "perderán" contra SEM o email. Esto lleva a sub-inversión crónica en canales de awareness.

*Fuente: Google Marketing Platform, "Attribution Mistakes" (2023)*

### Anti-patrón: Usar el mismo modelo para todos los objetivos

Un modelo de atribución para brand awareness debe ser diferente al de performance/revenue. Usar last-click para todo es el error más común.

*Fuente: Google Marketing Platform, "Multi-model Approach" (2023)*

### Anti-patrón: Ignorar conversiones view-through

Las conversiones view-through (usuario vio el ad pero no hizo click, luego convirtió) son invisibles en modelos click-based. Para canales de display y video, ignorarlas subestima masivamente el impacto.

*Fuente: Google Analytics, "View-Through Attribution" (2023)*
