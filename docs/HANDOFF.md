# Handoff Document — MasterMind Framework

**Última actualización:** 2026-02-25
**Sesión:** Testing Suite Completo + Cerebro #7 NotebookLM Cargado
**Estado:** Framework Core + 3 Cerebros Activos ✅

---

## Para Continuar en Próxima Sesión

### Paso 1: Activar Proyecto y Recuperar Contexto

```bash
# Entrar al directorio
cd /home/rpadron/proy/mastermind

# Verificar rama
git branch  # Debe estar en master

# Verificar estado
git status  # Debe estar clean
```

### Paso 2: Cargar Memorias de Serena

| Memoria | Propósito |
|---------|-----------|
| `MEMORY.md` | Estado general del proyecto |
| `session/2026-02-25-brain-testing-complete` | Testing suite completo (4 tests) |
| `session/2025-02-25-testing-brains` | Tests de cerebros activos |

**Para cargar contexto al iniciar sesión:**
1. Leer `MEMORY.md` para overview
2. Leer `session/2026-02-25-brain-testing-complete` para resultados de tests

---

## Estado Actual del Proyecto

### PRPs Completados ✅

| PRP | Descripción | Status | Commit |
|-----|-------------|--------|--------|
| PRP-000 | Initial Setup | ✅ | ac1696a |
| PRP-001 | mastermind-cli | ✅ | b050e22 |
| PRP-002 | YAML Versioning | ✅ | (completado) |
| PRP-003 | System Prompts | ✅ | - |
| PRP-004 | NotebookLM Integration | ✅ | 254f108 |
| PRP-005 | Brain #7 Evaluator | ✅ | 286efb8 |
| PRP-006 | Orchestrator | ✅ | 4873faf |
| PRP-008 | CLI Orchestrate | ✅ | bb1ec26 |

### Cerebros Activos ✅

| Cerebro | Estado | NotebookLM | Testing |
|---------|--------|------------|---------|
| **#1 Product Strategy** | ✅ Activo | f276ccb3 (10 sources) | ✅ Validated |
| **#2 UX Research** | ✅ Activo | - | ✅ Validated |
| **#7 Growth/Data** | ✅ Activo | d8de74d6 (10 sources) | ✅ Validated |

### Cerebros Pendientes ⏳

| Cerebro | Prioridad | Estimated |
|---------|----------|-----------|
| #3 UI Design | High | Usuario cargando fuentes |
| #4 Frontend | Medium | 2-3 hours |
| #5 Backend | Medium | 2-3 hours |
| #6 QA/DevOps | Medium | 2-3 hours |

**Progreso:** 3/7 cerebros activos (**43%** - Framework Core + Testing COMPLETE!)

---

## Testing Suite Completado (2026-02-25)

### Resultados de los 4 Tests

| Test | Input | Score | Veredicto | Validación |
|------|-------|-------|-----------|------------|
| **Test 1** | PetNFT (brief malo) | 0/156 (0%) | 🔴 REJECT | ✅ Detectó solución disfrazada de problema |
| **Test 2** | HabitFlow v1 (borderline) | 114/156 (73%) | ⚠️ CONDITIONAL | ✅ Distinguió correctamente CONDITIONAL vs APPROVE/REJECT |
| **Test 3** | HabitFlow v2 (iterado) | 149/156 (96%) | ✅ APPROVE | ✅ Ciclo de feedback validado (+23 puntos) |
| **Test 4** | UX Research (sesgado) | 8/50 (16%) | 🔴 REJECT | ✅ Detectó 4 sesgos cognitivos |

### Sesgos Detectados por el Cerebro #7

| Bias ID | Nombre | Detección |
|---------|--------|-----------|
| BIAS-01 | Confirmation Bias | ✅ Funciona |
| BIAS-04 | Survivorship Bias | ✅ Funciona |
| BIAS-06 | Authority Bias | ✅ Funciona |
| BIAS-07 | WYSIATI | ✅ Funciona |
| BIAS-10 | Inversion Failure | ✅ Funciona |

### Conclusiones del Testing

1. **Sistema de evaluación funciona** - Umbrales correctos (80% APPROVE, 60-79% CONDITIONAL, <60% REJECT)
2. **Detección de sesgos funciona** - 5/5 biases principales detectados correctamente
3. **Feedback es accionable** - Instrucciones específicas permiten iteración efectiva
4. **Ciclo de feedback validado** - v1 → v2 en 1 iteración mejoró de 73% a 96%

---

## NotebookLM Integration

### Notebooks Activos

| Notebook | ID | Sources | Status |
|----------|-----|---------|--------|
| `[CEREBRO] Product Strategy - Software Development` | f276ccb3 | 10/10 | ✅ Verified |
| `[CEREBRO] Growth & Data (Evaluator)` | d8de74d6 | 10/10 | ✅ Loaded 2026-02-25 |

### Fuentes del Cerebro #7 (Cargadas v1.0.1)

| Fuente | Experto | Tema |
|--------|---------|------|
| FUENTE-701 | Munger | Poor Charlie's Almanack (Mental Models) |
| FUENTE-702 | Kahneman | Thinking Fast & Slow (Sesgos Cognitivos) |
| FUENTE-703 | Tetlock | Superforecasting (Probabilistic Thinking) |
| FUENTE-704 | Hormozi | $100M Offers (Value Equation) |
| FUENTE-705 | Ellis | Hacking Growth (Growth Frameworks) |
| FUENTE-706 | Chen | Cold Start Problem (Network Effects) |
| FUENTE-707 | Dobelli | Art of Thinking Clearly (Sesgos Prácticos) |
| FUENTE-708 | Lenny | Newsletter Benchmarks (Métricas) |
| FUENTE-709 | Generated | Checklist Evaluación (placeholder - depende cerebros 3-6) |
| FUENTE-710 | Generated | Anti-patrones (placeholder - depende cerebros 3-6) |

---

## Comandos Útiles

### CLI mastermind

```bash
# Source management
mm source new                    # Crear nueva fuente
mm source validate --brain 01    # Validar fuentes
mm source status --brain 07      # Status cerebro 07
mm source list                   # Listar todas

# Brain management
mm brain status 07               # Status cerebro 07
mm brain compile-radar 07        # Generar FUENTE-709/710
mm brain validate 01             # Validar cerebro

# Framework
mm framework status              # Status general
mm info                          # System info

# Orchestrate
mm orchestrate run "brief"       # Orquestrar brief
mm orchestrate run --dry-run     # Ver plan sin ejecutar
mm orchestrate run --flow validation_only "brief"  # Forzar flujo
```

### Git

```bash
# Ver commits recientes
git log --oneline -5

# Ver cambios
git diff

# Branch actual
git branch  # Debe ser master
```

---

## Estructura del Proyecto

```
mastermind/
├── agents/
│   ├── brains/
│   │   ├── product-strategy.md   # Cerebro #1 ✅ TESTED
│   │   ├── ux-research.md        # Cerebro #2 ✅ TESTED
│   │   └── growth-data.md        # Cerebro #7 ✅ TESTED
│   └── orchestrator/            # Orquestador ✅
│
├── docs/
│   ├── design/                  # Especificaciones (00-11)
│   ├── software-development/    # Nicho: desarrollo de software
│   │   ├── 01-product-strategy-brain/ ✅
│   │   ├── 02-ux-research-brain/ ✅
│   │   ├── 03-06-*-brain/       # Cerebros pendientes
│   │   └── 07-growth-data-brain/ ✅
│   ├── HANDOFF.md               # ESTE ARCHIVO
│   ├── EVALUATOR-GUIDE.md       # Guía del evaluador ✅
│   └── ORCHESTRATOR-GUIDE.md    # Guía del orquestador ✅
│
├── skills/evaluator/            # Evaluator Skill ✅
│   ├── SKILL.md
│   ├── protocol.md
│   ├── bias-catalog.yaml        # 10 sesgos cognitivos
│   ├── benchmarks.yaml          # Benchmarks de industria
│   └── evaluation-matrices/
│       └── product-brief.yaml   # Matriz de evaluación ✅
│
├── tools/mastermind-cli/        # CLI implementado ✅
│
└── CLAUDE.md                    # Instrucciones para Claude
```

---

## Próximos Pasos Recomendados

### Opción A: Cerebro #3 - UI Design (En Progreso 🔵)

**Estado:** Usuario cargando fuentes maestras

**Qué falta:**
1. Validar fuentes cargadas (YAML front matter completo)
2. Crear system prompt del Cerebro #3
3. Crear NotebookLM notebook
4. Testing con briefs de diseño

**Expertas a incluir:** Norman, Nielsen, Krug, Young, Walter, Fitzpatrick, NN/g, Yablonski, (+ fuentes de UI que el usuario esté subiendo)

### Opción B: Matriz de Evaluación UX Research (1 hora)

Crear `skills/evaluator/evaluation-matrices/ux-research.yaml` basado en:
- FUENTE-201 a FUENTE-210 (Cerebro #2 sources)
- Bias catalog (BIAS-01, BIAS-04, BIAS-06 para research)
- Protocolo de evaluación del Cerebro #7

**Checks sugeridos:**
- ¿Se entrevistaron usuarios reales? (no amigos/familia)
- ¿Se reporta FUNNEL completo? (contactados → aceptaron → completaron)
- ¿Hay sección de Negative Findings? (BIAS-01)
- ¿Raw quotes vs interpretations? (BIAS-06)
- ¿Se reconocen limitaciones? (BIAS-07)

### Opción C: Implementar Cerebro #4 Frontend (2-3 hours)

Requiere:
1. 10 fuentes maestras de Frontend (React, Angular, State Management, Testing)
2. System prompt con frameworks expertos
3. NotebookLM notebook
4. Testing con briefs de implementación

### Opción D: Testing End-to-End

Probar el flujo completo:
1. Usuario da brief
2. Orchestrator clasifica y crea plan
3. Cerebro #1 genera product-brief
4. Cerebro #7 evalúa
5. Si CONDITIONAL → Cerebro #1 itera
6. Si APPROVE → siguiente cerebro (#2 UX)

---

## Archivos Clave para Leer

| Archivo | Para qué |
|---------|----------|
| `CLAUDE.md` | Instrucciones del proyecto para Claude |
| `docs/design/00-PRD-MasterMind-Framework.md` | PRD principal - LEER PRIMERO |
| `docs/design/11-Cerebro-07-Evaluador-Critico.md` | Especificación Cerebro #7 |
| `docs/EVALUATOR-GUIDE.md` | Guía de uso del evaluador |
| `skills/evaluator/bias-catalog.yaml` | 10 sesgos cognitivos |
| `skills/evaluator/evaluation-matrices/product-brief.yaml` | Matriz de evaluación |

---

## Convenciones del Proyecto

### Git Commits

- **Formato:** Conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **SIN "Co-Authored-By"** — Nunca agregar atribución AI
- **NUNCA usar `--no-verify`** — Esperar al GGA hook

### Lenguaje

- **Documentación:** Español
- **Código:** Inglés
- **Comentarios:** Inglés (código), Español (docs)

### YAML Front Matter (Fuentes)

```yaml
---
source_id: "FUENTE-XXX"
brain: "brain-software-XX-*-brain"
title: "Title"
author: "Author"
expert_id: "EXP-XXX"
type: "book|article|video"
version: "1.0.0"
last_updated: "YYYY-MM-DD"
changelog:
  - version: "1.0.0"
    date: "YYYY-MM-DD"
    changes: []
status: "active"
loaded_in_notebook: true/false
---
```

---

## Session Context Quick-Load

Para recuperar rápidamente el contexto en la próxima sesión:

```bash
# 1. Entrar al proyecto
cd /home/rpadron/proy/mastermind

# 2. Verificar estado
git status
git log --oneline -3

# 3. Leer memorias Serena (via MCP)
# - MEMORY.md
# - session/2026-02-25-brain-testing-complete

# 4. Verificar fuentes de cerebros
mm source status --brain 07  # Debe mostrar 10/10 loaded
mm source status --brain 03  # Ver estado de carga

# 5. Continuar con próxima tarea
```

---

## Problemas Conocidos

| Issue | Severidad | Workaround |
|-------|-----------|------------|
| FUENTE-709/710 vacías | Low | Son placeholders que se llenarán cuando cerebros 3-6 existan |
| Matriz ux-research.yaml falta | Medium | Usar evaluación manual hasta crearla |

---

## Contacto / Referencias

- **Repo:** https://github.com/rap77/mastermind-framework
- **Branch:** master
- **Último commit:** 5d327d7 (Cerebro #7 sources update)

---

**Documento de Handoff v3.0**
**Generado:** 2026-02-25
**Framework Core: 43% COMPLETE (3/7 cerebros)** ✅
**Testing Suite: VALIDATED** ✅
**Para sesiones futuras de MasterMind Framework**
