---
id: FUENTE-204
cerebro: 02-ux-research
titulo: Practical Empathy
autor: Indi Young
tipo: libro
isbn: 978-1933820583
edicion: 1st Edition
año: 2015
capa: frameworks + modelos-mentales
experto: Indi Young
habilidad: Research cualitativo profundo y mental model mapping
tags:
- empathy
- qualitative-research
- mental-models
- listening
- personas
- archetypes
- user-interviews
version_ficha: '1.0'
fecha_creacion: '2026-02-24'
source_id: FUENTE-204
brain: brain-software-02-ux-research
niche: software-development
title: Practical Empathy
author: Indi Young
type: libro
year: 2015
expert_id: EXP-204
language: en
skills_covered:
- U1
- U4
- U8
distillation_date: '2026-02-24'
distillation_quality: complete
loaded_in_notebook: true
version: 1.0.1
last_updated: '2026-02-25'
changelog:
- version: 1.0.0
  date: '2026-02-24'
  changes:
  - Destilación inicial completa
  - Campos estándar de versioning agregados
- version: 1.0.1
  date: '2026-02-25'
  changes:
  - 'Cargada en NotebookLM (Cerebro #2 UX Research)'
  - 'Notebook ID: ea006ece-00a9-4d5c-91f5-012b8b712936'
status: active
---



# FUENTE-204 — Practical Empathy
**Indi Young | Rosenfeld Media, 2015**

---

## 1. Por qué esta fuente es indispensable para el Cerebro #2

Young resuelve el problema más frecuente en UX research: confundir lo que los usuarios dicen que quieren con lo que realmente necesitan. Su método de "listening sessions" y mental model mapping va una capa más profunda que los métodos tradicionales. Es la fuente que permite al Cerebro #2 entender el contexto real, las motivaciones subyacentes y los modelos mentales del usuario — no solo sus preferencias superficiales.

---

## 2. El Problema que Resuelve

La mayoría del research captura:
- Lo que el usuario dice que quiere (declarativo)
- Lo que el usuario hace en el producto (comportamental)

Lo que falta:
- **Por qué** el usuario piensa como piensa
- Qué contexto y experiencias previas forman sus expectativas
- Qué principios guían sus decisiones (no solo sus acciones)

Young propone que la empatía real requiere entender el **razonamiento**, no solo el comportamiento.

---

## 3. Conceptos Maestros

### 3.1 La Distinción Empática
Young distingue entre dos tipos de empatía en el contexto de diseño:

**Empatía cognitiva (la que importa para UX):**
Comprender cómo piensa otra persona — su lógica, sus razones, su perspectiva — sin necesariamente compartir sus emociones.

**Empatía emocional (útil pero insuficiente):**
Sentir lo que siente otra persona. Útil para identificar pain points, insuficiente para diseñar soluciones que encajen en su modelo mental.

**Implicación del #2:** El research debe aspirar a la empatía cognitiva — entender la lógica del usuario, no solo sus frustraciones.

### 3.2 Listening Sessions (vs Entrevistas Tradicionales)
Young diferencia entre entrevistas convencionales y listening sessions:

| Entrevista Tradicional | Listening Session (Young) |
|---|---|
| Preguntas predefinidas | Guía abierta, conversacional |
| Busca confirmar hipótesis | Busca entender sin agenda |
| El researcher habla ~40% | El researcher habla ~10% |
| Respuestas sobre el producto | Respuestas sobre la vida del usuario |
| Output: preferencias | Output: modelo mental |

**El objetivo de una listening session:** Que el usuario explore en profundidad UNA situación específica de su vida relacionada con el dominio del producto.

### 3.3 Reglas de la Listening Session

**Lo que SÍ hacer:**
- Hacer preguntas de exploración ("¿Puedes contarme más sobre eso?", "¿Qué pasaba por tu cabeza en ese momento?")
- Seguir los hilos del usuario, no tu agenda
- Preguntar por comportamientos pasados específicos, no por opiniones
- Tomar notas de verbatims importantes

**Lo que NUNCA hacer:**
- Hablar sobre el producto o soluciones
- Defender o explicar el sistema actual
- Sugerir posibles razones de su comportamiento
- Hacer preguntas que impliquen respuesta ("¿No crees que sería mejor si...?")
- Interrumpir silencios demasiado pronto (esperar al menos 5 segundos)

### 3.4 Mental Model Mapping
El producto más conocido de Young es el Mental Model Diagram — una técnica para mapear el espacio mental del usuario y compararlo con las capacidades del sistema actual.

**Estructura del Mental Model Diagram:**

```
[Espacio del usuario - arriba]
Tareas | Razonamiento | Principios guía
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Espacio del sistema - abajo]
Features | Contenido | Soporte
```

**Proceso de construcción:**
1. Analizar transcripciones de listening sessions
2. Extraer "tasks" (acciones) y "reasonings" (por qué) de las palabras del usuario
3. Agrupar tareas por afinidad en "task towers"
4. Mapear debajo de cada tower qué features del sistema la cubren
5. Identificar gaps: tareas del usuario sin cobertura del sistema

**El gap es donde vive la oportunidad de diseño.**

### 3.5 De Personas a Arquetipos
Young es crítica del uso tradicional de personas con foto, nombre y edad ficticia. Los llama "marketing personas" y argumenta que generan sesgo de similitud.

**Su alternativa: Arquetipos de comportamiento**

Un arquetipo no es un perfil demográfico — es un patrón de razonamiento y comportamiento observado en múltiples usuarios.

| Persona Tradicional (problemática) | Arquetipo Young |
|---|---|
| "María, 35 años, mamá ocupada..." | "Usuario que prioriza velocidad sobre control" |
| Basada en demografía | Basada en comportamiento observado |
| Generada en workshop interno | Derivada de research real |
| Genera empatía superficial | Genera comprensión del razonamiento |

### 3.6 Principios Guía del Usuario
Young introduce el concepto de "guiding principles" — los valores o reglas no escritas que gobiernan las decisiones del usuario en un dominio.

**Ejemplo:** En finanzas personales, un principio guía puede ser "nunca gastar más de lo que tengo en cuenta, sin excepción." Este principio explica comportamientos que parecen irracionales desde afuera (como no usar crédito aunque sea más conveniente).

**Implicación para diseño:** Un producto que viola el principio guía del usuario será abandonado aunque sea objetivamente mejor. Diseñar alineado a los principios guía es más importante que agregar features.

---

## 4. Proceso de Research con el Método Young

### Fase 1 — Scope del Research
1. Definir el dominio a investigar (NO el producto — el dominio de vida del usuario)
2. Identificar qué tipo de personas (no demografía — comportamiento) incluir
3. Definir el objetivo: ¿qué decisión de diseño queremos informar?

### Fase 2 — Recruiting
- Reclutar por comportamiento, no por demografía
- 8-12 personas para un mental model diagram inicial
- Incluir usuarios en los extremos del espectro de comportamiento (no solo los "típicos")

### Fase 3 — Listening Sessions
- 60-90 minutos por sesión
- 1 moderador, 1 observador (opcional)
- Grabar con permiso
- Transcribir inmediatamente después

### Fase 4 — Análisis
1. Leer transcripciones e identificar tasks y reasonings
2. Extraer frases en "lenguaje de usuario" (no interpretar, citar)
3. Agrupar por afinidad temática
4. Construir el mental model diagram

### Fase 5 — Síntesis para Diseño
1. Identificar gaps entre modelo mental del usuario y sistema actual
2. Priorizar gaps por frecuencia y severidad
3. Generar oportunidades de diseño alineadas al modelo mental
4. Compartir con Cerebro #3 (UI Design)

---

## 5. Señales de que se necesita FUENTE-204

El Cerebro #2 debe activar el método Young cuando:
- El equipo asume que sabe lo que el usuario necesita sin haberlo investigado
- Los usuarios están usando el producto de maneras inesperadas
- El onboarding falla aunque el producto "sea obvio" para el equipo
- Las personas actuales se sienten artificiales o no orientan decisiones reales
- Hay discrepancia entre lo que los usuarios dicen en encuestas y lo que hacen en analytics

---

## 6. Herramientas del #2 derivadas de FUENTE-204

### Guía mínima de listening session (20 preguntas)
*No es un script — es un repositorio de preguntas de exploración:*

**Apertura:**
- "Cuéntame sobre la última vez que [hiciste X en tu vida cotidiana]"
- "¿Cómo es tu rutina típica cuando necesitas [dominio del producto]?"

**Exploración:**
- "¿Qué estabas tratando de lograr en ese momento?"
- "¿Qué pasaba por tu cabeza cuando [acción específica]?"
- "¿Cómo decidiste hacer eso en lugar de [alternativa]?"

**Principios guía:**
- "¿Hay cosas que para ti son no negociables cuando [dominio]?"
- "¿Cómo sabes si [resultado] fue exitoso para ti?"

**Contexto:**
- "¿Con quién más hablas cuando necesitas tomar este tipo de decisión?"
- "¿Qué pasaría si no pudieras [acción que describiste]?"

---

## 7. Aplicación directa en el flujo del Mastermind

**Aplica FUENTE-204 para:**
- Reemplazar o validar las personas del Cerebro #1 con arquetipos de comportamiento
- Construir mental model diagrams antes de definir arquitectura de información
- Identificar principios guía del usuario que el Cerebro #3 no puede violar
- Generar insight cualitativo profundo que ninguna encuesta o analítica puede capturar

**Pregunta que activa esta fuente:** "¿Realmente sabemos cómo piensa el usuario sobre este dominio, o estamos proyectando?"

---

## 8. Conexiones con otras fuentes del Cerebro #2

- **FUENTE-201 (Norman):** Los mental models de Young son la misma idea de Norman sobre modelos conceptuales, pero investigados empíricamente
- **FUENTE-207 (Fitzpatrick):** El Mom Test complementa a Young — Fitzpatrick da las reglas de la conversación, Young da el marco de análisis
- **FUENTE-208 (Torres):** Torres adapta el método de listening de Young a un ciclo semanal continuo en equipos de producto
