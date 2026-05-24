# Token, Cost and Quality Telemetry

## 1. Propósito

Definir la telemetría mínima para observar uso de tokens, costos y calidad a través de proveedores, modelos, proyectos, tareas y runs.

---

## 2. Qué debe registrar

Por evento de uso:

- provider
- model
- auth_mode
- prompt_tokens
- completion_tokens
- cached_tokens si aplica
- estimated_cost
- project_id
- task_id
- run_id
- agent_id o brain_id
- timestamp

---

## 3. Qué más debe medir

### Calidad
- review pass/fail
- verification pass/fail
- rework rate
- reopened tasks
- defect signals

### Eficiencia
- costo por tarea
- costo por proyecto
- costo por provider/model
- costo por output útil

---

## 4. Principios

1. Tokens sin contexto de tarea sirven poco.
2. Costos deben leerse junto a calidad y tiempo.
3. La telemetría debe permitir comparar proveedores y estrategias.
4. Debe alimentar dashboards y alertas.

---

## 5. Vistas objetivo

- costo por proyecto
- costo por tarea
- tokens por proveedor/modelo
- costo vs calidad
- costo vs throughput

## Key Learnings:

1. El costo debe analizarse junto a tarea, calidad y tiempo, no en aislamiento.
2. La telemetría es clave para decidir runtime strategy y metodología.
3. Comparar proveedores requiere trazabilidad fina por run y por tarea.
