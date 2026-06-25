# Tech Stack Decisions — UOW-1 Governance Core

## Decision Summary

UOW-1 se implementará primero en Python, dentro del stack actual de `apps/api/mastermind_cli/orchestrator/`, con persistencia MVP file-based append-only y diseño listo para migraciones futuras sin acoplar el `Coordinator`.

## 1. Runtime Language

### Decision
Usar **Python** para el primer release del governance harness.

### Rationale
- El requirement FR-10 fija Python-first para esta capa.
- El `Coordinator` actual ya vive en el stack Python.
- Reduce riesgo de integración y evita introducir una frontera Rust prematura.

## 2. Integration Pattern

### Decision
Usar **constructor injection** y un **interceptor/middleware class** separado del `Coordinator`.

### Rationale
- Preserva backward compatibility.
- Permite `governance=None` en tests o callers legacy.
- Mantiene la frontera del cambio pequeña y explícita.

## 3. Policy Execution Model

### Decision
Usar **PolicySet ordenado en memoria** con evaluación secuencial y short-circuit.

### Rationale
- Favorece determinismo y costo predecible.
- Hace observable el orden de evaluación.
- Simplifica pruebas unitarias e integración.

## 4. Evidence Persistence MVP

### Decision
Usar **JSON Lines append-only** para `AuditEvent` en el MVP.

### Rationale
- Fue la decisión ya tomada en inception para evidencia y continuidad.
- Permite inspección humana simple, parseo por tooling y reanudación sin DB obligatoria.
- Mantiene abierta una migración futura a PostgreSQL sin cambiar el contrato lógico.

## 5. Redaction Boundary

### Decision
Redactar secretos antes de persistir evidencia, no después.

### Rationale
- Minimiza riesgo de fuga en logs/archivos.
- Mantiene la persistencia como sink seguro por defecto.

## 6. Testing Stack

### Decision
Cubrir UOW-1 con **tests unitarios por policy** + **tests de integración del interceptor** usando el stack de tests Python existente.

### Rationale
- Se alinea con NFR de testabilidad aislada.
- Permite probar short-circuit, orden estable y fail-closed del audit writer.

## 7. Infra Dependencies

### Decision
No introducir dependencias de red ni infraestructura adicional en el camino crítico de UOW-1.

### Rationale
- Governance debe operar aun cuando otros servicios no estén disponibles.
- Reduce latencia y evita puntos extra de falla.

## 8. Future Migration Boundary

### Decision
Mantener una frontera explícita para posible migración futura de enforcement o persistence, pero sin diseñar para Rust de forma especulativa.

### Rationale
- El roadmap permite extraer piezas a Rust solo si la medición futura lo justifica.
- Evita sobre-arquitectura en el MVP.
