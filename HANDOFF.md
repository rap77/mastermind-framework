# MasterMind Framework - Handoff / Continue Session

> Última actualización: **2026-02-23**
> Proyecto: mastermind-framework
> Repo: https://github.com/rap77/mastermind-framework
> Branch: **master** (todos los commits pusheados)

---

## Quick Start (Para continuar sesión)

```bash
# 1. Ir al proyecto
cd /home/rpadron/proy/mastermind

# 2. Verificar estado
git status
git log --oneline -5

# 3. Cargar contexto del proyecto con Serena MCP
# (El proyecto ya debería estar activado como "mastermind")

# 4. Leer PRP siguiente o continuar con implementación
```

---

## Estado Actual

### ✅ PRPs Completados

| PRP | Descripción | Commit | Estado |
|-----|-------------|--------|--------|
| PRP-000 | Initial Setup & Project Structure | ac1696a | ✅ Done |
| PRP-001 | mastermind-cli (CLI con 11 comandos) | b050e22 | ✅ Done |
| PRP-002 | YAML Versioning en 10 fuentes + update script | e4ed255 | ✅ Done |
| PRP-003 | System Prompts (Orquestador, Evaluador, Cerebro #1) | e0ea9bf | ✅ Done |
| PRP-004 | NotebookLM Integration (Cerebro #1 completo) | 254f108 | ✅ Done |
| PRP-005 | Brain #7 Critical Evaluator (10 fuentes + PRP) | 235d3b7 | ✅ **CREADO** |

### 📋 Siguiente Paso

| Opción | Descripción | Acción |
|--------|-------------|--------|
| **A** | Implementar PRP-005 (Evaluator Skill + CLI) | Leer `PRPs/PRP-005-brain-07-evaluator.md` y ejecutar |
| **B** | Probar Orquestador con Cerebro #1 + #7 | Crear brief de prueba, coordinar ambos cerebros |
| **C** | Crear notebook NotebookLM para Cerebro #7 | Usar MCP notebooklm-mcp para cargar 10 fuentes |

**Recomendación:** Opción A → Implementar PRP-005 primero para tener evaluación funcional.

---

## Estructura del Proyecto

```
/home/rpadron/proy/mastermind/
├── docs/
│   ├── design/
│   │   ├── 00-PRD-MasterMind-Framework.md      ← PRD principal
│   │   ├── 10-Plan-Implementacion-Claude-Code.md  ← Plan de implementación
│   │   └── 11-Cerebro-07-Evaluador-Critico.md  ← Spec Cerebro #7
│   ├── NOTEBOOKLM-GUIDE.md                    ← Guía de integración
│   └── software-development/
│       ├── 01-product-strategy-brain/
│       │   ├── sources/                          → 10 fuentes ✅
│       │   │   ├── FUENTE-001 through FUENTE-010
│       │   └── notebook-config.json              → NotebookLM configurado ✅
│       └── 07-growth-data-brain/
│           └── sources/                          → 10 fuentes ✅
│               ├── FUENTE-701 through FUENTE-710
├── agents/
│   ├── orchestrator/system-prompt.md
│   ├── evaluator/system-prompt.md
│   └── brains/
│       ├── product-strategy.md                  → Cerebro #1 ✅
│       └── (growth-data.md)                       → Cerebro #7 (pendiente)
├── tools/mastermind-cli/                          → CLI funcional ✅
├── PRPs/
│   ├── PRP-000 through PRP-005                     → Todos creados ✅
│   └── PRP-MASTER-coordinator.md
└── CLAUDE.md                                        → Reglas del proyecto
```

---

## NotebookLM Status

### Notebooks Activos

| Notebook | ID | Fuentes | Estado |
|----------|-----|---------|--------|
| `[CEREBRO] Product Strategy - Software Development` | `f276ccb3-0bce-4069-8b55-eae8693dbe75` | 10/10 | ✅ Verified |
| `[CEREBRO] Growth & Data - Software Development` | Por crear | 10 listas | ⏳ Pendiente |

### Comandos MCP NotebookLM

```python
# Listar notebooks
mcp__notebooklm_mcp__notebook_list(max_results=100)

# Crear notebook
mcp__notebooklm_mcp__notebook_create(title="[CEREBRO] Nombre - Nicho")

# Agregar fuente (file)
mcp__notebooklm_mcp__source_add(notebook_id="ID", source_type="file", file_path="ruta")

# Consultar notebook
mcp__notebooklm_mcp__notebook_query(notebook_id="ID", query="Pregunta")

# Exportar fuentes (usar tools/export_sources_notebooklm.py)
```

---

## Comandos CLI Disponibles

```bash
# Desde la raíz del proyecto
uv run python tools/mastermind-cli/main.py <comando>

# O usando el alias (si está configurado)
mastermind source {new,update,validate,status,list,export}
mastermind brain {status,validate,package}
mastermind framework {status,release}
mastermind info

# Ejemplos:
mastermind source list              # Listar todas las fuentes
mastermind brain status 01-product-strategy
mastermind brain status 07-growth-data
```

---

## Stack y Versiones

| Componente | Versión | Estado |
|------------|---------|--------|
| Python | 3.12.3 | ⚠️ Proyecto requiere ≥3.14 (funciona para dev) |
| uv | 0.9.28+ | ✅ |
| Click | 8.3.1 | CLI framework |
| Rich | 14.3.3 | Terminal output |
| GitPython | 3.1.46 | Git operations |

---

## Git Rules

- **NUNCA** usar `--no-verify` (usuario lo prohibió explícitamente)
- Esperar a que termine el hook GGA (puede tardar con muchos archivos)
- Conventional commits: `feat(scope): description`
- Formato commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`

---

## Lo que Falta por Implementar

### 1. PRP-005: Brain #7 Evaluator Skill (3-4 horas)

**Archivos a crear:**
```
skills/evaluator/
├── SKILL.md                          # System prompt del evaluador
├── protocol.md                       # Protocolo de 5 pasos
├── bias-catalog.yaml                 # 10 sesgos cognitivos
├── benchmarks.yaml                   # Métricas SaaS/Marketplace
├── evaluation-matrices/
│   └── product-brief.yaml            # Matrix para Cerebro #1
└── templates/
    ├── evaluation-report.yaml        # Template de reporte
    └── escalation-report.yaml        # Template para escalaciones
```

**CLI a agregar:**
```python
# Comando a agregar en tools/mastermind-cli/mastermind_cli/commands/brain.py
@brain.command("compile-radar")
def brain_compile_radar(brain_id: str):
    """Compile evaluation criteria from all brains."""
    # Implementación descrita en PRP-005
```

**System prompt a crear:**
- `agents/brains/growth-data.md` (usar `agents/brains/product-strategy.md` como referencia)

### 2. Orquestador (Futuro)

Coordinará cerebros #1 y #7 para flujo completo:
- Brief → Cerebro #1 → Evaluación #7 → Output

---

## MCP Servers Configurados

| Server | Propósito | Estado |
|--------|----------|--------|
| **Serena** | Memoria del proyecto, navegación de código | ✅ Activo |
| **NotebookLM** | Integración con cerebros | ✅ Funcionando |
| **Context7** | Documentación de librerías | ✅ Configurado |
| **Sequential-Thinking** | Razonamiento multi-paso | ✅ Configurado |

---

## Testing - Cerebro #1 Validado

### Test 1: TaskFlow Pro Brief ✅
- Brief sobre AI coding assistant para devs junior
- Respuesta completa sobre 4 riesgos de discovery
- Score: 9.8/10

### Test 2: TaskFlow Pro Completo ✅
- Brief completo TaskFlow Pro con contexto
- Respuesta detallada con estrategia, hipótesis, métricas
- Integró correctamente múltiples expertos (Cagan, Torres, Ries, Perri, Doerr)

---

## Comandos de Referencia Rápida

```bash
# Validar fuentes
mastermind source validate --brain 01-product-strategy

# Listar fuentes
mastermind source list

# Brain status
mastermind brain status 01
mastermind brain status 07

# Framework status
mastermind framework status

# Exportar a NotebookLM
python3 tools/export_sources_notebooklm.py

# Git
git status
git log --oneline -5

# MCP - NotebookLM
# (Usar herramientas mcp__notebooklm_mcp__*)
```

---

## Para Terminar Sesión

```bash
# 1. Verificar que no hay cambios pendientes
git status

# 2. Si hay cambios, commitear
git add -A
git commit -m "feat: descripción"

# 3. Guardar sesión (usar /sc:save)
# La memoria ya está guardada

# 4. Salir o cerrar terminal
```

---

## Siguiente Comando para Continuar

**Opción A - Implementar PRP-005:**
```bash
# Leer el PRP primero
cat PRPs/PRP-005-brain-07-evaluator.md

# Crear estructura de directorios
mkdir -p skills/evaluator/{evaluation-matrices,templates}
mkdir -p logs/{evaluations,precedents}

# Empezar implementación siguiendo las tareas del PRP
```

**Opción B - Probar Orquestador:**
```bash
# Crear brief de prueba
# Ejecutar flujo: Brief → Cerebro #1 → Cerebro #7 → Output
# Usar MCP notebooklm para #1 y skill evaluator para #7
```

**Opción C - NotebookLM para Cerebro #7:**
```bash
# Crear notebook
mcp__notebooklm_mcp__notebook_create(title="[CEREBRO] Growth & Data - Software Development")

# Exportar fuentes (adaptar script existente)
python3 tools/export_sources_notebooklm.py

# Cargar 10 fuentes
# (usar mcp__notebooklm_mcp__source_add para cada FUENTE-701 a FUENTE-710)
```

---

## Notas Importantes

1. **Nombre del proyecto:** El repo es `mastermind-framework`, pero el proyecto interno se llama "Mente Maestra" o "MasterMind Framework"
2. **Formato de notebooks:** Siempre `[CEREBRO]` no `[MM]`
3. **Serena MCP:** Proyecto activado como "mastermind" - usar `mcp__serena__*` herramientas para memoria
4. **GGA Hook:** Paciencia, tarda más con muchos archivos pero es necesario
5. **Python 3.12:** Funciona para desarrollo, actualizar a 3.14 antes de producción

---

**Último commit:** `235d3b7` - docs(prp): add PRP-005 for Brain #7 with 10 sources

**Siguiente PRP a implementar:** PRP-005 (Evaluator Skill + CLI compile-radar)
