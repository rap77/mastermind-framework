# External Project Adoption Model

## 1. Objetivo

Definir cómo MasterMind debe usarse en proyectos externos o nuevos sin copiar caóticamente todo el repo ni romper la evolución del core.

## 2. Principio central

> MasterMind debe usarse como **Core + Project Adapter**, no como un monolito replicado manualmente proyecto por proyecto.

## 3. Qué es el Core

El **Core** contiene capacidades generales y reutilizables que sirven a múltiples proyectos.

### El Core incluye

- brains y brain specs reutilizables
- documentación canónica
- protocolos multi-brain
- Brain Factory
- plantillas
- reglas de memoria
- modelos de decisión
- principios de adopción

## 4. Qué es el Project Adapter

El **Project Adapter** contiene el contexto específico de un proyecto concreto.

### El Project Adapter incluye

- contexto del proyecto
- nicho
- restricciones locales
- stack técnico
- integraciones específicas
- reglas del dominio
- project-local knowledge
- decisiones específicas del proyecto

## 5. Regla de separación

### Sube al Core si:

- generaliza a múltiples proyectos
- mejora el protocolo
- mejora las plantillas
- mejora los brains de forma reusable
- mejora runtime o memory de manera general

### Se queda en el Project Adapter si:

- solo sirve a ese proyecto
- depende de una API o negocio específico
- responde a una excepción local
- no ha demostrado ser reusable

## 6. Flujo de adopción externa

```text
New Project
→ Define project context
→ Select existing brains
→ Detect missing expertise
→ Create project adapter
→ Run multi-brain workflow
→ Capture decisions and learning
→ Promote reusable improvements back to core
```

## 7. Qué debe poder hacer MasterMind en un proyecto externo

- entender el contexto del proyecto
- elegir brains relevantes
- crear nuevos brains si faltan
- coordinar decisiones reales
- dejar trazabilidad
- capturar aprendizaje
- devolver mejoras al core

## 8. Artefactos mínimos por proyecto externo

### A. Project Context

- objetivo
- nicho
- stack
- restricciones
- riesgos

### B. Brain Topology

- qué brains participan
- roles
- rights / veto / gates

### C. Decision Records

- decisiones tomadas
- objeciones
- gates
- outcomes

### D. Learning Capture

- observaciones
- patrones
- heurísticas candidatas

## 9. Project Lifecycle with MasterMind

### Step 1 — Project Initialization

Definir contexto, nicho y constraints.

### Step 2 — Brain Selection

Usar brains existentes o detectar faltantes.

### Step 3 — Workflow Execution

Aplicar protocolo multi-brain.

### Step 4 — Delivery / Action

Producir decisiones, planes, specs o implementación.

### Step 5 — Learning Extraction

Guardar aprendizajes locales.

### Step 6 — Core Promotion Review

Evaluar qué cambios deben volver al core.

## 10. Promotion Back to Core

Cada proyecto externo debe responder:

1. ¿Qué funcionó que sirve a todos?
2. ¿Qué brain mejoró de forma reusable?
3. ¿Qué template faltó?
4. ¿Qué protocolo necesitó ajuste?
5. ¿Qué parte es solo local y no debe contaminar el core?

## 11. Riesgos a evitar

- copiar todo MasterMind en cada repo
- no separar core de project-local logic
- subir al core mejoras no generalizadas
- dejar aprendizajes atrapados en un proyecto
- usar MasterMind sin trazabilidad

## 12. MVP Adoption Target

El MVP queda validado cuando:

- MasterMind funciona en al menos un proyecto externo real
- deja artefactos útiles
- captura aprendizaje
- y ese aprendizaje mejora el core

## 13. Decisión canónica

> MasterMind debe adoptarse externamente como un sistema Core + Project Adapter, donde cada proyecto sirve como entorno real de validación y mejora continua del framework.
