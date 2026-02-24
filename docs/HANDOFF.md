# Handoff Document — MasterMind Framework

**Última actualización:** 2026-02-24
**Sesión:** PRP-005 Implementation Complete
**Estado:** Framework al 85% de completion

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
| `SESSION-2026-02-24-PROGRESS` | Detalle de PRP-005 implementado |
| `CHECKPOINT-2026-02-24-PRP005-COMPLETE` | Punto de recuperación completo |
| `COMMANDS` | Comandos útiles del proyecto |
| `CONVENTIONS` | Convenciones de código y git |

**Para cargar contexto al iniciar sesión:**
1. Leer `PROJECT` para overview
2. Leer `SESSION-2026-02-24-PROGRESS` para lo último hecho
3. Leer `CHECKPOINT-2026-02-24-PRP005-COMPLETE` para recuperación

---

## Estado Actual del Proyecto

### PRPs Completados ✅

| PRP | Descripción | Status | Commit |
|-----|-------------|--------|--------|
| PRP-000 | Initial Setup | ✅ | ac1696a |
| PRP-001 | mastermind-cli | ✅ | b050e22 |
| PRP-003 | System Prompts | ✅ | - |
| PRP-004 | NotebookLM Integration | ✅ | 254f108 |
| PRP-005 | Brain #7 Evaluator | ✅ | **286efb8** |

### PRPs Pendientes ⏳

| PRP | Descripción | Prioridad | Estimated |
|-----|-------------|-----------|-----------|
| PRP-002 | YAML Versioning | Medium | 30 min |
| PRP-006 | Orchestrator | High | 2-3 hours |

**Progreso:** 6/7 PRPs completados (**85%**)

---

## Lo Que Se Acaba de Completar (PRP-005)

### Evaluator Skill Implementado

```
skills/evaluator/
├── SKILL.md                    # System prompt del evaluador
├── protocol.md                 # Protocolo de 5 pasos
├── bias-catalog.yaml          # 10 sesgos cognitivos
├── benchmarks.yaml            # SaaS/Marketplace/Mobile benchmarks
├── evaluation-matrices/
│   └── product-brief.yaml     # 19 checks en 4 categorías
└── templates/
    ├── evaluation-report.yaml
    └── escalation-report.yaml
```

### Brain #7 Creado

- **Archivo:** `agents/brains/growth-data.md`
- **Expertos:** Munger, Kahneman, Tetlock, Hormozi, Ellis, Chen, Lenny
- **Rol:** Evalúa outputs de cerebros 1-6

### CLI Enhanced

- **Comando nuevo:** `mm brain compile-radar 07`
- **Función:** Genera FUENTE-709 y FUENTE-710 desde cerebros 1-6

### Commit Pendiente de Push

```bash
# El commit 286efb8 NO está pusheado aún
git push origin master
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
├── agents/brains/
│   ├── product-strategy.md      # Cerebro #1 ✅
│   └── growth-data.md           # Cerebro #7 ✅ NEW
│
├── docs/
│   ├── design/                  # Especificaciones (00-11)
│   ├── software-development/    # Nicho: desarrollo de software
│   │   ├── 01-product-strategy-brain/
│   │   ├── 02-06-*-brain/       # Cerebros pendientes
│   │   └── 07-growth-data-brain/ ✅
│   ├── PRD/                     # PRDs del framework
│   ├── PRPs/                    # PRPs de implementación
│   ├── HANDOFF.md               # ESTE ARCHIVO
│   └── EVALUATOR-GUIDE.md       # Guía del evaluador ✅ NEW
│
├── skills/evaluator/            # Evaluator Skill ✅ NEW
│   ├── SKILL.md
│   ├── protocol.md
│   ├── bias-catalog.yaml
│   ├── benchmarks.yaml
│   ├── evaluation-matrices/
│   └── templates/
│
├── tests/fixtures/
│   └── product-brief-defectuoso.md  # Test ✅ NEW
│
├── tools/mastermind-cli/        # CLI implementado
│
├── PRPs/                        # PRPs creados
│   └── PRP-005-brain-07-evaluator.md ✅
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

### Opción A: Continuar con PRPs (Recomendado)

**PRP-006: Orchestrator** (High Priority)
- Coordina Cerebro #1 + Cerebro #7
- Implementa flujo de evaluación automático
- Maneja iteraciones y veredictos
- Estimated: 2-3 hours

**PRP-002: YAML Versioning** (Medium Priority)
- Agregar YAML front matter a fuentes existentes
- Completar secciones faltantes
- Estimated: 30 min

### Opción B: Testing

**Probar flujo completo**
- Usar test brief defectuoso
- Verificar que el evaluador detecta problemas
- Probar con un brief real

### Opción C: NotebookLM para Cerebro #7 (Opcional)

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
| `docs/design/10-Plan-Implementacion-Claude-Code.md` | Plan de implementación |
| `docs/design/11-Cerebro-07-Evaluador-Critico.md` | Especificación Cerebro #7 |
| `PRPs/PRP-005-brain-07-evaluator.md` | PRP recién completado |
| `docs/EVALUATOR-GUIDE.md` | Guía de uso del evaluador |

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
# - CHECKPOINT-2026-02-24-PRP005-COMPLETE

# 4. Opcional: Push cambios pendientes
git push origin master

# 5. Continuar con próximo PRP o tarea
```

---

## Problemas Conocidos

Ninguno. Todas las validaciones pasaron.

---

## Contacto / Referencias

- **Repo:** https://github.com/rap77/mastermind-framework
- **Branch:** master
- **Último commit:** 286efb8

---

**Documento de Handoff v2.0**
**Generado:** 2026-02-24
**Para sesiones futuras de MasterMind Framework**
