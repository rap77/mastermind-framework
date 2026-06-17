# Requirements — memory-layer-v1

## Problem / Purpose

MasterMind depende hoy de Engram como memoria persistente externa para parte de su continuidad y aprendizaje. Eso impide ownership total, complica la extensibilidad por niche y deja la memoria fuera del modelo modular/comercializable del framework.

El objetivo de `memory-layer-v1` es introducir una capa propia de memoria con contrato estable, backend Postgres inicial y bridge temporal a Engram.

## Stakeholders / Users

- **Primary:** maintainers del framework y futuros módulos `memory`, `retrieval`, `brains`
- **Secondary:** operadores humanos, Brain #7, Strategy Vault, futuros niche packs

## Scope

### In Scope

- definir e implementar un contrato propio `MemoryStore`
- introducir modelos internos de memoria
- encapsular Engram detrás de un adapter
- construir un `PostgresMemoryStore` mínimo viable
- migrar primeras superficies:
  - session summaries
  - learnings / fixes / patterns
  - preferences operativas
- dejar preparada la base para retrieval híbrido posterior

### Out of Scope

- grafo completo de memoria
- reranker
- eval harness completo
- cutover total de Engram
- niche packs concretos de inversiones o marketing

## Non-negotiables

- La memoria propia no debe colapsarse con `project_state`.
- Ningún flujo nuevo debe hablar directo con Engram.
- La arquitectura debe soportar modularidad tipo lego:
  - standalone
  - integrada
  - empaquetable por capability o niche
- El diseño debe ser extensible a nuevos niches y nuevos cerebros.
- No introducir sobreingeniería: este slice cubre contrato + store mínimo, no la solución final completa.

## Objective-level Acceptance Criteria

- [ ] Existe un contrato `MemoryStore` que abstrae el backend de memoria.
- [ ] Existe un adapter `EngramMemoryStore` que encapsula la integración actual.
- [ ] Existe un `PostgresMemoryStore` mínimo viable para items, session summaries y preferences.
- [ ] Las primeras superficies migradas ya no dependen conceptualmente de Engram.
- [ ] El diseño sigue siendo compatible con extensibilidad por niche y modularización futura.
