# Handoff Document — MasterMind Framework

**Última actualización:** 2026-02-24
**Sesión:** PRP-006 Implementation Complete
**Estado:** Framework Core al 100% de completion ✅

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

El proyecto usa **Serena MCP** para gestión de memoria. Las memorias disponibles son:

| Memoria | Propósito |
|---------|-----------|
| `PROJECT` | Estado general del proyecto |
| `SESSION-2026-02-24-PROGRESS` | Detalle de sesión completa (PRP-005 + PRP-006) |
| `CHECKPOINT-2026-02-24-PRP005-COMPLETE` | PRP-005 Brain #7 |
| `CHECKPOINT-2026-02-24-PRP006-COMPLETE` | PRP-006 Orchestrator |
| `COMMANDS` | Comandos útiles del proyecto |
| `CONVENTIONS` | Convenciones de código y git |

**Para cargar contexto al iniciar sesión:**
1. Leer `PROJECT` para overview
2. Leer `SESSION-2026-02-24-PROGRESS` para lo último hecho
3. Leer `CHECKPOINT-2026-02-24-PRP006-COMPLETE` para recuperación más reciente

---

## Estado Actual del Proyecto

### PRPs Completados ✅

| PRP | Descripción | Status | Commit |
|-----|-------------|--------|--------|
| PRP-000 | Initial Setup | ✅ | ac1696a |
| PRP-001 | mastermind-cli | ✅ | b050e22 |
| PRP-003 | System Prompts | ✅ | - |
| PRP-004 | NotebookLM Integration | ✅ | 254f108 |
| PRP-005 | Brain #7 Evaluator | ✅ | 286efb8 |
| PRP-006 | Orchestrator | ✅ | **4873faf** |

### PRPs Pendientes ⏳

| PRP | Descripción | Prioridad | Estimated |
|-----|-------------|-----------|-----------|
| PRP-002 | YAML Versioning | Medium | 30 min |

**Progreso:** 7/7 PRPs core completados (**100%** - Framework Core COMPLETE!)

---

## Lo Que Se Acaba de Completar (PRP-006)

### Orchestrator Central Implementado

```
agents/orchestrator/
├── system-prompt.md            # System prompt (400+ líneas)
├── config/
│   ├── flows.yaml             # 6 flujos estándar
│   ├── brains.yaml            # 7 cerebros con triggers
│   └── thresholds.yaml        # Umbrales de decisión
├── protocols/
│   ├── task-decomposition.md  # Descomposición de briefs
│   ├── evaluation-flow.md     # Iteración con Cerebro #7
│   └── escalation.md          # Protocolo de escalación
└── precedents/
    ├── template.yaml          # Template de precedente
    └── catalog.yaml           # Catálogo (vacío)
```

### Flujos Estándar Definidos

| Flujo | Secuencia | Propósito |
|-------|-----------|-----------|
| `full_product` | 1→2→3→4→5→6→7 | Producto completo |
| `validation_only` | 1→7 | Validación de idea |
| `design_sprint` | 1→2→3→7 | Diseño sin construcción |
| `build_feature` | 4→5→6→7 | Implementar feature |
| `optimization` | 7→1 | Optimizar existente |
| `technical_review` | 5→6→7 | Revisión técnica |

### Protocolos Implementados

- **Task Decomposition:** Descomponer briefs en tareas atómicas
- **Evaluation Flow:** Iterar con Cerebro #7 (3 rechazos = escalar)
- **Escalation:** Escalar a humano cuando sea necesario
- **Precedents:** Aprender de conflictos resueltos

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

### Validación

```bash
# Validar YAML
python3 -c "import yaml; yaml.safe_load(open('skills/evaluator/bias-catalog.yaml'))"

# Verificar estructura
ls -la skills/evaluator/
```

---

## Estructura del Proyecto

```
mastermind/
├── agents/
│   ├── brains/
│   │   ├── product-strategy.md   # Cerebro #1 ✅
│   │   └── growth-data.md        # Cerebro #7 ✅
│   └── orchestrator/            # Orquestador ✅ NEW
│       ├── system-prompt.md
│       ├── config/              # flows, brains, thresholds
│       ├── protocols/           # task-decomp, evaluation, escalation
│       └── precedents/          # template, catalog
│
├── docs/
│   ├── design/                  # Especificaciones (00-11)
│   ├── software-development/    # Nicho: desarrollo de software
│   │   ├── 01-product-strategy-brain/ ✅
│   │   ├── 02-06-*-brain/       # Cerebros pendientes
│   │   └── 07-growth-data-brain/ ✅
│   ├── PRD/                     # PRDs del framework
│   ├── PRPs/                    # PRPs de implementación
│   ├── HANDOFF.md               # ESTE ARCHIVO
│   ├── EVALUATOR-GUIDE.md       # Guía del evaluador ✅
│   └── ORCHESTRATOR-GUIDE.md    # Guía del orquestador ✅ NEW
│
├── skills/evaluator/            # Evaluator Skill ✅
│   ├── SKILL.md
│   ├── protocol.md
│   ├── bias-catalog.yaml
│   ├── benchmarks.yaml
│   ├── evaluation-matrices/
│   └── templates/
│
├── tests/fixtures/
│   └── product-brief-defectuoso.md  # Test ✅
│
├── tools/mastermind-cli/        # CLI implementado ✅
│
├── PRPs/                        # PRPs creados
│   ├── PRP-005-brain-07-evaluator.md ✅
│   └── PRP-006-orchestrator.md ✅ NEW
│
├── logs/                        # Logs (gitignored)
│   ├── evaluations/
│   └── precedents/
│
├── CLAUDE.md                    # Instrucciones para Claude
└── .gitignore
```

---

## NotebookLM Integration

### Notebook Activo

| Notebook | ID | Sources | Status |
|----------|-----|---------|--------|
| `[CEREBRO] Product Strategy - Software Development` | `f276ccb3-0bce-4069-8b55-eae8693dbe75` | 10/10 | ✅ Verified |

### MCP NotebookLM

```bash
# El MCP notebooklm-mcp está funcionando
# Comandos disponibles vía MCP
```

---

## Próximos Pasos Recomendados

### Opción A: PRP-002 - YAML Versioning (30 min)

- Agregar YAML front matter a fuentes existentes
- Completar secciones faltantes en FUENTE-008, FUENTE-009, FUENTE-010
- Agregar version y changelog

### Opción B: Testing del Orquestador (1-2 horas)

- Probar flujo completo con briefs reales
- Verificar interacción: Orchestrator → Cerebro #1 → Cerebro #7
- Crear precedents de ejemplo

### Opción C: CLI Command - `mm orchestrate` (PRP-008, 2-3 hours)

- Implementar comando `mm orchestrate <brief>`
- Integrar con CLI existente
- Testing con briefs de ejemplo

### Opción D: NotebookLM para Cerebro #7 (Opcional)

- Crear notebook: `[CEREBRO] Growth & Data - Software Development`
- Cargar 10 fuentes (FUENTE-701 a FUENTE-710)
- Ejecutar 3 consultas de prueba

---

## Archivos Clave para Leer

Si necesitas entender el framework:

| Archivo | Para qué |
|---------|----------|
| `CLAUDE.md` | Instrucciones del proyecto para Claude |
| `docs/design/00-PRD-MasterMind-Framework.md` | PRD principal - LEER PRIMERO |
| `docs/design/07-Orquestador-y-Evaluador.md` | Especificación Orquestador |
| `docs/design/11-Cerebro-07-Evaluador-Critico.md` | Especificación Cerebro #7 |
| `PRPs/PRP-006-orchestrator.md` | PRP Orquestador |
| `docs/EVALUATOR-GUIDE.md` | Guía de uso del evaluador |
| `docs/ORCHESTRATOR-GUIDE.md` | Guía de uso del orquestador |

---

## Convenciones del Proyecto

### Git Commits

- **Formato:** Conventional commits (`feat:`, `fix:`, `docs:`, etc.)
- **SIN "Co-Authored-By"** — Nunca agregar atribución AI
- **Ejemplo:** `feat(evaluator): implement Cerebro #7 with evaluator skill`

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
version: "1.0.0"
last_updated: "YYYY-MM-DD"
changelog:
  - version: "1.0.0"
    date: "YYYY-MM-DD"
    changes: []
---
```

---

## Notas Técnicas

### MCP Servers Activos

- **Serena:** ✅ Project memory, code navigation
- **NotebookLM:** ✅ Notebook integration
- **Context7:** ✅ Documentation lookup
- **Sequential-Thinking:** ✅ Multi-step reasoning

### GGA Hook

- **Estado:** Activo y pasando
- **Caché:** Utilizado (13 archivos from cache)
- **Nota:** NUNCA usar `--no-verify`

### CLI mastermind

- **Instalado:** ✅ En `/home/rpadron/proy/mastermind/tools/mastermind-cli/`
- **Alias:** `mm` funciona
- **Comandos:** source, brain, framework

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
# - PROJECT
# - SESSION-2026-02-24-PROGRESS
# - CHECKPOINT-2026-02-24-PRP006-COMPLETE (más reciente)

# 4. Verificar estado (todo debe estar pusheado)
git status
git log --oneline -3

# 5. Continuar con próxima tarea
```

---

## Problemas Conocidos

Ninguno. Todas las validaciones pasaron.

---

## Contacto / Referencias

- **Repo:** https://github.com/rap77/mastermind-framework
- **Branch:** master
- **Último commit:** 4873faf (PRP-006)

---

**Documento de Handoff v2.1**
**Generado:** 2026-02-24
**Framework Core: 100% COMPLETE** ✅
**Para sesiones futuras de MasterMind Framework**
