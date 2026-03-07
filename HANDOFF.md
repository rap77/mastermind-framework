# MasterMind Framework - Handoff / Continue Session

> Última actualización: **2026-03-06**
> Proyecto: mastermind-framework
> Repo: https://github.com/rap77/mastermind-framework
> Branch: **master** (✅ Up to date)

---

## Quick Start (Para continuar sesión)

```bash
# 1. Ir al proyecto
cd /home/rpadron/proy/mastermind

# 2. Verificar estado
git status
git log --oneline -5

# 3. Cargar contexto del proyecto con Serena MCP
/sc:load

# 4. Continuar con siguiente tarea
```

---

## Estado Actual

### Framework Completion: 100% ✅

| # | Cerebro | System Prompt | Fuentes | NotebookLM | Estado |
|---|---------|---------------|---------|-----------|--------|
| 1 | Product Strategy | ✅ | 10 | ✅ f276ccb3 | **Activo** |
| 2 | UX Research | ✅ | 19 | ✅ ea006ece | **Activo** |
| 3 | UI Design | ✅ | 20 | ✅ 8d544475 | **Activo** |
| 4 | Frontend | ✅ | 18 | ✅ 85e47142 | **Activo** |
| 5 | Backend | ✅ | 21 | ✅ c6befbbc | **Activo** |
| 6 | QA/DevOps | ✅ | 20 | ✅ 74cd3a81 | **Activo** |
| 7 | Growth/Data | ✅ MEJORADO | 14 | ✅ d8de74d6 | **Activo** |

**Total:** 7/7 cerebros con system prompts (100%), 7/7 activos en NotebookLM (100%), **122/122 fuentes (100%)**, Testing Suite 5/5 passed ✅

**Mejora Cerebro #7 (2026-03-03):** Se agregaron 4 fuentes críticas:
- FUENTE-711: Reforge Product Management (Brian Balfour)
- FUENTE-712: The Mom Test (Rob Fitzpatrick)
- FUENTE-713: Trustworthy Online Controlled Experiments (Ron Kohavi)
- FUENTE-714: Lean Analytics (Alistair Croll)

---

## Últimos Commits

| Commit | Descripción | Fecha |
|--------|-------------|-------|
| 626f40e | chore: ignore checkpoints directory | 2026-03-06 |
| 9f5ef48 | docs: add prosell v2 briefs and evaluation reports | 2026-03-06 |
| 977a21e | feat(commands): add slash commands and 22 expert knowledge sources | 2026-03-06 |
| 78b208f | feat(cli): add install command, brain registry, and upgrade orchestrator | 2026-03-06 |
| 3b56e0b | feat(mcp): add integration and 6 critical sources | 2026-03-05 |

---

## Próximos Pasos Recomendados

| # | Tarea | Estado | Acción |
|---|-------|--------|--------|
| 1 | CLI v1.0.0 | ✅ Completado | mastermind install, source, brain, framework |
| 2 | Slash Commands | ✅ Completado | 11 commands (/ask product, /ask ux, etc.) |
| 3 | 22 Fuentes Nuevas | ✅ Completado | UX(9), UI(2), Frontend(1), Backend(8), QA(6), Growth(4) |
| 4 | **PRP-008: `mm orchestrate`** | ⏳ Pendiente | Exponer comando en CLI |
| 5 | README.md Update | ⏳ Pendiente | Actualizar a v1.0.0 con cerebros correctos |
| 6 | CLI Testing | ⏳ Pendiente | End-to-end de todos los comandos |

**Recomendación:** Opción 4 → Exponer comando `orchestrate` en CLI para completar PRP-008.

---

## Estructura de Fuentes por Cerebro

```
docs/software-development/
├── 01-product-strategy-brain/sources/   → FUENTE-001 a 010 ✅
├── 02-ux-research-brain/sources/        → FUENTE-201 a 221 ✅ (19+9 nuevas)
├── 03-ui-design-brain/sources/          → FUENTE-301 a 320 ✅ (15+2 nuevas)
├── 04-frontend-brain/sources/           → FUENTE-401 a 418 ✅ (15+1 nueva)
├── 05-backend-brain/sources/            → FUENTE-500 a 522 ✅ (11+8 nuevas)
├── 06-qa-devops-brain/sources/          → FUENTE-601 a 621 ✅ (11+6 nuevas)
└── 07-growth-data-brain/sources/        → FUENTE-701 a 714 ✅ (10+4 nuevas)
```

**Total: 122 fuentes** (100% completo)

---

## NotebookLM Status

### Notebooks Activos (7/7)

| Notebook | ID | Fuentes | URL |
|----------|-----|---------|-----|
| `[CEREBRO] Product Strategy` | `f276ccb3` | 10 | [Abrir](https://notebooklm.google.com/notebook/f276ccb3) |
| `[CEREBRO] UX Research` | `ea006ece` | 19 | [Abrir](https://notebooklm.google.com/notebook/ea006ece) |
| `[CEREBRO] UI Design` | `8d544475` | 20 | [Abrir](https://notebooklm.google.com/notebook/8d544475) |
| `[CEREBRO] Frontend Architecture` | `85e47142` | 18 | [Abrir](https://notebooklm.google.com/notebook/85e47142) |
| `[CEREBRO] Backend Architecture` | `c6befbbc` | 21 | [Abrir](https://notebooklm.google.com/notebook/c6befbbc) |
| `[CEREBRO] QA/DevOps` | `74cd3a81` | 20 | [Abrir](https://notebooklm.google.com/notebook/74cd3a81) |
| `[CEREBRO] Growth & Data` | `d8de74d6` | 14 | [Abrir](https://notebooklm.google.com/notebook/d8de74d6) |

---

## Comandos CLI Disponibles (v1.0.0)

```bash
# Instalación en proyectos
mastermind install init              # Inicializa framework en proyecto actual
mastermind install status             # Muestra estado de instalación
mastermind install uninstall          # Desinstala framework del proyecto

# Gestión de fuentes
mastermind source new                 # Crear nueva fuente
mastermind source update <id>         # Actualizar fuente existente
mastermind source validate --brain <id>  # Validar fuentes de cerebro
mastermind source status --brain <id>  # Estado de fuentes
mastermind source list                # Listar todas las fuentes
mastermind source export --brain <id> # Exportar fuentes

# Gestión de cerebros
mastermind brain status               # Estado de cerebros
mastermind brain validate             # Validar configuración
mastermind brain package              # Package para distribución

# Framework
mastermind framework status           # Estado general del framework
mastermind framework release          # Crear release

# Info
mastermind info                       # Información del sistema

# Alias: mm (ej: mm source list)
```

### Slash Commands (Claude Code)

```bash
/ask product [pregunta]      # Cerebro #1 - Product Strategy
/ask ux [pregunta]           # Cerebro #2 - UX Research
/ask design [pregunta]       # Cerebro #3 - UI Design
/ask frontend [pregunta]     # Cerebro #4 - Frontend
/ask backend [pregunta]      # Cerebro #5 - Backend
/ask qa [pregunta]           # Cerebro #6 - QA/DevOps
/ask growth [pregunta]       # Cerebro #7 - Growth/Data

/ask-all [pregunta]          # Todos los 7 cerebros como equipo
/ask-ui-docs [contexto]      # Genera documentación UI/UX
/audit [estado]              # Health check completo
/project-health-check [tipo] # Alias de /audit
```

---

## Orquestador Status

### Implementado ✅ (no expuesto en CLI aún)

**Ubicación:** `mastermind_cli/orchestrator/`

**Componentes:**
- `coordinator.py` - Coordina los 7 cerebros
- `brain_executor.py` - Ejecuta consultas vía NotebookLM MCP
- `evaluator.py` - Cerebro #7 evalúa resultados
- `flow_detector.py` - Detecta flujo según brief
- `plan_generator.py` - Genera plan de ejecución
- `mcp_integration.py` - Wrapper MCP NotebookLM
- `notebooklm_client.py` - Cliente NotebookLM
- `output_formatter.py` - Formatea outputs

**Falta:** Exponer comando `orchestrate` en `mastermind_cli/main.py`

---

## Stack y Versiones

| Componente | Versión | Estado |
|------------|---------|--------|
| Python | 3.14+ | ✅ (requerido) |
| uv | 0.9.28+ | ✅ |
| Click | 8.3.1 | ✅ |
| Rich | 14.3.3 | ✅ |
| PyYAML | 6.x | ✅ |
| GitPython | 3.1.46 | ✅ |

---

## Git Rules

- **NUNCA** usar `--no-verify` (usuario lo prohibió explícitamente)
- Conventional commits: `feat(scope): description`
- GGA hook: esperar a que termine (cachea revisiones)
- Si GGA falla sin output claro, ejecutar: `pre-commit run gga --all-files`

---

## Archivos Clave del Proyecto

| Archivo | Propósito |
|---------|-----------|
| `CLAUDE.md` | Instrucciones del proyecto para Claude Code |
| `HANDOFF.md` | Este archivo - handoff entre sesiones |
| `docs/CLI-REFERENCE.md` | Documentación completa del CLI |
| `mastermind_cli/` | Paquete CLI v1.0.0 ✅ |
| `mastermind_cli/brain_registry.py` | IDs de NotebookLM (config pública) ✅ |
| `tools/mastermind-cli/` | CLI tools distribution ✅ |
| `.claude/commands/` | Slash commands (11 archivos) ✅ |

---

## MCP Servers Configurados

| Server | Propósito | Estado |
|--------|----------|--------|
| **Serena** | Memoria del proyecto, navegación de código | ✅ Activo |
| **NotebookLM** | Integración con cerebros | ✅ Funcionando |
| **Context7** | Documentación de librerías | ✅ Configurado |
| **Sequential-Thinking** | Razonamiento multi-paso | ✅ Configurado |

---

## Comandos de Referencia Rápida

```bash
# Estado del framework
mastermind framework status

# Listar fuentes
mastermind source list

# Instalar en proyecto actual
mastermind install init

# Git status
git status
git log --oneline -5

# Usar cerebro vía slash command
/ask product ¿Deberíamos construir X?
```

---

## Para Termininar Sesión

```bash
# 1. Guardar sesión
/sc:save

# 2. Verificar cambios pendientes
git status

# 3. Si hay cambios, commitear
git add -A
git commit -m "feat: descripción"

# 4. Salir
```

---

## Notas Importantes

1. **Nombre del proyecto:** Repo = `mastermind-framework`, interno = "Mente Maestra"
2. **Formato de notebooks:** Siempre `[CEREBRO]` no `[MM]`
3. **Serena MCP:** Proyecto activado como "mastermind"
4. **GGA Hook:** Ejecutar manualmente si falla: `pre-commit run gga --all-files`
5. **brain_registry.py:** IDs son config pública, NO credenciales
6. **Checkpoints:** `.claude/checkpoints/` ignorado en `.gitignore`

---

## Test Results Histórico

**Testing Suite 2026-02-28 (5/5 tests passed)**
- Test-01 (Bad Brief): 9/100 REJECT ✅
- Test-02 (Borderline): 68/100 CONDITIONAL ✅
- Test-03 (Good Brief): 88/100 APPROVE ✅
- Test-04 (Full Flow): 84/100 CONDITIONAL ✅
- Test-05 (Optimization): 82/100 CONDITIONAL ✅

**Accuracy: 100% | Confidence avg: 87.6%**

---

**Último commit:** `626f40e` - chore: ignore checkpoints directory

**Framework Status:** 100% completo (7/7 cerebros, 122/122 fuentes, orquestador implementado)
