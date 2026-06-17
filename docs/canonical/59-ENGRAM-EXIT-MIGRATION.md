# Engram Exit Migration

## 1. Propósito

Definir la estrategia de transición desde Engram hacia una Memory Layer propia de MasterMind sin romper continuidad operativa.

---

## 2. Tesis central

> No se debe reemplazar Engram con un big bang. Primero se reemplaza el contrato; después el backend.

---

## 3. Estrategia

### Fase 1 — Contract first

Introducir un contrato propio:

- `MemoryStore`
- `MemorySearchResult`
- `MemoryContextBundle`

Todo el código nuevo habla con este contrato, no con Engram.

### Fase 2 — Bridge mode

Implementaciones:

- `EngramMemoryStore`
- `PostgresMemoryStore`

Durante esta fase se puede:

- leer desde Engram
- escribir dual
- validar equivalencia

### Fase 3 — Cutover by surface

Mover progresivamente:

- session summaries
- project learnings
- decisions
- preferences
- brain feedback

### Fase 4 — Default flip

Cambiar el default a `PostgresMemoryStore`.

### Fase 5 — Retirement

Dejar Engram como:

- import path temporal
- o removerlo completamente

---

## 4. Prioridad de migración

### Primero

- resúmenes de sesión
- learnings
- fixes
- patrones

### Después

- preferencias
- decision logs
- feedback de brains

### Al final

- sync legacy
- bridges auxiliares

---

## 5. Compatibilidad

Durante transición, el sistema debe tolerar:

- memoria solo en Engram
- memoria solo en Postgres
- memoria duplicada

La lectura debe preferir:

1. memoria propia
2. fallback de bridge temporal

---

## 6. Riesgos

### Riesgo 1 — pérdida de contexto histórico

Mitigación:

- importar observaciones valiosas
- mantener bridge temporal

### Riesgo 2 — degradación de retrieval

Mitigación:

- baselines
- eval harness
- dual-run comparativo

### Riesgo 3 — mezclar runtime y memory

Mitigación:

- separar `project_state` de `memory_store`

### Riesgo 4 — rigidez frente a niches futuros

Mitigación:

- taxonomía extensible
- entidades y tipos registrables

### Riesgo 5 — construir una memoria útil solo dentro del stack completo

Mitigación:

- diseñar contratos modulares
- permitir despliegue standalone de memoria
- separar Memory API, Retrieval API y Runtime API

---

## 7. Criterios de salida de Engram

Se puede retirar Engram cuando:

1. el contrato `MemoryStore` cubra todas las operaciones necesarias
2. PostgresMemoryStore tenga parity suficiente en búsquedas y guardado
3. las suites de memoria pasen
4. los flujos activos ya no dependan de tooling Engram

---

## 8. Relación con nuevos niches y harnesses

La salida de Engram no debe diseñarse solo para software-development.

Debe dejar listo:

- registro de nuevos memory types por niche
- nuevas entidades
- nuevos retrieval scopes
- nuevos harnesses especializados

Ejemplos:

- un harness de inversiones puede necesitar `investment_thesis` y `risk_signal`
- uno de marketing puede necesitar `campaign_learning` y `channel_pattern`

La migración debe preservar esa extensibilidad desde el día 1.

---

## 9. Relación con modularidad comercial

La salida de Engram debe dejar una memoria que pueda consumirse de dos maneras:

### A. Como parte del stack completo

- brains + memory + project_state + harnesses

### B. Como módulo independiente

- memory + retrieval
- memory + niche pack
- memory + eval harness

Eso obliga a que el reemplazo no quede acoplado a un único flujo interno.

---

## 10. Resultado esperado

Pasar de una memoria externa-adaptada a una memoria nativa del framework:

- más controlable
- más evaluable
- más extensible
- más barata en tokens

## Key Learnings:

1. La salida de Engram debe ser guiada por contrato, no por reemplazo ad hoc de llamadas.
2. Dual-write y cutover gradual reducen el riesgo de perder continuidad.
3. La nueva memoria debe diseñarse para nuevos niches, nuevos cerebros y nuevos harnesses desde el principio.
4. La migración debe dejar un módulo de memoria comercializable de forma independiente o integrada.
