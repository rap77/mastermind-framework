---
id: FUENTE-202
cerebro: 02-ux-research
titulo: Usability Engineering
autor: Jakob Nielsen
tipo: libro+articulos
isbn: 978-0125184069
fuente_complementaria: https://www.nngroup.com/articles/
año: 1993 (libro) + actualización continua (NN/g)
capa: frameworks + retroalimentacion
experto: Jakob Nielsen
habilidad: Usabilidad y testing
tags:
- usability
- heuristics
- testing
- sus-score
- task-success
- metrics
- evaluation
version_ficha: '1.0'
fecha_creacion: '2026-02-24'
source_id: FUENTE-202
brain: brain-software-02-ux-research
niche: software-development
title: Usability Engineering
author: Jakob Nielsen
type: libro+articulos
year: 1993 (libro) + actualización continua (NN/g)
expert_id: EXP-202
language: en
skills_covered:
- U2
- U4
- U6
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


# FUENTE-202 — Usability Engineering
**Jakob Nielsen | Morgan Kaufmann, 1993 + NN/g Articles (ongoing)**

---

## 1. Por qué esta fuente es indispensable para el Cerebro #2

Nielsen es la referencia empírica del campo. Mientras Norman da el marco conceptual, Nielsen da la metodología operacional: cómo medir usabilidad, cómo encontrar problemas eficientemente, y qué métricas usar para demostrar que algo mejoró. Sus 10 heurísticas son el estándar universal de evaluación experta.

---

## 2. Las 10 Heurísticas de Nielsen

Estas son las heurísticas de evaluación más usadas en la industria. Cada una incluye su definición y señales de violación en productos digitales.

### H1 — Visibilidad del estado del sistema
El sistema siempre debe mantener informado al usuario sobre lo que está pasando, con feedback apropiado en tiempo razonable.

**Señales de violación:**
- Loading infinito sin indicador de progreso
- Formularios enviados sin confirmación visual
- Acciones sin estado de éxito/error

**Pregunta de diagnóstico:** ¿El usuario sabe en todo momento dónde está y qué acaba de pasar?

### H2 — Match entre sistema y mundo real
El sistema debe hablar el idioma del usuario: palabras, frases y conceptos familiares, siguiendo convenciones del mundo real.

**Señales de violación:**
- Jerga técnica en mensajes de error
- Terminología interna de la empresa en la UI
- Metáforas que no existen en el contexto del usuario

**Pregunta de diagnóstico:** ¿Un usuario nuevo (no el equipo) entiende todos los labels, mensajes y nombres sin explicación?

### H3 — Control y libertad del usuario
Los usuarios eligen funciones por error y necesitan salidas de emergencia claras sin procesos extendidos.

**Señales de violación:**
- No hay "Deshacer"
- Flujos de varios pasos sin opción de cancelar
- Eliminación de datos sin confirmación y sin recuperación

**Pregunta de diagnóstico:** ¿Puede el usuario salir de cualquier estado del sistema fácilmente?

### H4 — Consistencia y estándares
Los usuarios no deberían preguntarse si palabras, situaciones o acciones diferentes significan la misma cosa.

**Señales de violación:**
- El mismo elemento tiene distintos nombres en diferentes pantallas
- Íconos que cambian de función según contexto
- Diferentes patrones de interacción para acciones similares

**Pregunta de diagnóstico:** ¿Todo el sistema habla con una sola voz?

### H5 — Prevención de errores
Mejor que buenos mensajes de error es un diseño cuidadoso que previene los problemas.

**Señales de violación:**
- Campos de formulario que aceptan formatos incorrectos sin validación
- Acciones destructivas sin confirmación
- No hay restricciones en inputs que tienen formato requerido

**Pregunta de diagnóstico:** ¿El sistema hace difícil cometer errores comunes?

### H6 — Reconocer en lugar de recordar
Minimizar la carga de memoria del usuario haciendo visibles objetos, acciones y opciones.

**Señales de violación:**
- El usuario debe recordar información de un paso anterior para completar el siguiente
- Las opciones disponibles no son visibles (menús ocultos sin indicación)
- El historial de acciones no es accesible

**Pregunta de diagnóstico:** ¿El usuario necesita recordar algo entre pantallas?

### H7 — Flexibilidad y eficiencia de uso
Los aceleradores (invisibles para el novato) permiten al usuario experto hacer las tareas más rápido.

**Señales de violación:**
- No hay atajos de teclado para acciones frecuentes
- El flujo para usuarios avanzados es igual de largo que para nuevos
- No hay personalización o customización

**Pregunta de diagnóstico:** ¿El producto es igual de frustrante para un usuario de 2 años que para uno nuevo?

### H8 — Diseño estético y minimalista
Los diálogos no deben contener información irrelevante o raramente necesaria.

**Señales de violación:**
- Pantallas cargadas de información que compite por atención
- Features secundarias con el mismo peso visual que las primarias
- Información de contexto excesiva en cada acción

**Pregunta de diagnóstico:** ¿Hay algo en esta pantalla que el usuario no necesita para completar su tarea?

### H9 — Ayuda a reconocer, diagnosticar y recuperarse de errores
Los mensajes de error deben estar en lenguaje claro, indicar el problema con precisión y sugerir una solución.

**Señales de violación:**
- Mensajes de error con códigos técnicos ("Error 404", "Exception null pointer")
- Mensajes que dicen qué falló pero no cómo resolverlo
- Errores que desaparecen sin que el usuario los vea

**Pregunta de diagnóstico:** ¿Puede el usuario resolver el error por sí solo con el mensaje que recibe?

### H10 — Ayuda y documentación
Aunque es mejor que el sistema pueda usarse sin documentación, puede ser necesario proveer ayuda.

**Señales de violación:**
- La ayuda no está indexada por tarea del usuario
- Los artículos de soporte son técnicos, no orientados a objetivos
- No hay ayuda contextual en el momento de necesidad

**Pregunta de diagnóstico:** ¿La ayuda responde "cómo hacer X" o solo "qué es X"?

---

## 3. Metodología: Evaluación Heurística

### Proceso estándar
1. **Seleccionar evaluadores:** Idealmente 3-5 expertos en UX (Nielsen demostró que 1 evaluador encuentra ~35% de problemas; 5 encuentran ~75%)
2. **Definir tareas a evaluar:** Las más críticas del user journey
3. **Evaluar individualmente:** Cada evaluador revisa el sistema solo
4. **Clasificar hallazgos:** Por heurística violada
5. **Severity ratings:** Asignar severidad a cada problema

### Severity Rating Scale de Nielsen

| Rating | Descripción | Acción |
|---|---|---|
| 0 | No es problema de usabilidad | Ignorar |
| 1 | Problema cosmético | Fix solo si hay tiempo |
| 2 | Problema menor | Baja prioridad |
| 3 | Problema mayor | Alta prioridad |
| 4 | Catástrofe de usabilidad | Fix obligatorio antes de lanzar |

---

## 4. Métricas de Usabilidad

### 4.1 Las 5 dimensiones de usabilidad de Nielsen

| Dimensión | Definición | Cómo medirla |
|---|---|---|
| **Learnability** | ¿Qué tan fácil es para nuevos usuarios completar tareas básicas? | Task success rate en primera sesión |
| **Efficiency** | Una vez aprendido, ¿qué tan rápido pueden completar tareas? | Time-on-task en usuarios experimentados |
| **Memorability** | Si dejan de usar el producto, ¿qué tan rápido recuperan proficiencia? | Task success rate tras período sin uso |
| **Errors** | ¿Cuántos errores cometen? ¿Son recuperables? | Error rate + recovery rate |
| **Satisfaction** | ¿Qué tan placentero es usar el diseño? | SUS Score, NPS post-tarea |

### 4.2 System Usability Scale (SUS)
Escala de 10 ítems desarrollada por John Brooke (pero popularizada por Nielsen) para medir usabilidad percibida.

**Interpretación de scores:**

| Score | Clasificación | Percentil |
|---|---|---|
| > 80.3 | Excelente | Top 10% |
| 68 – 80.3 | Buena | Arriba del promedio |
| 68 | Promedio | Benchmark |
| 51 – 68 | Regular | Bajo promedio |
| < 51 | Pobre | Requiere rediseño urgente |

### 4.3 Task Success Rate
Porcentaje de tareas completadas sin ayuda externa.

- **Benchmark industria:** > 78% para tareas críticas
- < 50% en tarea crítica = bloqueador de lanzamiento
- Se mide con: completó vs no completó (binario), o con escala de dificultad

### 4.4 Time-on-Task
Tiempo promedio para completar una tarea específica.

- Útil como benchmark comparativo (A vs B, antes vs después)
- No tiene valor absoluto sin contexto — lo que importa es la tendencia
- Outliers (usuarios que no completan) se excluyen del cálculo o se registran como failures

---

## 5. Regla de los 5 usuarios (Discount Usability Testing)

Nielsen demostró matemáticamente que con 5 usuarios se descubren ~85% de los problemas de usabilidad. La curva de nuevos hallazgos se aplana drásticamente después del quinto usuario.

**Fórmula:** N(1-(1-L)^n) donde L es la proporción de problemas que encuentra un usuario típico (~31%)

**Implicación práctica para el #2:**
- No esperar a tener budget para 30 participantes
- Hacer múltiples rondas de 5 usuarios es más valioso que una ronda de 20
- Iterar rápido: testear → corregir → volver a testear

---

## 6. Tipos de User Research (marco Nielsen)

| Tipo | Cuándo | Método | Output |
|---|---|---|---|
| Exploratorio | Antes de diseñar | Entrevistas, observación | Necesidades, mental models |
| Generativo | Definiendo la solución | Co-design, card sorting | Arquitectura de información |
| Evaluativo | Validando el diseño | Usability testing, heurísticas | Problemas priorizados |
| Post-lanzamiento | Producto vivo | Analytics, encuestas | Áreas de mejora |

---

## 7. Aplicación directa en el flujo del Mastermind

**Aplica FUENTE-202 para:**
- Evaluación heurística de prototipos antes de pasar al Cerebro #3
- Definir métricas base de usabilidad (SUS, task success, time-on-task) para el producto
- Establecer severity ratings para problemas encontrados en research
- Diseñar el protocolo de usability testing con 5 usuarios por ronda

**Pregunta que activa esta fuente:** "¿Este diseño tiene problemas de usabilidad antes de construir?"

---

## 8. Conexiones con otras fuentes del Cerebro #2

- **FUENTE-201 (Norman):** Las heurísticas de Nielsen operacionalizan los principios conceptuales de Norman
- **FUENTE-203 (Krug):** Krug simplifica el testing de usabilidad para equipos sin recursos dedicados
- **FUENTE-209 (NN/g Articles):** Los artículos de NN/g son la actualización continua de los métodos de Nielsen
