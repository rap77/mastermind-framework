# Backend Service Boundary for Agents

## 1. Propósito

Definir el boundary entre agentes/modelos, tools/MCP, backend services y base de datos en MasterMind.

---

## 2. Regla central

> Los agentes no hablan con la base de datos; hablan con capacidades semánticas del backend.

---

## 3. Capas

### A. Agent Layer

Brains, agentes, orquestador y workers que necesitan leer o registrar estado.

### B. Tool Layer

Tools semánticas expuestas al agente, por MCP o interfaz interna.

### C. Service Layer

Lógica de negocio y workflow del core.

### D. Persistence Layer

Repositorios y acceso a Postgres/JSONB/pgvector.

### E. Event Layer

Emisión de eventos para realtime, auditoría y observabilidad.

---

## 4. Qué sí hacen los agentes

- pedir context projection
- pedir doctrine projection
- crear checkpoints
- registrar decisiones
- registrar handoffs
- listar tareas activas
- consultar overview de proyecto
- registrar token usage mediante service
- pausar o completar una tarea según policy

---

## 5. Qué NO hacen los agentes

- queries SQL arbitrarias
- updates genéricos por tabla
- bypass de validaciones
- escritura directa de estado crítico
- mutaciones sin generar auditoría

---

## 6. Forma correcta de las tools

### Bien
- `get_project_overview(project_id)`
- `get_task_context_projection(task_id)`
- `get_task_doctrine_projection(task_id)`
- `create_checkpoint(task_id, summary, next_step)`
- `record_decision(...)`
- `record_backend_switch(...)`

### Mal
- `run_sql(...)`
- `update_row(table, id, payload)`
- `execute_query(...)`
- `mutate_any_state(...)`

---

## 7. Responsabilidades del backend service layer

- validar reglas de negocio
- aplicar doctrine gates
- verificar permisos
- persistir transacciones consistentes
- crear audit trail
- emitir eventos realtime
- producir respuestas agregadas para UI y agentes

---

## 8. Principios

1. Tools semánticas sobre operaciones crudas.
2. Backend como autoridad de estado.
3. Auditoría por defecto.
4. Persistencia desacoplada del agente.

---

## 9. Resultado esperado

Que un agente pueda operar fluidamente sin conocer el esquema de la base ni arriesgar la consistencia del sistema.

## Key Learnings:

1. El service boundary protege consistencia, permisos y auditabilidad.
2. Las tools deben expresar intención de dominio, no detalles de almacenamiento.
3. La ergonomía agente mejora cuando las capacidades son semánticas.
