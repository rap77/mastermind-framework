# MasterMind Framework — Estado de Implementación

**Fecha:** 2026-04-20
**Versión:** 3.0
**Objetivo:** Framework utilizable en cualquier proyecto (plug-and-play)

---

## ✅ LO QUE ESTÁ IMPLEMENTADO

### 1. Comandos de Claude Code (Slash Commands)

**Total:** 28 comandos `.md` implementados

| Comando | Estado | Handler Python | Nota |
|---------|--------|----------------|------|
| `/mm:discover` | ✅ Completo | ✅ Sí | Nuevo - genera SPEC.md + plan.md |
| `/mm:complete-task` | ✅ Completo | ✅ Sí | Ejecuta build → test → review → commit |
| `/mm:safe-commit` | ✅ Completo | ❌ No | GGA hook validation |
| `/mm:plan-phase` | ✅ Completo | ❌ No | Planea fases con brains |
| `/mm:execute-phase` | ✅ Completo | ❌ No | Ejecuta fases |
| `/mm:complete-phase` | ✅ Completo | ❌ No | Completa y commitea fase |
| `/mm:verify-task` | ✅ Completo | ❌ No | Verifica task completado |
| `/mm:ask-*` | ✅ 8 comandos | ❌ No | Consulta brains específicos |
| `/mm:propose` | ✅ Completo | ❌ No | Genera propuestas |
| `/mm:new-milestone` | ✅ Completo | ❌ No | Crea nuevo milestone |
| Otros 16 | ✅ Completos | ❌ No | Varios comandos |

**Problema:** Solo 2 de 28 comandos tienen lógica Python detrás. Los demás son solo documentación que Claude debe interpretar.

---

### 2. Agents (Cerebros Especializados)

**Total:** 10 agentes implementados

| Agent | Estado | Nota |
|-------|--------|------|
| `brain-01-product` | ✅ Completo | Product Strategy |
| `brain-02-ux` | ✅ Completo | UX Research |
| `brain-03-ui` | ✅ Completo | UI Design |
| `brain-04-frontend` | ✅ Completo | Frontend Architecture |
| `brain-05-backend` | ✅ Completo | Backend Architecture |
| `brain-06-qa` | ✅ Completo | QA/DevOps |
| `brain-07-growth` | ✅ Completo | Growth/Data |
| `discover-planner` | ✅ Completo | Modo nuevo |
| `rediscovery-auditor` | ✅ Completo | Modo existing |
| `task-executor` | ✅ Completo | Ejecuta build → test → review |

**Estado:** ✅ Todos los agents necesarios están implementados

---

### 3. Skills

**Total:** 7 skills implementados

| Skill | Estado | Nota |
|-------|--------|------|
| `brain-context` | ✅ Completo | Consulta cerebros |
| `brain-persistence` | ✅ Completo | Persiste output |
| `discover` | ✅ Completo | Nuevo discovery |
| `mastermind-consultant` | ✅ Completo | Consultant principal |
| `plan-phase` | ✅ Completo | Planea fases |
| `safe-commit` | ✅ Completo | Valida commits |
| `verify-task` | ✅ Completo | Verifica tasks |

**Estado:** ✅ Todos los skills necesarios están implementados

---

### 4. CLI (tools/mastermind-cli)

**Estado:** ⚠️ Incompleto

| Componente | Estado | Nota |
|-----------|--------|------|
| `main.py` | ❌ Placeholder | Solo tiene print |
| `commands/` | ❌ Vacío | No hay comandos implementados |
| `orchestrator/` | ⚠️ Parcial | Algún código existe |
| `INSTALL.md` | ✅ Completo | Documentación exhaustiva |

**Problema:** El CLI NO es funcional standalone. Solo funciona vía Claude Code.

---

## ❌ LO QUE FALTA PARA SER "PLUG-AND-PLAY"

### 1. Handlers Python para Comandos Críticos

**Prioridad ALTA:**

Comandos que NECESITAN handlers Python:

1. **`/mm:safe-commit`** — Pre-commit hook
   - Ejecuta GGA hook
   - Valida tests
   - Valida formato de commit
   - Auto-corrije errores

2. **`/mm:plan-phase`** — Planea fases
   - Lee plan.md
   - Consulta brains
   - Genera PLAN.md
   - Actualiza todo.md

3. **`/mm:verify-task`** — Verifica tasks
   - Lee plan.md + todo.md
   - Verifica acceptance criteria
   - Valida tests pasan
   - Genera reporte

4. **`/mm:ask-*`** (8 comandos) — Consulta brains
   - `ask-product` → Brain #1
   - `ask-ux` → Brain #2
   - `ask-design` → Brain #3
   - `ask-frontend` → Brain #4
   - `ask-backend` → Brain #5
   - `ask-qa` → Brain #6
   - `ask-growth` → Brain #7
   - `ask-all` → Todos los brains

5. **`/mm:new-milestone`** — Crea milestones
   - Lee ROADMAP.md
   - Valida con Brain #1 + #7
   - Crea estructura de fases
   - Genera templates

---

### 2. CLI Standalone Funcional

**Qué necesita el CLI:**

1. **Comando `mastermind install init`**
   ```bash
   mastermind install init [--brains #1,#4,#7] [--framework-path ~/projects/mastermind]
   ```
   - Copia archivos .claude/ al proyecto
   - Crea .mastermind/config.yaml
   - Crea .mastermind-active marker
   - Instala hooks

2. **Comando `mastermind brain status`**
   ```bash
   mastermind brain status [#1|#all]
   ```
   - Muestra estado de brains
   - Valida conexión NotebookLM
   - Muestra notebook IDs

3. **Comando `mastermind orchestrate`**
   ```bash
   mastermind orchestrate brief.md --flow full_product
   ```
   - Ejecuta flujo de brains
   - Genera outputs
   - Guarda en .planning/

---

### 3. Instalación Automatizada

**Script de instalación:**

`install-mastermind.sh`:
```bash
#!/bin/bash
# MasterMind Framework Installer

# 1. Detect framework path
FRAMEWORK_PATH="${MASTERMIND_FRAMEWORK_PATH:-~/proy/mastermind}"

# 2. Copy .claude/ structure
cp -r $FRAMEWORK_PATH/.claude $PROJECT_ROOT/

# 3. Create .mastermind/config.yaml
cat > $PROJECT_ROOT/.mastermind/config.yaml <<EOF
project:
  name: $PROJECT_NAME
  path: $PROJECT_ROOT

framework:
  version: 3.0.0
  path: $FRAMEWORK_PATH

brains:
  #1:
    name: Product Strategy
    notebook_id: $BRAIN_1_NOTEBOOK_ID
    active: true
  # ... (otros brains)
EOF

# 4. Create .mastermind-active
touch $PROJECT_ROOT/.mastermind-active

# 5. Verify installation
echo "✅ MasterMind installed in $PROJECT_ROOT"
```

---

### 4. Configuración Universal por Defecto

**Template de config.yaml:**

```yaml
# .mastermind/config.template.yaml
project:
  name: "{PROJECT_NAME}"  # Auto-detected
  path: "{PROJECT_ROOT}"   # Auto-detected

framework:
  version: 3.0.0
  path: "{FRAMEWORK_PATH}"  # Auto-detected or ~/proy/mastermind

brains:
  #1:
    name: Product Strategy
    notebook_id: "{BRAIN_1_NOTEBOOK_ID}"  # From env or prompt
    active: true
  #2:
    name: UX Research
    notebook_id: "{BRAIN_2_NOTEBOOK_ID}"
    active: true
  #3:
    name: UI Design
    notebook_id: "{BRAIN_3_NOTEBOOK_ID}"
    active: true
  #4:
    name: Frontend
    notebook_id: "{BRAIN_4_NOTEBOOK_ID}"
    active: true
  #5:
    name: Backend
    notebook_id: "{BRAIN_5_NOTEBOOK_ID}"
    active: true
  #6:
    name: QA/DevOps
    notebook_id: "{BRAIN_6_NOTEBOOK_ID}"
    active: true
  #7:
    name: Growth/Data
    notebook_id: "{BRAIN_7_NOTEBOOK_ID}"
    active: true

orchestration:
  default_flow: validation_only  # validation_only | full_product | design_sprint
  checkpoint_every: 3           # Save checkpoint every N brain outputs
  auto_approve: false            # Require Brain #7 approval

output:
  format: markdown              # markdown | json | yaml
  location: .planning/           # Relative to project root
  timestamps: true
```

---

### 5. Tests del Framework

**Tests faltantes:**

1. **Test de instalación:**
   ```python
   def test_install_in_new_project():
       project = create_temp_project()
       install_mastermind(project)
       assert (project / ".mastermind-active").exists()
       assert (project / ".claude/commands/mm/").exists()
   ```

2. **Test de comandos:**
   ```python
   def test_discover_new_project():
       result = run_command("/mm:discover", "Test idea")
       assert "SPEC.md" in result.files_created
       assert "plan.md" in result.files_created
   ```

3. **Test de integración:**
   ```python
   def test_full_workflow():
       # 1. Discover
       discover("Test idea")
       # 2. Complete task
       complete_task("A1")
       # 3. Verify
       verify_task("A1")
       # 4. Safe commit
       safe_commit()
   ```

---

## 🎯 PLAN DE COMPLETACIÓN

### Fase 1: Handlers Críticos (PRIORIDAD ALTA)

**Archivos a crear:**

1. `.claude/commands/mm/safe-commit-handler.py`
2. `.claude/commands/mm/plan-phase-handler.py`
3. `.claude/commands/mm/verify-task-handler.py`
4. `.claude/commands/mm/ask-*-handler.py` (8 handlers)
5. `.claude/commands/mm/new-milestone-handler.py`

**Tiempo estimado:** 4-6 horas

---

### Fase 2: CLI Standalone (PRIORIDAD MEDIA)

**Archivos a crear/modificar:**

1. `tools/mastermind-cli/main.py` — Implementar CLI real
2. `tools/mastermind-cli/commands/install.py` — Comando install
3. `tools/mastermind-cli/commands/brain.py` — Comandos brain
4. `tools/mastermind-cli/commands/orchestrate.py` — Comando orchestrate
5. `tools/mastermind-cli/commands/framework.py` — Comandos framework

**Tiempo estimado:** 6-8 horas

---

### Fase 3: Instalación Automatizada (PRIORIDAD MEDIA)

**Archivos a crear:**

1. `scripts/install-mastermind.sh` — Script bash
2. `scripts/install-mastermind.ps1` — Script PowerShell
3. `.mastermind/config.template.yaml` — Template config
4. `scripts/verify-installation.sh` — Verifica instalación

**Tiempo estimado:** 2-3 horas

---

### Fase 4: Tests (PRIORIDAD BAJA)

**Archivos a crear:**

1. `tests/test_installation.py`
2. `tests/test_commands.py`
3. `tests/test_integration.py`
4. `tests/test_cli.py`

**Tiempo estimado:** 4-6 horas

---

## 📊 RESUMEN

| Categoría | Implementado | Falta | % Completado |
|-----------|--------------|-------|--------------|
| Comandos .md | 28/28 | 0 | 100% |
| Handlers Python | 2/28 | 26 | 7% |
| Agents | 10/10 | 0 | 100% |
| Skills | 7/7 | 0 | 100% |
| CLI Standalone | 0/1 | 1 | 0% |
| Instalación Auto | 0/1 | 1 | 0% |
| Tests | 0/1 | 1 | 0% |
| **TOTAL** | **47/69** | **22** | **68% |

---

## 🚀 RECOMENDACIÓN

**Para usar el framework en otro proyecto HOY:**

1. ✅ **Manualmente** copiar:
   - `.claude/` → nuevo proyecto
   - `.claude/commands/mm/` → comandos funcionan en Claude Code
   - `.claude/skills/mm/` → skills se activan automáticamente
   - `.claude/agents/mm/` → agents disponibles

2. ❌ **NO funcionan** sin trabajo adicional:
   - CLI standalone (`mastermind install init`)
   - Handlers Python (solo complete-task y discover)
   - Instalación automatizada
   - Tests

**Para completarlo:**

Ejecutar **Fase 1** (Handlers críticos) — 4-6 horas de trabajo.

Esto haría que el framework sea **90% funcional** para cualquier proyecto.

---

**¿Querés que proceda con la Fase 1 ahora, loco?** 🎯
