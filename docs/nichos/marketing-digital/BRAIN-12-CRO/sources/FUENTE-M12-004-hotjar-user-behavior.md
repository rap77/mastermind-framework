---
source_id: "FUENTE-M12-004"
brain: "brain-marketing-12-cro"
niche: "marketing-digital"
title: "Understanding User Behavior: The Hotjar Guide to Heatmaps, Session Recordings, and Feedback"
author: "Hotjar Team"
expert_id: "EXP-M12-004"
type: "guide"
language: "en"
year: 2023
isbn: null
url: "https://www.hotjar.com/blog/user-behavior/"
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

habilidad_primaria: "Análisis de comportamiento de usuario con heatmaps, recordings y surveys"
habilidad_secundaria: "Rage clicks, dead clicks, scroll depth, friction detection"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — Hotjar es el estándar de la industria para análisis cualitativo de comportamiento en CRO. Sus herramientas (heatmaps, session recordings, feedback) son el complemento indispensable del analytics cuantitativo de GA4."
---

# FUENTE-M12-004: Understanding User Behavior (Hotjar)

## Tesis Central

> **"Los números de GA4 te dicen QUÉ está pasando. Hotjar te dice POR QUÉ. El 95% de las oportunidades de CRO se descubren viendo cómo los usuarios reales interactúan con tu sitio, no analizando tablas de datos."**

---

## 1. Principios Fundamentales

### Los 3 tipos de análisis de comportamiento

1. **Heatmaps:** Agregado visual de dónde hacen click, se mueven, y hasta dónde hacen scroll miles de usuarios
   - Click maps: Qué elementos se clickean (y cuáles se clickean pensando que son links cuando no lo son)
   - Move maps: Correlacionan con donde leen (eye-tracking proxy)
   - Scroll maps: % de usuarios que llegan a cada punto de la página

2. **Session Recordings:** Videos individuales de sesiones reales
   - Ver el comportamiento completo de usuarios reales
   - Identificar puntos de confusión, frustración, abandon
   - Descubrir bugs y errores que los usuarios encuentran

3. **Surveys y Feedback:**
   - On-site surveys: Preguntar en el momento justo (exit intent, post-conversión)
   - NPS en producto: Medir satisfacción de usuarios activos
   - User testing: Tareas específicas con feedback verbal

*Fuente: Hotjar, "Behavior Analytics Guide" (2023)*

### Las señales de fricción que hay que buscar

**Rage clicks:** El usuario hace click repetidamente en el mismo elemento en frustración
- Señal de: Elemento que parece interactivo pero no lo es, o proceso que no responde

**Dead clicks:** Clicks en áreas sin función
- Señal de: Confusión sobre qué es clickeable

**U-turns:** El usuario llega a una página y vuelve inmediatamente
- Señal de: Mismatch entre expectativa (del link que clickeó) y contenido de la página

**Form abandonments:** El usuario empieza a completar un formulario y lo abandona
- Señal de: Campo específico que genera fricción o duda

*Fuente: Hotjar, "Friction Detection" (2023)*

---

## 2. Frameworks y Metodologías

### Framework: Hotjar CRO Research Process

```
PASO 1: Heatmaps en páginas clave
└── ¿Hacen scroll suficiente para ver el CTA?
└── ¿Hay elementos que confunden (dead clicks)?
└── ¿El CTA recibe suficientes clicks?

PASO 2: Session recordings filtradas
└── Filtrar por: páginas con alta exit rate
└── Filtrar por: usuarios que llegaron al checkout pero no compraron
└── Filtrar por: rage clicks y errores
└── Ver mínimo 50 sesiones por página problemática

PASO 3: On-site surveys en exit intent
└── Pregunta para visitantes que salen sin convertir:
    "¿Qué te impidió completar tu compra hoy?"
└── Pregunta para nuevos visitantes:
    "¿Pudiste encontrar lo que buscabas?"
└── Analizar respuestas abiertas para patrones

PASO 4: Post-purchase survey
└── "¿Cómo describirías este producto a un amigo?"
└── (Usar respuestas para mejorar el copy de la landing)

PASO 5: Sintetizar hallazgos en hipótesis priorizadas
└── Cada hipótesis: problema identificado + solución propuesta + KPI a medir
```

*Fuente: Hotjar, "CRO Research Guide" (2023)*

### Framework: Preguntas de Survey según objetivo

| Objetivo | Pregunta | Dónde mostrar |
|----------|----------|---------------|
| Entender objeciones | "¿Qué te impidió completar hoy?" | Exit intent en checkout |
| Mejorar copy | "¿Cómo describirías esto a un amigo?" | Post-compra |
| Identificar confusión | "¿Pudiste encontrar lo que buscabas?" | Exit intent en home/product |
| Validar messaging | "¿Qué palabras usarías para describir X?" | A usuarios de alto engagement |
| NPS | "¿Recomendarías X a un amigo?" (0-10) | Post-uso, después de 30 días |

*Fuente: Hotjar, "Survey Question Guide" (2023)*

---

## 3. Modelos Mentales

### "5 usuarios de user testing revelan el 80% de los problemas de usabilidad"

(Nielsen/Hotjar data) No necesitás 100 usuarios para descubrir problemas de usabilidad. Con 5 usuarios que piensan en voz alta mientras completan una tarea típica, se descubren la gran mayoría de los problemas.

**Implicación:** User testing es accesible para cualquier empresa, incluso con presupuesto limitado.

*Fuente: Hotjar, "User Testing Fundamentals" (2023)*

### "El comportamiento revela lo que las encuestas no pueden"

Los usuarios dicen lo que creen que querés escuchar. Los recordings muestran lo que realmente hacen. Siempre priorizar behavioral data sobre declaraciones directas cuando haya contradicción.

*Fuente: Hotjar, "Behavioral vs. Attitudinal Research" (2023)*

---

## 4. Criterios de Decisión

### Cuántas session recordings ver por página

- **Páginas de alto valor (checkout, pricing, hero landing):** 50-100 sesiones mínimo
- **Páginas de medio valor (product pages, blog con alto tráfico):** 20-50 sesiones
- **Páginas de bajo valor:** 10-20 sesiones o solo heatmaps

*Fuente: Hotjar, "Research Depth Guide" (2023)*

### Hotjar vs. FullStory vs. Microsoft Clarity

| Herramienta | Mejor para | Costo |
|-------------|-----------|-------|
| **Hotjar** | CRO y UX research, surveys integradas | Desde €32/mes |
| **FullStory** | Enterprise, datos más granulares | Desde €2000/año |
| **Microsoft Clarity** | Básico, gratuito, integra con GA4 | Gratis |
| **LogRocket** | Debugging técnico + UX | Desde €100/mes |

*Fuente: CRO community benchmarks (2023)*

---

## 5. Anti-patrones

### Anti-patrón: Ver recordings sin hipótesis previa

Ver recordings sin saber qué buscás es una pérdida de tiempo. Siempre filtrar por comportamiento específico (rage clicks, abandono en checkout) y tener una pregunta en mente.

*Fuente: Hotjar, "Research Efficiency" (2023)*

### Anti-patrón: Survey con demasiadas preguntas

Una survey de exit intent con 5+ preguntas tiene tasa de respuesta < 5%. Una pregunta bien elegida puede tener 15-25% de respuesta. Menos es más.

*Fuente: Hotjar, "Survey Best Practices" (2023)*

### Anti-patrón: Ignorar mobile recordings

Si el 60-70% del tráfico es mobile pero solo revisás recordings de desktop, estás viendo el 30-40% del problema. Siempre segmentar el análisis por dispositivo.

*Fuente: Hotjar, "Mobile CRO" (2023)*
