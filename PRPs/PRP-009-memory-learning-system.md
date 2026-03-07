# PRP-009: Memory & Learning System

**Status:** Planned
**Priority:** High
**Estimated:** 4-6 hours (across 4 phases)
**Dependencies:** PRP-006 (Orchestrator), PRP-008 (Orchestrate CLI)

---

## Overview

Implementar el **Sistema de Memoria y Aprendizaje** del MasterMind Framework — una arquitectura centralizada que permite a los cerebros aprender de experiencias pasadas, capturar evaluaciones, detectar patrones, y habilitar búsqueda semántica cross-brain y cross-nicho.

---

## Vision Statement

> "El framework no solo debe responder preguntas. Debe RECORDAR lo que dijo antes, APRENDER de sus errores, y MEJORAR con cada proyecto."

**Hoy:** Los cerebros evalúan y olvidan.
**Mañana:** Los cerebros evalúan, recuerdan, y aplican aprendizaje.

---

## Objectives

### Primary (Fase 1 - Immediate Value)
1. **Evaluation Logger** — Capturar todas las evaluaciones del cerebro #7
2. **Basic Queries** — Buscar evaluaciones por proyecto, fecha, veredicto
3. **CLI Integration** — `mm eval {list, show, find}`

### Secondary (Fase 2-3 - Growth)
4. **Retention Policy** — Sistema de capas hot/warm/cold
5. **Summarization** — Auto-resumir evaluaciones viejas
6. **SQLite Migration** — Búsqueda estructurada rápida

### Tertiary (Fase 4 - Scale)
7. **Vector Database** — Búsqueda semántica con embeddings
8. **RAG Integration** — Contexto histórico en nuevas evaluaciones
9. **Cross-Brain Patterns** — Patrones que cruzan fronteras de cerebros

---

## Architecture

### Memory Structure

```
mastermind-memory/
├── evaluations/                  # Fase 1: YAML files
│   ├── hot/                      # Últimos 30 días (completo)
│   ├── warm/                     # 30-90 días (resumido)
│   ├── cold/                     # +90 días (solo patrones)
│   └── archive/                  # +1 año (comprimido)
│
├── vector-db/                    # Fase 4: Vector database
│   ├── nicho_software-development/
│   │   ├── space_brain_01_product/
│   │   ├── space_brain_02_ux/
│   │   ├── space_brain_03_ui/
│   │   ├── space_brain_04_frontend/
│   │   ├── space_brain_05_backend/
│   │   ├── space_brain_06_qa/
│   │   ├── space_brain_07_growth/
│   │   └── space_cross_brain/    # PATRONES multi-cerebro
│   │
│   ├── nicho_data-engineering/   # Futuros nichos
│   └── nicho_mobile-dev/
│
├── evaluations.db                 # Fase 3: SQLite (opcional)
│
└── config/
    ├── retention-policy.yaml
    ├── summarization-rules.yaml
    └── embedding-config.yaml
```

---

## Phase 1: Evaluation Logger (2-3 hours)

**Goal:** Capturar evaluaciones en YAML con comandos básicos.

### Directorios

```
mastermind_cli/
├── memory/
│   ├── __init__.py
│   ├── logger.py              # EvaluationLogger class
│   ├── storage.py             # YamlStorage class
│   └── models.py              # Data models (Pydantic)
│
├── commands/
│   └── eval.py                # CLI commands

logs/evaluations/hot/           # Últimos 30 días
```

### Data Model

```yaml
---
evaluation_id: "EVAL-2026-03-07-001"
timestamp: "2026-03-07T10:30:00Z"
project: "prosell-sass"
brief: "quiero una app de citas para barberos"
flow_type: "validation_only"
brains_involved: [1, 7]

evaluator:
  brain_id: 7
  brain_name: "Growth/Data"
  score:
    total: 68
    max: 156
    percentage: 44
  verdict: "CONDITIONAL"
  issues_found:
    - type: "cold-start"
      severity: "high"
      description: "No hay estrategia de adquisición"
      recommendation: "Definir primeros 100 usuarios"
  strengths_found:
    - "Propuesta de valor clara"
    - "Persona bien definida"
  tags: ["validation", "b2c", "mobile", "cold-start"]

full_output: |
  [Texto completo de la evaluación]
```

### CLI Commands

```bash
mm eval list [--limit N]              # Listar recientes
mm eval show <EVAL-ID>                # Mostrar detalle
mm eval find <project>                # Buscar por proyecto
```

---

## Phase 2: Retention Policy (2-3 hours)

**Goal:** Sistema de capas hot/warm/cold con auto-summarización.

### Retention Config

```yaml
policies:
  hot:
    max_age_days: 30
    action: "keep_full"

  warm:
    max_age_days: 90
    action: "summarize"
    summary_fields:
      - evaluation_id
      - timestamp
      - project
      - verdict
      - score
      - tags
      - key_issues_only

  cold:
    max_age_days: 365
    action: "extract_patterns"

  archive:
    action: "compress"
```

### Auto-Summarization

```python
# De 100 líneas a 5-10 líneas clave

summary:
  evaluation_id: "EVAL-2026-02-15-001-summary"
  verdict: "CONDITIONAL"
  score: 68/156 (44%)
  key_issues: ["cold-start", "omtm", "sample-size"]
  project_type: b2c-mobile
  would_recommend: false
```

---

## Phase 3: SQLite Migration (2 hours)

**Goal:** Búsqueda estructurada rápida.

### Schema

```sql
CREATE TABLE evaluations (
    evaluation_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    project TEXT NOT NULL,
    brief TEXT NOT NULL,
    verdict TEXT NOT NULL,
    score_total INTEGER NOT NULL,
    tags TEXT NOT NULL,  -- JSON array
    full_output TEXT NOT NULL
);

CREATE INDEX idx_project ON evaluations(project);
CREATE INDEX idx_verdict ON evaluations(verdict);
```

### Migration Command

```bash
mm migrate --from yaml --to sqlite
```

---

## Phase 4: Vector Database + RAG (3-4 hours)

**Goal:** Búsqueda semántica con embeddings + RAG.

### Vector Store

```python
# Buscar evaluaciones similares
results = vector_store.search_similar(
    query="quiero crear una Tinder para perros",
    space="space_brain_07_growth",
    top_k=3
)

# Results:
# - "app de citas para barberos" (0.92 similitud)
# - "plataforma de rencontres caninas" (0.85 similitud)
```

### RAG Integration

```python
# Evaluar con contexto histórico
result = evaluator.evaluate_with_rag(
    brief="quiero crear app de citas",
    context={}
)

# Prompt incluye:
# "Basado en 3 casos similares:
#  - EVAL-001 (fitness app): REJECT por cold-start
#  - EVAL-042 (gym tech): CONDITIONAL por modelo
#
# Tu evaluación:"
```

---

## Success Criteria

### Fase 1
- ✅ Evaluaciones se guardan automáticamente
- ✅ `mm eval list/show/find` funcionan
- ✅ Búsqueda por proyecto devuelve resultados

### Fase 2
- ✅ Evaluaciones viejas se resumen automáticamente
- ✅ No hay crecimiento infinito de archivos

### Fase 3
- ✅ SQLite contiene todas las evaluaciones
- ✅ Búsqueda SQL < 100ms

### Fase 4
- ✅ Búsqueda semántica encuentra casos similares
- ✅ RAG mejora calidad de evaluaciones

---

## Migration Path

```
HOY (Fase 1):
  └─ YAML + commands básicos
  └─ Costo: 2-3 horas

+3 MESES (Fase 2):
  └─ Retención hot/warm/cold
  └─ Costo: 2-3 horas

+6 MESES (Fase 3):
  └─ Migración a SQLite
  └─ Costo: 2 horas

+12 MESES (Fase 4):
  └─ Vector DB + RAG
  └─ Costo: 3-4 horas
```

---

## Next Steps

1. **Aprobar PRP-009** — Review y feedback
2. **Implementar Fase 1** — Evaluation Logger básico
3. **Testear en proyecto real** — Validar captura de datos
4. **Iterar basado en uso** — Descubrir qué falta

---

**Status:** Ready for Implementation
**Priority:** High
**Risk:** Low (evolutionary, can roll back)
