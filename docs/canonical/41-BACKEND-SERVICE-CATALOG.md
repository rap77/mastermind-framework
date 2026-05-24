# Backend Service Catalog

## 1. Propósito

Definir el catálogo inicial de servicios backend que implementan la lógica del thin slice MVP y sirven de base para tools de agentes y API.

---

## 2. Tesis central

> Los servicios backend deben encapsular la lógica reusable del dominio y servir como frontera estable entre persistencia, API, realtime y tools de agentes.

---

## 3. Servicios iniciales recomendados

### A. ProjectOverviewService

Responsable de:

- construir overview del proyecto
- agregar métricas básicas
- exponer estado global para dashboard

### B. TaskService

Responsable de:

- obtener task detail
- listar tareas por proyecto
- resolver dependencias

### C. CheckpointService

Responsable de:

- crear checkpoint
- obtener latest checkpoint
- construir continuidad mínima

### D. DecisionService

Responsable de:

- registrar decision record
- listar decisiones recientes
- obtener decision detail

### E. TelemetryService

Responsable de:

- registrar token usage
- construir cost summaries
- soportar comparativas por provider/modelo

### F. ContextProjectionService

Responsable de:

- construir task context projection
- empaquetar artefactos, estado, decisiones y next step

### G. DoctrineProjectionService

Responsable de:

- construir doctrine projection
- combinar doctrine global, proyecto, nicho y task policy

### H. ActivityFeedService

Responsable de:

- construir feed reciente
- agregar eventos relevantes

---

## 4. Principios

1. Un servicio por responsabilidad dominante.
2. Reutilizable por API, WebSocket y tools.
3. Validaciones y auditoría en services, no en controllers.
4. Los servicios no deben exponer detalles del schema al agente.

---

## 5. Orden recomendado de implementación

### Primera ola
- ProjectOverviewService
- TaskService
- CheckpointService
- TelemetryService

### Segunda ola
- DecisionService
- ContextProjectionService
- DoctrineProjectionService
- ActivityFeedService

---

## 6. Relación con tools

Las tools de agentes deben mapear casi 1:1 a estos servicios o a métodos dentro de ellos.

## Key Learnings:

1. El service catalog convierte la arquitectura en piezas implementables.
2. Overview, tasks, checkpoints y telemetry forman la primera ola correcta.
3. Context y doctrine projection deben ser servicios explícitos, no helpers dispersos.
