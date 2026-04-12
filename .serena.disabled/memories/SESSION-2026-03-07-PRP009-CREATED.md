# Session 2026-03-07 - PRP-009 Memory & Learning System Created ✅

## Status: Planning Complete

**File Created:** `PRPs/PRP-009-memory-learning-system.md`

## What Was Designed

### Sistema de Memoria y Aprendizaje Completo

Arquitectura en 4 fases para que los cerebros aprendan de experiencias:

#### Fase 1: Evaluation Logger (2-3 hours)
- Capturar todas las evaluaciones del cerebro #7
- Guardar en YAML estructurado
- CLI commands: `mm eval {list, show, find}`
- **Valor inmediato:** Memoria del sistema

#### Fase 2: Retention Policy (2-3 hours)
- Sistema de capas: hot/warm/cold/archive
- Auto-summarización de evaluaciones viejas
- Extracción de patrones desde casos repetidos
- **Resuelve:** Crecimiento infinito de archivos

#### Fase 3: SQLite Migration (2 hours)
- Migración desde YAML a SQLite
- Búsqueda estructurada rápida (< 100ms)
- Comando: `mm migrate --from yaml --to sqlite`
- **Resuelve:** Performance en búsquedas

#### Fase 4: Vector Database + RAG (3-4 hours)
- Búsqueda semántica con embeddings
- RAG: Contexto histórico en nuevas evaluaciones
- Patrones cross-brain y cross-nicho
- **Resuelve:** "¿Alguien ya evaluó algo PARECIDO a esto?"

## Key Design Decisions

### 1. Una BD Centralizada con Spaces
- NO separar BD por cerebro
- Usar UNA BD vectorial con "spaces" por cerebro
- Permite búsqueda cross-brain

### 2. Memoria por Capas (como la humana)
```
hot/   → Últimos 30 días (YAML completo)
warm/  → 30-90 días (YAML resumido)
cold/  → +90 días (Solo patrones)
archive/ → +1 año (Comprimido)
```

### 3. Data Model Unificado
```yaml
evaluation_id: "EVAL-2026-03-07-001"
timestamp: "..."
project: "..."
verdict: "CONDITIONAL"
score: {total: 68, max: 156, percentage: 44}
issues_found: [...]
strengths_found: [...]
tags: [...]
```

### 4. Ruta de Migración Clara
- YAML → SQLite → Vector DB
- Cada fase es opcional
- Se puede migrar cuando haga falta

## Architecture Highlights

### Memory Structure
```
mastermind-memory/
├── evaluations/
│   ├── hot/       # Últimos 30 días
│   ├── warm/      # 30-90 días (resumido)
│   ├── cold/      # +90 días (patrones)
│   └── archive/   # +1 año (comprimido)
│
├── vector-db/
│   ├── nicho_software-development/
│   │   ├── space_brain_01_product/
│   │   ├── space_brain_02_ux/
│   │   ├── ...
│   │   └── space_cross_brain/  # Multi-cerebro
│   │
│   ├── nicho_data-engineering/  # Futuros nichos
│   └── nicho_mobile-dev/
│
└── evaluations.db  # SQLite (Fase 3)
```

### Cross-Brain Patterns
```yaml
cross_pattern_id: "CROSS-001"
pattern: "SaaS B2B sin onboarding = 90% churn"
brains_involved: [1, 2, 6, 7]
confidence: 0.92
recommendation: |
  Si detectas B2B SaaS early-stage:
  - Cerebro #1: Preguntar estrategia onboarding
  - Cerebro #2: Diseñar journey de onboarding
  - Cerebro #6: Definir métricas de activación
```

## CLI Commands (Full)

```bash
# Fase 1: Evaluations
mm eval list [--limit N]
mm eval show <EVAL-ID>
mm eval find <project>

# Fase 2: Retention
mm retention run [--dry-run]
mm retention status

# Fase 3: Migration
mm migrate --from yaml --to sqlite

# Fase 4: Vector Search
mm vector search "app de citas"
mm vector similar <EVAL-ID>
mm vector patterns --confidence 0.8
mm vector rag --enable
```

## Open Questions

1. **¿Qué modelo de embeddings?**
   - OpenAI `text-embedding-3-small` ($0.02/1M tokens)
   - O local: `sentence-transformers` (gratis)

2. **¿Cuándo activar RAG?**
   - Esperar +100 evaluaciones en BD?

3. **¿Persistir embeddings o recrear?**
   - Guardar en YAML (más espacio, más rápido)
   - O recrear on-demand (más lento, más fresco)

## Next Steps

1. ✅ PRP-009 creado y documentado
2. ⏳ Aprobación del usuario
3. ⏳ Implementar Fase 1 (Evaluation Logger)
4. ⏳ Testear en proyecto real
5. ⏳ Iterar basado en feedback

## Framework Status Post-PRP-009

| Componente | Status |
|------------|--------|
| CLI v1.0.0 | ✅ Complete |
| 7 Cerebros | ✅ Active (122 sources) |
| Orchestrate Command | ✅ Functional |
| Testing Suite | ✅ 5/5 passing |
| Installation | ✅ Working |
| README v1.0.0 | ✅ Production Ready |
| **Memory System** | ⏳ **PRP-009 Planned** |
