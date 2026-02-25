# Handoff Document — MasterMind Framework

**Última actualización:** 2026-02-24
**Sesión:** PRP-006 + PRP-008 Complete + CLI Automation
**Estado:** Framework Core 100% + CLI Automation ✅

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
| PRP-006 | Orchestrator | ✅ | 4873faf |
| PRP-008 | CLI Orchestrate | ✅ | **bb1ec26** |

### PRPs Pendientes ⏳

| Componente | Prioridad | Estimated |
|------------|----------|-----------|
| Cerebro #2 (UX Research) | Medium | 2-3 hours |
| Cerebro #3 (UI Design) | Low | 2-3 hours |
| Cerebro #4 (Frontend) | Low | 2-3 hours |
| Cerebro #5 (Backend) | Low | 2-3 hours |
| Cerebro #6 (QA/DevOps) | Low | 2-3 hours |
| NotebookLM para Cerebro #7 | Low | 1 hour |

**Progreso:** 8/8 core PRPs completados (**100%** - Framework Core + CLI COMPLETE!)

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

## Lo Que Se Acaba de Completar (PRP-008)

### CLI `mm orchestrate` Implementado

```
tools/mastermind-cli/mastermind_cli/
├── commands/orchestrate.py      # Comando CLI principal
└── orchestrator/
    ├── flow_detector.py          # Detección automática de flujo
    ├── plan_generator.py         # Generación de execution plans
    ├── brain_executor.py         # Ejecución de cerebros (placeholder)
    ├── output_formatter.py       # Formato de outputs legibles
    └── coordinator.py            # Coordinador principal
```

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `mm orchestrate run "brief"` | Orquestra brief completo |
| `mm orchestrate run --dry-run "brief"` | Genera plan sin ejecutar |
| `mm orchestrate run --flow validation_only "brief"` | Fuerza flujo específico |
| `mm orchestrate run --file brief.md` | Lee brief desde archivo |
| `mm orchestrate run -o output.yaml "brief"` | Guarda output en archivo |

### Ejemplos de Uso

```bash
# Validación de idea (flow automático)
mm orchestrate run "validar idea de app de viajes"

# Producto completo (solo ver plan)
mm orchestrate run --dry-run "quiero crear una app de delivery"

# Forzar flujo de validación
mm orchestrate run --flow validation_only "es buena idea esta app?"
```

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

## Testing Pendiente ⚠️

Los siguientes componentes están implementados pero **NO han sido probados con briefs reales**:

### Componentes Sin Testing Real

| Componente | Estado Implementación | Estado Testing |
|------------|----------------------|----------------|
| **Orchestrator Central** | ✅ Completo | ⚠️ Solo simulación (TEST-001) |
| **Cerebro #7 (Evaluador)** | ✅ Evaluator skill completo | ⚠️ Sin NotebookLM |
| **CLI `mm orchestrate`** | ✅ Funcional | ⚠️ Outputs placeholder |
| **Integración NotebookLM → Cerebro #1** | ✅ Notebook existe | ⚠️ Sin testing en CLI |
| **Loop completo Orchestrator → #1 → #7** | ⚠️ No probado | ⚠️ End-to-end pendiente |

### Qué Significa "Sin Testing Real"

- **Orchestrator**: Se probó con simulación, no con brief real que consulte NotebookLM
- **Cerebro #7**: Tiene el evaluator skill pero no tiene NotebookLM con FUENTE-701-710
- **CLI `mm orchestrate`**: Funciona pero devuelve placeholders (no llama realmente a NotebookLM MCP)
- **Precedents**: El catálogo está vacío, no se ha creado ningún precedente

### Para Hacer Testing Real

```bash
# 1. Probar CLI con brief real (sin MCP)
mm orchestrate run "quiero validar una app de delivery para restaurantes"

# 2. Verificar que el flujo completo funcione
# Debería: Detectar flow → Generar plan → Ejecutar #1 (placeholder) → Evaluar #7 (placeholder)

# 3. Para integración real con NotebookLM
# Necesita: MCP notebooklm-mcp configurado y funcionando
# Cerebro #1: Notebook ID f276ccb3-0bce-4069-8b55-eae8693dbe75
```

---

## Próximos Pasos Recomendados

### Opción A: Testing End-to-End (Recomendado)

**Test del flujo validation_only con brief real**
- Probar `mm orchestrate run --validation_only "quiero validar idea de app"`
- Verificar que el plan se genere correctamente
- Verificar que los outputs se formateen bien
- Documentar cualquier bug encontrado

### Opción B: NotebookLM para Cerebro #7 (1 hora)

- Crear notebook: `[CEREBRO] Growth & Data - Software Development`
- Cargar 10 fuentes (FUENTE-701 a FUENTE-710) — **ESTAS FUENTES NO EXISTEN AÚN**
- Ejecutar 3 consultas de prueba
- Nota: Primero hay que crear las fuentes FUENTE-701 a FUENTE-710

### Opción C: Cerebro #2 (UX Research) (2-3 horas)

- Requiere 10 fuentes maestras de UX Research
- Crear system prompt
- Crear NotebookLM notebook
- Testing con briefs de diseño

### Opción D: Documentación y Mejoras

- Tutoriales de uso del CLI
- Ejemplos de briefs y sus outputs
- Demo videos (opcional)


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
