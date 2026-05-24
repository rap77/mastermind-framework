# MVP Read Model Queries

## 1. Propósito

Definir las consultas read-side mínimas que el backend debe poder resolver eficientemente para servir el dashboard MVP y las projections de agentes.

---

## 2. Tesis central

> Si el backend no puede responder rápido las preguntas operativas clave, el modelo de datos todavía no está listo para el MVP.

---

## 3. Queries mínimas

### A. Project overview query

Debe responder:

- proyecto
- status
- total tareas
- tareas activas
- tareas bloqueadas
- último checkpoint
- última decisión
- costo acumulado

### B. Task detail query

Debe responder:

- identidad de tarea
- owner actual
- status
- dependencias
- latest checkpoint
- next step
- decisiones relacionadas

### C. Active runs query

Debe responder:

- runs activos por proyecto
- actor actual
- tarea actual
- estado del run

### D. Latest checkpoint query

Debe responder:

- checkpoint más reciente por tarea
- summary
- next step
- timestamp

### E. Cost summary query

Debe responder:

- tokens por provider/modelo
- costo por proyecto
- costo por tarea
- ventana temporal seleccionada

### F. Activity feed query

Debe responder:

- eventos recientes de runs, checkpoints, decisiones y runtime

---

## 4. Principios

1. Overview y task detail son queries de primer nivel.
2. Las queries del MVP deben ser agregadas y estables.
3. El dashboard no debe reconstruir lógica crítica en frontend.
4. Las projections deben depender de estas lecturas, no de joins improvisados en cada endpoint.

---

## 5. Resultados esperados

Estas queries deben alimentar:

- Project Overview screen
- Task Detail screen
- Activity Feed
- Cost View
- Context Projection
- Doctrine Projection parcial

## Key Learnings:

1. Las queries del MVP definen en gran parte si el schema inicial es correcto.
2. Overview, task detail y cost summary son los read models más valiosos al inicio.
3. Las projections de agentes y la UI deben construirse sobre lecturas consistentes compartidas.
