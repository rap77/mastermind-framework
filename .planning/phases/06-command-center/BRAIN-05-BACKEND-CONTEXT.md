# brain-05 (Backend) — Phase 06 Command Center Consultation

**Date:** 2026-03-20
**Brain:** brain-05-backend
**Notebook:** c6befbbc-b7dd-4ad0-a677-314750684208

---

## Architecture

**Clean Architecture:** 4 capas concéntricas, dependencias hacia adentro.
- Entity (Cerebro): Reglas de negocio
- Use Case: Orquesta recuperación
- Controller: Traduce HTTP
- Framework: FastAPI

**Screaming Architecture:** Estructura refleja dominio (/brains).

---

## API Design

**GET /v1/api/brains** con paginación opcional (?limit=24&cursor=xyz)

Para 24 brains: all-at-once aceptable HOY, pero incluir paginación para escalabilidad.

**Versionado:** /v1/ para evitar deuda técnica.

---

## Data Models

### Brain (Entity)
- id (UUID), name, niche
- Lógica: Aptitud para tarea

### BrainStatusUpdate (Value Object)
- status (Enum: active/idle/offline)
- uptime, last_called_at
- **sequence_number (bigint)** — CRITICAL para orden en sistemas distribuidos

### CommandCenterRegistry (Aggregate)
- registry_id, total_brains_count, active_sessions
- Unidad de consistencia

---

## Authentication

**JWT RS256:**
- Clave pública en FastAPI (verify)
- Clave privada aislada (sign)
- Expiración: 15-60 min
- Validar iat/exp en cada request

---

## Answers to Questions

### Q1: ¿24 brains simultáneos o paginado?
**All-at-once aceptable HOY** pero incluir paginación para escalabilidad. Margin of Safety.

### Q2: ¿Tamaño seguro de payload?
**Fermi Estimation:** Si brains se duplican (48) + metadata crece, payload puede saturar. Paginación desde inicio.

### Q3: ¿sequence_number en WebSocket?
**CRITICAL.** Cada event tiene sequence_number monotónico. Cliente descarta <= last_seen.

### Q4: ¿Caching?
**NO cachear get_all_brains().** Siempre fresh data. WebSocket = cache (delta updates).

---

## Margin of Safety

**Inversion:** ¿Cuándo fallará get_all_brains()?
- Cuando brains * metadata > capacidad
- **Solución:** Paginación basada en cursores desde el inicio

---

*Saved: 2026-03-20*
