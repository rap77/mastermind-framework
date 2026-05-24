# Dashboard Information Architecture

## 1. Propósito

Definir la estructura de información mínima para la UI que permitirá a humanos observar, entender y gobernar el estado de proyectos manejados por MasterMind.

---

## 2. Tesis central

> El dashboard no debe ser solo un panel visual; debe ser la interfaz humana principal para revisar estado, costos, decisiones, bloqueos y continuidad operativa.

---

## 3. Preguntas que el dashboard debe responder

### Estado
- ¿qué proyecto está activo?
- ¿qué tarea se está ejecutando ahora?
- ¿quién la está ejecutando?
- ¿qué está bloqueado?

### Continuidad
- ¿cuál es el último checkpoint?
- ¿qué pasó en la última pausa?
- ¿qué sigue si retomamos ahora?

### Decisiones
- ¿qué decisiones se tomaron?
- ¿quién las tomó o influenció?
- ¿qué reglas o criterios aplicaron?

### Costos y tiempo
- ¿cuántos tokens/costo llevamos?
- ¿en qué se gastaron?
- ¿cuánto tiempo real tomó cada tarea?
- ¿cómo vamos vs estimado?

### Runtime
- ¿qué backend/modelo está activo?
- ¿hubo switches?
- ¿qué ventanas están agotadas o disponibles?

---

## 4. Vistas mínimas recomendadas

### A. Project Overview

Debe mostrar:

- nombre del proyecto
- estado general
- progreso global
- tareas activas
- blockers principales
- ETA real vs estimada
- costo acumulado

### B. Task Board / Graph

Debe mostrar:

- tareas
- subtareas
- estados
- dependencias
- posibles paralelismos
- ownership

### C. Live Activity Feed

Debe mostrar:

- runs recientes
- agentes/humanos activos
- switches de backend
- checkpoints creados
- pausas y bloqueos
- decisiones recientes

### D. Decision Timeline

Debe mostrar:

- decisiones tomadas
- status
- rationale breve
- brains/humanos involucrados
- impacto en tareas relacionadas

### E. Cost and Token View

Debe mostrar:

- tokens por provider/modelo
- costo por proyecto
- costo por tarea
- evolución temporal
- costo vs calidad

### F. Context & Checkpoint View

Debe mostrar:

- último checkpoint por tarea
- resumen operativo
- next step
- open questions
- artefactos relacionados

---

## 5. Jerarquía de navegación sugerida

### Nivel 1
Selector de proyecto

### Nivel 2
Tabs principales:
- Overview
- Tasks
- Activity
- Decisions
- Cost
- Context

### Nivel 3
Drill-down por:
- tarea
- run
- decisión
- participante
- backend

---

## 6. Principios UX

1. Priorizar estado actual y next action.
2. Reducir necesidad de abrir muchos paneles para entender bloqueos.
3. Separar resumen ejecutivo de detalle técnico.
4. Todo evento importante debe ser navegable hasta su fuente.
5. La UI debe servir igual a operador técnico y owner del proyecto.

---

## 7. Información crítica en tiempo real

El dashboard debe poder actualizar en tiempo casi real:

- tarea activa
- actor activo
- backend activo
- switches
- bloqueos
- checkpoints nuevos
- costo acumulado de la sesión

---

## 8. Información histórica mínima

Debe poder navegar historial de:

- runs
- decisiones
- cambios de estado
- uso de tokens
- variación contra estimados

---

## 9. Qué NO hacer en la primera versión

- querer mostrar todo a la vez
- construir visualizaciones complejas antes de tener estado confiable
- depender de logs crudos como UI principal
- esconder bloqueos o excepciones en vistas secundarias

---

## 10. Resultado esperado

La primera versión del dashboard debería permitir que un humano pueda, en pocos minutos:

- entender dónde está el proyecto
- ver qué está corriendo o bloqueado
- identificar qué cuesta más
- retomar una tarea con contexto suficiente
- revisar decisiones recientes

---

## 11. Próximos artefactos recomendados

1. `31-DOCTRINE-PROJECTION-FORMAT.md`
2. `32-INITIAL-API-SURFACE.md`
3. `33-DASHBOARD-REALTIME-EVENTS.md`

## Key Learnings:

1. El dashboard debe responder preguntas operativas reales, no solo mostrar datos bonitos.
2. Overview, Tasks, Activity, Decisions, Cost y Context forman la mínima arquitectura informacional útil.
3. El verdadero valor de la UI está en reducir tiempo de comprensión y retoma del proyecto.
