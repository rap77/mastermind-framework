# MVP Dashboard Screen Map

## 1. Propósito

Definir el mapa mínimo de pantallas del dashboard MVP para que humanos puedan observar y gobernar proyectos en MasterMind.

---

## 2. Tesis central

> El dashboard MVP debe permitir comprender estado, continuidad, costo y decisiones sin obligar a navegar múltiples herramientas o logs.

---

## 3. Pantallas mínimas

### A. Projects List

Debe mostrar:

- proyectos disponibles
- status general
- última actividad
- costo acumulado básico
- ETA básica si existe

### B. Project Overview

Debe mostrar:

- resumen general
- tareas activas
- tareas bloqueadas
- último checkpoint
- última decisión
- costo total
- backend/run activo si existe

### C. Tasks View

Debe mostrar:

- lista o board de tareas
- estado
- owner actual
- dependencias
- posibles bloqueos

### D. Task Detail

Debe mostrar:

- objetivo
- status
- owner
- dependencias
- último checkpoint
- next step
- decisiones relacionadas
- costo/tiempo básicos

### E. Activity Feed

Debe mostrar:

- eventos recientes
- cambios de tarea
- checkpoints
- decisiones
- switches de backend
- bloqueos

### F. Cost View

Debe mostrar:

- tokens por proveedor/modelo
- costo por proyecto
- costo por tarea
- tendencia simple temporal

### G. Decision View

Debe mostrar:

- decisiones recientes
- status
- rationale breve
- links a tareas afectadas

---

## 4. Flujo recomendado del usuario

1. entrar por Projects List
2. abrir Project Overview
3. ir a Tasks o Activity según necesidad
4. abrir Task Detail si necesita retomar o intervenir
5. revisar Cost o Decisions si hay señales anómalas

---

## 5. Principios UX

1. Priorizar next action.
2. Mostrar bloqueos claramente.
3. Permitir drill-down rápido desde resúmenes.
4. Mantener separación entre overview ejecutivo y detalle técnico.

---

## 6. Qué dejar fuera del MVP

- visualizaciones densas tipo graph compleja avanzada
- replay completo
- edición profunda de doctrine
- simulación de runtime policies

---

## 7. Señal de éxito

El dashboard MVP funciona si un humano puede, en menos de 3 minutos:

- entender el estado del proyecto
- detectar qué está corriendo o bloqueado
- identificar dónde retomar
- ver gasto básico y decisiones recientes

---

## 8. Próximos artefactos recomendados

1. `38-AGENT-TOOLS-CATALOG.md`
2. `39-INITIAL-MIGRATION-BREAKDOWN.md`
3. `40-MVP-READ-MODEL-QUERIES.md`

## Key Learnings:

1. El MVP necesita pocas pantallas, pero muy enfocadas.
2. Project Overview y Task Detail son las dos vistas más críticas.
3. La UI debe reducir tiempo de comprensión y retoma, no solo verse bien.
