# Task Time and Estimation Model

## 1. Propósito

Definir cómo MasterMind mide tiempo real de trabajo, espera, bloqueo y rework, y cómo usa esos datos para estimar mejor tareas y proyectos.

---

## 2. Qué debe medir

Por tarea y subtask:

- `started_at`
- `ended_at`
- `paused_at`
- `blocked_at`
- `active_duration`
- `wall_clock_duration`
- `wait_duration`
- `rework_duration`
- actor humano o agente

---

## 3. Para qué sirve

- ETA más realista
- detectar cuellos de botella
- comparar estimado vs real
- decidir cuándo paralelizar o escalar equipo
- alimentar dashboards de throughput

---

## 4. Entidades mínimas

- `task_estimates`
- `task_time_events`
- `task_metrics`

---

## 5. Principios

1. Primero medir bien, luego predecir.
2. Tiempo activo y tiempo total no son lo mismo.
3. El rework debe modelarse explícitamente.
4. Las estimaciones deben guardar confianza y base de cálculo.

---

## 6. Evolución recomendada

### Fase 1
Heurísticas simples y medianas históricas.

### Fase 2
Percentiles por tipo de tarea, brain y proyecto.

### Fase 3
Predicción más sofisticada si ya existe buen histórico.

## Key Learnings:

1. El mejor predictor inicial es un buen historial, no un modelo complejo.
2. Tiempo, espera y rework deben separarse.
3. La estimación es una capacidad de management, no solo de reporting.
