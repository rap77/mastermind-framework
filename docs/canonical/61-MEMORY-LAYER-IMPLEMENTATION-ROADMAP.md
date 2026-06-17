# Memory Layer Implementation Roadmap

## 1. Propósito

Traducir la arquitectura canónica de Memory Layer a un roadmap ejecutable por fases, con entregables, verificaciones y criterios de corte.

---

## 2. Tesis central

> La salida de Engram y la construcción de una memoria propia deben hacerse como una secuencia de cortes pequeños: primero contrato, luego storage, luego retrieval, luego graph, luego evaluación, y recién al final el cutover.

---

## 3. Objetivo del roadmap

Construir una Memory Layer propia de MasterMind que:

- reemplace Engram progresivamente
- reduzca tokens y dependencia de contexto bruto
- sea extensible por niche
- sea modular/comercializable
- tenga evaluación reproducible

---

## 4. Fases

## Phase 0 — Canonicalization and boundary freeze

### Goal

Congelar vocabulario, límites y ownership antes de implementar más código.

### Entregables

- docs canónicos 55–60 publicados
- glosario de capas: session / runtime / memory / retrieval
- decisión formal de que Engram deja de ser contrato primario

### Verificación

- arquitectura aprobada a nivel de docs
- no nuevas features que hablen directo con Engram

---

## Phase 1 — Memory API abstraction

### Goal

Introducir un contrato propio de memoria.

### Entregables

- interfaz `MemoryStore`
- modelos base:
  - `MemoryItem`
  - `MemorySearchResult`
  - `MemoryContextBundle`
- adapter `EngramMemoryStore`

### Superficies a migrar primero

- session summaries
- learnings
- preferences
- decision summaries

### Verificación

- flujos existentes compilan y funcionan usando el contrato nuevo
- ninguna ruta nueva consume herramientas Engram directamente

---

## Phase 2 — Postgres memory store minimum viable

### Goal

Crear el backend propio mínimo de memoria.

### Entregables

- tablas iniciales de memoria
- `PostgresMemoryStore`
- save/get/list/search básico
- scope por:
  - project
  - brain
  - niche
  - visibility

### Tablas mínimas sugeridas

- `mm_memory_items`
- `mm_memory_sources`
- `mm_memory_links`
- `mm_memory_sessions`
- `mm_memory_preferences`

### Verificación

- guardar y recuperar items sin Engram
- dual-write opcional Engram/Postgres funcionando

---

## Phase 3 — Ingestion and projection

### Goal

Proyectar memoria útil desde señales ya existentes del framework.

### Entregables

- projection jobs desde:
  - task_runs
  - checkpoints
  - decisions
  - artifacts
  - Brain #7 feedback
  - session summaries
- taxonomy routing inicial

### Primeros tipos a poblar

- `decision`
- `lesson`
- `fix`
- `incident`
- `project_summary`
- `brain_feedback`

### Verificación

- runs reales generan memoria utilizable
- el historial reciente del proyecto ya se puede reconstruir desde Memory Layer

---

## Phase 4 — Hybrid retrieval v1

### Goal

Pasar de vector-only a retrieval híbrido mínimo.

### Entregables

- pgvector search
- full-text / BM25
- RRF fusion
- source scoping
- response shape con evidence básica

### Fuentes iniciales

- `project_memory`
- `knowledge_memory`
- `decision_memory`

### Verificación

- mejora medible contra vector-only
- resultados explicables por fuente

---

## Phase 5 — Graph over project_state and memory

### Goal

Agregar relaciones útiles para contexto y reasoning.

### Entregables

- nodos y edges mínimos
- graph query inicial
- relational recall básico

### Relaciones iniciales

- task → run
- run → artifact
- decision → artifact
- decision → task
- memory_item → decision
- memory_item → niche_entity

### Verificación

- queries relacionales básicas responden mejor que vector-only
- Strategy Vault / Brain #7 pueden consumir esas relaciones

---

## Phase 6 — Eval harness

### Goal

Volver la memoria medible y resistente a regresiones.

### Entregables

- qrels sellados iniciales
- baselines versionados
- scorecards
- suites de:
  - retrieval
  - temporal
  - provenance
  - source isolation
  - think vs search

### Verificación

- baseline público dentro del repo
- nuevos cambios comparables contra baseline

---

## Phase 7 — Engram cutover

### Goal

Cambiar el default a memoria propia.

### Entregables

- read path por defecto → PostgresMemoryStore
- write path por defecto → PostgresMemoryStore
- bridge Engram solo fallback o import

### Verificación

- parity suficiente para flujos activos
- suites de memoria en verde
- sin dependencias críticas en tooling Engram

---

## Phase 8 — Niche packs and modularization

### Goal

Hacer extensible la memoria a nuevos nichos y empaquetados.

### Entregables

- registro de `memory_type` extensible
- registro de entity types por niche
- retrieval policies por niche
- eval packs por niche

### Niches iniciales previstos

- software-development
- finanzas / inversiones
- marketing / digital

### Verificación

- un niche nuevo puede agregar tipos y retrieval sin tocar el core

---

## 5. Orden recomendado de implementación

1. Phase 1
2. Phase 2
3. Phase 3
4. Phase 4
5. Phase 6
6. Phase 7
7. Phase 5
8. Phase 8

### Nota

El grafo es muy valioso, pero no debe bloquear el reemplazo inicial de Engram.

---

## 6. Quick wins tempranos

### Quick win A

Session summaries sobre `MemoryStore`

### Quick win B

Lessons learned + fixes sobre PostgresMemoryStore

### Quick win C

Retrieval híbrido solo para `project_memory`

### Quick win D

Suite mínima de qrels sobre decisiones y fixes

---

## 7. Riesgos de implementación

### Riesgo 1

Construir demasiada generalidad antes de tener uso real.

### Mitigación

empezar con software-development como niche semilla.

### Riesgo 2

Confundir runtime state con memory state.

### Mitigación

mantener `project_state` separado del store de memoria.

### Riesgo 3

Intentar copiar GBrain entero.

### Mitigación

importar patrones, no producto completo.

### Riesgo 4

No medir calidad de retrieval.

### Mitigación

introducir el eval harness antes del cutover total.

---

## 8. Resultado esperado

Al final del roadmap, MasterMind debería poder ofrecer:

- memoria propia persistente
- retrieval más barato y útil
- continuidad fuerte entre sesiones
- base reusable para nuevos niches
- módulo vendible standalone o integrado

## Key Learnings:

1. La migración correcta sale por contrato → storage → ingestion → retrieval → evaluación → cutover.
2. El reemplazo de Engram no debe bloquearse por graph sophistication; primero importa poseer el contrato y el dato.
3. La extensibilidad por niche y la modularización comercial deben influir en el roadmap desde el principio.
