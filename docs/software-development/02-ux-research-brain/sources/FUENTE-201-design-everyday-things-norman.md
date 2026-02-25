---
id: FUENTE-201
source_id: FUENTE-201
brain: brain-software-02-ux-research
niche: software-development
cerebro: 02-ux-research
titulo: The Design of Everyday Things
title: The Design of Everyday Things
autor: Don Norman
author: Don Norman
expert_id: EXP-201
tipo: libro
type: book
language: en
isbn: 978-0465050659
edicion: Revised & Expanded Edition
año: 2013
year: 2013
capa: base-conceptual
experto: Don Norman
habilidad: Diseño centrado en humanos
tags:
- affordances
- mental-models
- feedback
- mappings
- cognitive-psychology
- human-centered-design
skills_covered:
- U1
- U3
- U5
distillation_date: '2026-02-24'
distillation_quality: complete
loaded_in_notebook: false
version_ficha: '1.0'
version: 1.0.0
last_updated: '2026-02-24'
changelog:
- version: 1.0.0
  date: '2026-02-24'
  changes:
  - Destilación inicial completa
  - Campos estándar de versioning agregados
status: active
fecha_creacion: '2026-02-24'
---


# FUENTE-201 — The Design of Everyday Things
**Don Norman | Basic Books, 2013 (Rev. Ed.)**

---

## 1. Por qué esta fuente es indispensable para el Cerebro #2

Norman fundó el campo del UX con este libro. No es una guía de tendencias ni un manual de herramientas — es la física del diseño centrado en humanos. Sus conceptos son atemporales porque están anclados en cómo funciona la cognición humana, no en modas de diseño. Todo lo que el Cerebro #2 evalúa, diagnostica o recomienda tiene su raíz conceptual aquí.

---

## 2. Conceptos Maestros

### 2.1 Affordances
Una affordance es la relación entre las propiedades de un objeto y las capacidades del usuario que determinan cómo podría usarse.

- **Affordance real:** Lo que el objeto permite físicamente hacer
- **Affordance percibida:** Lo que el usuario cree que puede hacer (lo que importa en UX)
- **Anti-affordance:** Señal de que algo NO se puede hacer (igualmente importante)

**Regla práctica del #2:** Si el usuario necesita leer un label para saber cómo interactuar con un elemento UI, la affordance falló.

### 2.2 Signifiers
Los signifiers son señales perceptibles que comunican dónde y cómo ocurre la acción. Son distintos de las affordances — las affordances existen, los signifiers comunican.

- Un botón elevado con sombra es un signifier (dice "soy clickeable")
- Un texto subrayado es un signifier (dice "soy un link")
- Espacio en blanco debajo de un campo es un signifier (dice "escribe aquí")

**Regla práctica del #2:** Diseñar para que los signifiers sean obvios sin instrucciones. Si hay tooltips de onboarding para features básicas, los signifiers fallaron.

### 2.3 Mappings
Relación entre controles y sus efectos. Un mapping natural reduce carga cognitiva porque coincide con las expectativas del usuario basadas en el mundo físico o en convenciones establecidas.

- **Mapping natural:** El slider izquierda/derecha controla el volumen bajo/alto (intuitivo)
- **Mapping arbitrario:** Los controles del horno de la mayoría de las cocinas (requieren aprender)

**Regla práctica del #2:** Evaluar siempre si el layout de controles en pantalla tiene mapping natural con el resultado esperado.

### 2.4 Feedback
El sistema debe comunicar al usuario el resultado de cada acción — inmediato, informativo, inequívoco.

Tipos de feedback relevantes en UX:
- **Sonoro:** Confirmaciones auditivas
- **Visual:** Cambio de estado visible (loading, success, error)
- **Táctil:** Vibración en mobile
- **Temporal:** Cuánto tiempo tomará una acción

**Ausencia de feedback = ansiedad del usuario.** Norman documenta que la falta de feedback es la causa #1 de errores por repetición (el usuario vuelve a clickear porque no sabe si pasó algo).

### 2.5 Conceptual Models (Mental Models)
El diseñador tiene un modelo del sistema. El usuario tiene un modelo mental de cómo cree que funciona. El sistema diseñado comunica uno de los dos. El problema: casi siempre comunica el del diseñador.

```
Modelo del Diseñador
        ↓
   Sistema diseñado (imagen del sistema)
        ↓
Modelo Mental del Usuario
```

**Regla del #2:** El modelo mental del usuario debe coincidir con cómo funciona realmente el sistema. Si no, habrá errores, frustración, y abandono. El UX Research existe para cerrar esta brecha.

### 2.6 El Golfo de Ejecución y el Golfo de Evaluación

**Golfo de Ejecución:** ¿Puede el usuario descubrir qué acciones son posibles y cómo ejecutarlas?
**Golfo de Evaluación:** ¿Puede el usuario interpretar el estado del sistema y saber si logró su objetivo?

Norman propone 7 etapas de la acción que mapean estos golfos:

| Etapa | Golfo |
|---|---|
| 1. Formar el objetivo | — |
| 2. Planear la acción | Ejecución |
| 3. Especificar la acción | Ejecución |
| 4. Ejecutar la acción | Ejecución |
| 5. Percibir el estado del sistema | Evaluación |
| 6. Interpretar la percepción | Evaluación |
| 7. Comparar con el objetivo | Evaluación |

**Diagnóstico del #2:** Cuando un usuario falla, identificar en cuál de las 7 etapas ocurrió la ruptura antes de proponer soluciones.

### 2.7 Errores: Slips vs Mistakes
- **Slip:** El usuario tiene el objetivo correcto pero ejecuta la acción incorrecta (error de ejecución automática)
- **Mistake:** El usuario tiene el objetivo incorrecto desde el principio (error de modelo mental)

**Implicación de diseño:** Los slips se resuelven con mejor diseño de interacción (prevención de errores, undo fácil). Los mistakes se resuelven con mejor comunicación del modelo conceptual.

### 2.8 Human-Centered Design (HCD) — El Proceso
Norman define el ciclo iterativo:

1. **Observar:** Entender las necesidades reales, no las declaradas
2. **Generar ideas:** Brainstorm sin restricciones
3. **Prototipar:** Rápido y barato, para aprender
4. **Testear:** Con usuarios reales, no con el equipo

**Principio clave:** "Si el usuario no puede usar el diseño, es culpa del diseño, no del usuario."

---

## 3. Heurísticas derivadas de Norman para evaluación UX

| # | Heurística Norman | Señal de fallo |
|---|---|---|
| 1 | Visibilidad del estado | El usuario pregunta "¿qué está pasando?" |
| 2 | Mapping natural | Requiere instrucciones para acciones básicas |
| 3 | Feedback inmediato | El usuario repite acciones por incertidumbre |
| 4 | Modelo conceptual claro | Errores sistemáticos en el mismo paso |
| 5 | Affordances obvias | Uso de tooltips para interacciones básicas |
| 6 | Reversibilidad | El usuario teme equivocarse |
| 7 | Manejo de errores | Los errores no explican cómo resolverse |

---

## 4. Frases Maestras (para activar el #2)

> "Good design is actually a lot harder to notice than poor design, in part because good designs fit our needs so well that the design is invisible."

> "Whenever you see signs or labels added to something, it is an indication of poor design."

> "The design should not require the user to read the manual."

> "If an error is possible, someone will make it."

---

## 5. Aplicación directa en el flujo del Mastermind

**Recibe del Cerebro #1:** Persona definida, propuesta de valor, problema validado
**Aplica FUENTE-201 para:**
- Diagnosticar si la arquitectura de interacción tiene affordances claras
- Evaluar si el modelo conceptual del sistema coincide con el mental model del usuario target
- Identificar golfo de ejecución vs golfo de evaluación en cada flujo crítico
- Clasificar errores de usuarios como slips o mistakes para priorizar soluciones

**Entrega al Cerebro #3:** Especificaciones de affordances, mappings requeridos, estados de feedback mínimos

---

## 6. Conexiones con otras fuentes del Cerebro #2

- **FUENTE-202 (Nielsen):** Las heurísticas de Nielsen son la operacionalización de los principios de Norman
- **FUENTE-203 (Krug):** Krug aplica los principios de Norman al contexto específico de web/apps
- **FUENTE-210 (Laws of UX):** Las leyes de Fitts, Hick y Miller son la cuantificación de los conceptos de Norman
