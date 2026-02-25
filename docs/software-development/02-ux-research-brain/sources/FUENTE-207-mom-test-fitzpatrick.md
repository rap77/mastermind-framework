---
id: FUENTE-207
cerebro: 02-ux-research
titulo: The Mom Test
autor: Rob Fitzpatrick
tipo: libro
isbn: 978-1492180746
edicion: 1st Edition
año: 2013
capa: frameworks
experto: Rob Fitzpatrick
habilidad: Entrevistas de usuario sin sesgo de confirmación
tags:
- user-interviews
- confirmation-bias
- customer-development
- behavioral-questions
- bad-data
- good-data
version_ficha: '1.0'
fecha_creacion: '2026-02-24'
source_id: FUENTE-207
brain: brain-software-02-ux-research
niche: software-development
title: The Mom Test
author: Rob Fitzpatrick
type: libro
year: 2013
expert_id: EXP-207
language: en
skills_covered:
- U8
- U9
distillation_date: '2026-02-24'
distillation_quality: complete
loaded_in_notebook: false
version: 1.0.0
last_updated: '2026-02-24'
changelog:
- version: 1.0.0
  date: '2026-02-24'
  changes:
  - Destilación inicial completa
  - Campos estándar de versioning agregados
status: active
---


# FUENTE-207 — The Mom Test
**Rob Fitzpatrick | CreateSpace, 2013**

---

## 1. Por qué esta fuente es indispensable para el Cerebro #2

El Mom Test resuelve el problema más frecuente en UX research: obtener datos falsos positivos en las entrevistas de usuario. La mayoría de los equipos realizan entrevistas que confirman lo que ya creen porque hacen las preguntas equivocadas. Fitzpatrick da las reglas precisas para hacer preguntas que producen datos reales, incluso cuando el entrevistado quiere ser amable (como tu mamá).

---

## 2. El Problema Central

> "Una entrevista de usuario es mala si hasta tu mamá te respondería lo que quieres escuchar."

El problema no es que los usuarios mientan — es que los humanos naturalmente quieren ser amables y evitar el conflicto. Si preguntas "¿te gustaría una app que haga X?", casi todos dirán "sí" — porque es lo que quieres escuchar y porque es una pregunta hipotética sin costo para ellos.

**Datos inútiles típicos de entrevistas mal hechas:**
- "Sí, me parece interesante"
- "Creo que lo usaría"
- "Definitivamente necesito algo así"
- "La idea es genial"

**Por qué son inútiles:** Expresan intención hipotética, no comportamiento real.

---

## 3. Las 3 Reglas del Mom Test

### Regla 1: Hablar sobre su vida, no sobre tu idea
Las conversaciones deben girar en torno a la vida, comportamiento y problemas del usuario — no a tu producto o solución.

**Mal:** "¿Qué piensas de nuestra idea de una app de meditación guiada?"
**Bien:** "¿Cómo manejas el estrés actualmente en tu día a día?"

### Regla 2: Preguntar sobre el pasado específico, no sobre el futuro hipotético
El comportamiento pasado predice el comportamiento futuro. Las intenciones hipotéticas no predicen nada.

**Mal:** "¿Pagarías $10 al mes por esta feature?"
**Bien:** "¿Cuánto pagaste el último mes por herramientas relacionadas con [problema]?"

**Mal:** "¿Usarías esto si lo construyéramos?"
**Bien:** "¿Cómo resolviste esto la última vez que ocurrió?"

### Regla 3: Hablar menos, escuchar más
El entrevistador debe hablar menos del 30% del tiempo. Si estás explicando tu producto, no estás haciendo research — estás vendiendo.

---

## 4. Señales de Datos Buenos vs Datos Malos

### Datos malos (ignorar en el análisis):
| Tipo | Ejemplo | Por qué es malo |
|---|---|---|
| Cumplidos | "¡Qué idea tan buena!" | Cortesía social, no información |
| Intenciones hipotéticas | "Definitivamente lo usaría" | Costo cero para el usuario |
| Afirmaciones genéricas | "Sí, eso es un problema" | Sin evidencia de comportamiento real |
| Respuestas a preguntas leading | "Sí, supongo que sería útil" | Confirmando tu hipótesis |

### Datos buenos (actuar sobre estos):
| Tipo | Ejemplo | Por qué es valioso |
|---|---|---|
| Comportamiento específico pasado | "La semana pasada pasé 3 horas buscando eso en Google" | Real, verificable |
| Dolor expresado espontáneamente | "Es una pesadilla hacer X" | Sin ser preguntado |
| Dinero o tiempo ya gastado | "Pago $50/mes en [solución alternativa]" | Comportamiento real |
| Compromiso en el momento | "¿Puedo darme de alta ahora?" | Señal de compra real |
| Referidos espontáneos | "Deberías hablar con mi colega — tiene el mismo problema" | Validación no solicitada |

---

## 5. Preguntas Correctas por Objetivo

### Para entender el problema real:
- "¿Puedes contarme la última vez que [problema ocurrió]?"
- "¿Cómo lo resolviste en ese momento?"
- "¿Cuánto tiempo/dinero te costó esa solución?"
- "¿Qué fue lo más frustrante de eso?"
- "¿Has buscado alternativas? ¿Qué encontraste?"

### Para entender el contexto de uso:
- "¿Con qué frecuencia sucede esto?"
- "¿Quién más está involucrado cuando esto pasa?"
- "¿En qué momento del día/semana ocurre?"

### Para entender la disposición a pagar:
- "¿Qué soluciones has probado para este problema?"
- "¿Cuánto pagaste por la última?"
- "¿Por qué dejaste de usarla?"

### Para validar prioridad del problema:
- "¿Cuáles son los 3 problemas más grandes en [dominio]?"
- "¿Qué has intentado hacer para resolverlos?"
- Si no lo han intentado resolver → el problema no es tan importante como dicen

---

## 6. La Jerarquía de Señales de Validación (Fitzpatrick)

Fitzpatrick propone una jerarquía de cuánto valor dar a diferentes señales:

```
MÁXIMO VALOR
    ↑
    │ Pre-compra / LOI firmado / Dinero en mano
    │ Compromisos no monetarios significativos (tiempo, intro a equipo, datos)
    │ Comportamiento pasado documentado con gasto real
    │ Dolor expresado espontáneamente sin ser preguntado
    │ Comportamiento pasado sin gasto
    │ Intención futura con especificidad ("Lo usaría si...")
    ↓
MÍNIMO VALOR
    │ Cumplidos ("¡Me encanta la idea!")
    │ Intención hipotética genérica
```

---

## 7. Tipos de Entrevistas y Cuándo Usarlas

### Entrevistas de exploración (antes de diseñar)
**Objetivo:** Entender el problema, el contexto, y el comportamiento actual
**Formato:** Conversacional, sin agenda rígida
**Duración:** 30-60 minutos
**Output:** Insights sobre el problema real

### Entrevistas de validación (con prototipo o concepto)
**Objetivo:** Verificar si una solución específica resuelve el problema correctamente
**Formato:** Show + observe + preguntar
**Duración:** 45-60 minutos
**Output:** Problemas de usabilidad y validación de valor percibido

### Entrevistas de precio (antes de lanzar)
**Objetivo:** Entender disposición a pagar y modelo de valor
**Formato:** Comportamiento pasado de gasto + reacción a precios reales
**Duración:** 20-30 minutos
**Output:** Rango de precios y modelo de valor percibido

---

## 8. Errores Fatales en Entrevistas (Fitzpatrick)

### Error #1: Defender la idea
Cuando el usuario expresa dudas, el natural humano es defender. Hacer esto invalida la entrevista — el usuario deja de ser honesto y empieza a buscar cómo no herir al entrevistador.

**En cambio:** "¿Puedes contarme más sobre esa duda?" / "¿Qué te hace sentir eso?"

### Error #2: Pedir confirmar hipótesis
"¿Entonces el problema es X, verdad?" → El usuario confirmará aunque no sea exactamente X.

**En cambio:** "¿Cómo describirías el problema con tus propias palabras?"

### Error #3: Hablar demasiado de la solución
Una vez que describes la solución, el usuario cambia de modo: ya no te da insights de problema, te da feedback de producto (que en esta etapa no necesitas).

### Error #4: Una sola persona como entrevistador y analista
El mismo sesgo cognitivo que distorsiona las preguntas distorsiona el análisis. Siempre que sea posible: un entrevistador, un observador/analista.

### Error #5: Entrevistas sin estructura de captura
Sin un sistema de notas consistente, los hallazgos se mezclan con las impresiones. Usar formato estándar: [cita textual] / [observación] / [interpretación] — claramente separados.

---

## 9. Formato de Notas del Mom Test

```
SESIÓN: [Nombre/alias del usuario] | [Fecha] | [Duración]
CONTEXTO: [Perfil relevante del usuario]

CITAS TEXTUALES (verbatims):
- "[Cita exacta]" → SEÑAL: [tipo de dato]

COMPORTAMIENTOS OBSERVADOS:
- [Acción específica que hizo]

INTERPRETACIONES:
- [Lo que esto podría significar]

COMPROMISOS / SEÑALES FUERTES:
- [Cualquier compromiso o señal de alta validez]

PREGUNTAS SIN RESPONDER:
- [Lo que todavía no sabemos]
```

---

## 10. Aplicación directa en el flujo del Mastermind

**Aplica FUENTE-207 para:**
- Diseñar el protocolo de entrevistas de usuario antes de cualquier sesión
- Revisar preguntas de entrevista para eliminar las que generan datos malos
- Analizar transcripciones de entrevistas y separar datos buenos de datos malos
- Entrenar al equipo en cómo hacer entrevistas sin sesgo de confirmación

**Pregunta que activa esta fuente:** "¿Las respuestas que estamos obteniendo son datos reales o cumplidos?"

---

## 11. Conexiones con otras fuentes del Cerebro #2

- **FUENTE-204 (Young):** Young provee el marco de análisis (mental models); Fitzpatrick provee las reglas de conversación para obtener datos limpios
- **FUENTE-205 (Hall):** Hall clasifica cuándo usar entrevistas; Fitzpatrick define cómo hacerlas bien
- **FUENTE-208 (Torres):** Torres aplica las entrevistas de Fitzpatrick en un ciclo continuo semanal en equipos de producto
