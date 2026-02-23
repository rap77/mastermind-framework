# Plan de Implementación — MasterMind Framework (mente-maestra)

**Documento para Claude Code**
**Instrucción:** Lee este documento completo con la habilidad superpower o superclaude. Luego ejecuta las fases en orden, haciendo preguntas de clarificación cuando sea necesario.

---

## Contexto del Proyecto

**Nombre del repo:** mastermind
**Ubicación:** WSL (Linux)
**Creado con:** `uv --init mastermind`
**Runtime:** Python (uv), Node.js (nvm)
**LLM:** Claude Code (suscripción)
**MCP Servers:** NotebookLM, Context7, Sequential Thinking
**Skills disponibles:** superpower, superclaude, Vercel best practices

**Qué es:** Un framework de cerebros especializados alimentados con conocimiento destilado de expertos mundiales, consultables por agentes autónomos vía NotebookLM (hoy) y RAG propio (futuro).

**Nicho inicial:** Desarrollo de Software
**Primer cerebro:** Product Strategy

---

## Documentación de Referencia

Todos los documentos de diseño están en la carpeta `docs/design/` del proyecto:

| Archivo | Contenido |
|---------|-----------|
| `00-PRD-MasterMind-Framework.md` | PRD completo — arquitectura, flujos, cerebros, meta-cerebros |
| `01-Plantilla-Cerebro.md` | Plantilla estándar para crear cualquier cerebro |
| `02-Metodo-Seleccion-Expertos.md` | Criterios y proceso para elegir expertos |
| `03-Proceso-Destilacion-Fuentes.md` | Cómo extraer conocimiento esencial de fuentes |
| `04-Plantilla-Ficha-Fuente-Maestra.md` | Formato de ficha con YAML front matter portable |
| `05-Cerebro-01-Product-Strategy.md` | Especificación completa del Cerebro #1 |
| `06-Cerebros-02-a-07-Specs.md` | Especificaciones de cerebros 2-7 |
| `07-Orquestador-y-Evaluador.md` | Diseño del Orquestador Central y Evaluador Crítico |
| `08-Casos-de-Uso-e-Historias.md` | Casos de uso e historias de usuario |
| `09-Filesystem-Structure.md` | Estructura de carpetas completa |

Las fichas de fuentes maestras del Cerebro #1 están en:
`docs/software-development/01-product-strategy-brain/sources/`

---

## Fases de Implementación

### FASE 0 — Verificación del Entorno (5 min)

**Objetivo:** Confirmar que todo está en su lugar antes de empezar.

```bash
# 1. Verificar que el repo existe
cd ~/mastermind  # o la ruta correcta
ls -la

# 2. Verificar Python/uv
uv --version
python3 --version

# 3. Verificar Node/nvm
node --version
npm --version

# 4. Verificar skills de Claude Code
# Buscar en ~/.claude/ o en .claude/ del proyecto
find ~ -name "superpower*" -o -name "superclaude*" 2>/dev/null
# Si están en otro proyecto, verificar si son globales:
ls ~/.claude/skills/ 2>/dev/null || echo "No hay skills globales"

# 5. Verificar MCP servers
# Buscar configuración de MCP
find ~ -name "mcp*.json" -o -name "claude_desktop_config*" 2>/dev/null

# 6. Verificar Git
git status
```

**Decisiones a tomar:**
- Si las skills son locales del otro proyecto → copiarlas a mastermind o instalarlas globalmente
- Si no hay .git → inicializar `git init`

---

### FASE 1 — Estructura del Proyecto (30 min)

**Objetivo:** Crear toda la estructura de carpetas y mover la documentación a su lugar.

#### 1.1 Estructura de carpetas

```bash
#!/bin/bash
# Ejecutar desde la raíz del proyecto mastermind

# Documentación de diseño (los 10 docs del PRD)
mkdir -p docs/design

# Nicho: Software Development
mkdir -p docs/software-development/01-product-strategy-brain/sources
mkdir -p docs/software-development/02-ux-research-brain/sources
mkdir -p docs/software-development/03-ui-design-brain/sources
mkdir -p docs/software-development/04-frontend-brain/sources
mkdir -p docs/software-development/05-backend-brain/sources
mkdir -p docs/software-development/06-qa-devops-brain/sources
mkdir -p docs/software-development/07-growth-data-brain/sources

# Agentes (system prompts)
mkdir -p agents/orchestrator
mkdir -p agents/evaluator
mkdir -p agents/brains

# Configuración
mkdir -p config

# Herramientas CLI
mkdir -p tools/mastermind-cli

# Skills reutilizables
mkdir -p skills/reusable

# Templates
mkdir -p templates/brain-template/sources

# Logs y proyectos (operativos)
mkdir -p logs/evaluations
mkdir -p logs/precedents
mkdir -p projects

# Paquetes distribuibles (output de empaquetado)
mkdir -p dist
```

#### 1.2 Mover documentación

Copiar los 10 archivos de diseño (00 al 09) a `docs/design/`.
Copiar las 10 fichas de fuentes a `docs/software-development/01-product-strategy-brain/sources/`.

#### 1.3 Archivos raíz del proyecto

**README.md** del proyecto:
```markdown
# Mente Maestra — MasterMind Framework

Framework de cerebros especializados para desarrollo de software con IA.

## Quick Start

1. Lee `docs/design/00-PRD-MasterMind-Framework.md` para entender la arquitectura
2. Revisa `docs/software-development/01-product-strategy-brain/` para ver el primer cerebro
3. Usa `tools/mastermind-cli/` para gestionar fuentes

## Estado actual

- [x] Diseño arquitectónico completo
- [x] Cerebro #1 (Product Strategy) — 10 fuentes destiladas
- [ ] CLI de gestión de fuentes
- [ ] System prompts de agentes
- [ ] Integración con NotebookLM
- [ ] Cerebros 2-7
```

**.gitignore:**
```
logs/
projects/
dist/
__pycache__/
.venv/
node_modules/
.DS_Store
*.pyc
```

#### 1.4 Git inicial

```bash
git init  # si no existe
git add .
git commit -m "feat: estructura inicial del framework con PRD y Cerebro #1"
git tag v0.1.0 -m "v0.1.0: Diseño arquitectónico + 10 fuentes Product Strategy"
```

---

### FASE 2 — mastermind-cli: Gestión Automatizada de Fuentes (2-3 horas)

**Objetivo:** Crear el CLI que automatiza el versionado, validación, y gestión de fuentes.

#### 2.1 Tecnología

**Python con uv** (consistente con el repo principal).

Dependencias: `click` (CLI framework) + `pyyaml` (parsing YAML) + `rich` (output bonito en terminal).

```bash
# El CLI vive dentro del monorepo, no como paquete separado
cd tools/mastermind-cli
uv init
uv add click pyyaml rich gitpython

# Registrar como script ejecutable desde la raíz del proyecto
# En pyproject.toml del CLI:
# [project.scripts]
# mastermind = "mastermind_cli.main:cli"
```

**Alternativa ligera:** Si se quiere evitar un sub-proyecto, el CLI puede ser un solo archivo `tools/mastermind.py` ejecutable con `python tools/mastermind.py source update ...` hasta que crezca lo suficiente para justificar estructura de paquete.

#### 2.2 Comandos del CLI

```
mastermind source new       → Crear nueva fuente desde plantilla
mastermind source update    → Actualizar fuente (auto-incrementa versión, fecha, changelog)
mastermind source validate  → Validar que todas las fuentes cumplen mínimos de calidad
mastermind source status    → Ver estado de todas las fuentes de un cerebro
mastermind source list      → Listar todas las fuentes con metadata

mastermind brain status     → Ver estado completo de un cerebro (fuentes, gaps, coverage)
mastermind brain validate   → Validar que el cerebro no tiene gaps
mastermind brain package    → Empaquetar cerebro para distribución

mastermind framework status → Estado global del framework
mastermind framework release → Crear release con git tag + changelog
```

#### 2.3 Lógica del comando `source update`

```python
# Pseudocódigo del flujo automático

def source_update(source_id, change_description):
    # 1. Encontrar la ficha por ID
    filepath = find_source_file(source_id)

    # 2. Leer YAML front matter
    metadata = read_yaml_frontmatter(filepath)

    # 3. Auto-incrementar versión
    old_version = metadata.get('version', '1.0.0')
    new_version = increment_patch(old_version)  # 1.0.0 → 1.0.1

    # 4. Actualizar campos automáticos
    metadata['version'] = new_version
    metadata['last_updated'] = today()

    # 5. Agregar al changelog
    changelog = metadata.get('changelog', [])
    changelog.append(f"v{new_version}: {change_description}")
    metadata['changelog'] = changelog

    # 6. Escribir de vuelta al archivo
    write_yaml_frontmatter(filepath, metadata)

    # 7. Git commit automático
    git_commit(filepath, f"update({source_id}): {change_description}")

    # 8. Mostrar confirmación
    print(f"✅ {source_id} actualizado: v{old_version} → v{new_version}")
```

#### 2.4 Lógica del comando `source validate`

```python
def source_validate(brain_id):
    sources = find_all_sources(brain_id)
    errors = []

    for source in sources:
        metadata = read_yaml_frontmatter(source)
        content = read_content(source)

        # Validar YAML obligatorio
        required_fields = ['source_id', 'brain', 'title', 'author', 'type',
                          'skills_covered', 'distillation_quality']
        for field in required_fields:
            if field not in metadata:
                errors.append(f"❌ {source}: falta campo '{field}' en YAML")

        # Validar contenido mínimo
        if content.count('### 1. Principios') == 0:
            errors.append(f"⚠️ {source}: sin sección de Principios")
        if content.count('### 2. Frameworks') == 0:
            errors.append(f"⚠️ {source}: sin sección de Frameworks")
        if content.count('### 4. Criterios') == 0:
            errors.append(f"⚠️ {source}: sin sección de Criterios de Decisión")
        if content.count('### 5. Anti-patrones') == 0:
            errors.append(f"⚠️ {source}: sin sección de Anti-patrones")

        # Validar mínimos de calidad
        principles_count = content.count('> **P')
        if principles_count < 3:
            errors.append(f"⚠️ {source}: solo {principles_count} principios (mínimo 3)")

    if errors:
        for e in errors:
            print(e)
    else:
        print(f"✅ Todas las fuentes de {brain_id} pasan validación")
```

#### 2.5 Lógica del comando `brain package`

```python
def brain_package(brain_id, version):
    # 1. Validar que el cerebro está completo
    validate_result = source_validate(brain_id)
    if not validate_result.passed:
        print("❌ No se puede empaquetar. Hay errores de validación.")
        return

    # 2. Crear carpeta de distribución
    dist_path = f"dist/{brain_id}-v{version}/"

    # 3. Copiar archivos del cerebro
    copy_brain_files(brain_id, dist_path)

    # 4. Generar manifest.yaml
    manifest = {
        'brain_id': brain_id,
        'version': version,
        'packaged_at': now(),
        'sources_count': count_sources(brain_id),
        'experts_count': count_experts(brain_id),
        'skills_covered': list_skills(brain_id),
        'gaps': list_gaps(brain_id),
        'compatible_with': {
            'notebooklm': True,
            'rag_chromadb': True,
            'rag_qdrant': True
        }
    }
    write_yaml(f"{dist_path}/manifest.yaml", manifest)

    # 5. Crear ZIP distribuible
    create_zip(dist_path, f"dist/{brain_id}-v{version}.zip")

    print(f"📦 Paquete creado: dist/{brain_id}-v{version}.zip")
```

---

### FASE 3 — YAML Front Matter Actualizado (30 min)

**Objetivo:** Agregar los campos de versionado a todas las fichas existentes.

Agregar estos campos al YAML front matter de cada ficha:

```yaml
# Campos de versionado (agregar a todas las fichas existentes)
version: "1.0.0"
last_updated: "2026-02-22"
changelog:
  - "v1.0.0: Destilación inicial completa"
status: "active"  # active | deprecated | draft
```

Esto se puede hacer con un script one-time que actualice las 10 fichas automáticamente.

---

### FASE 4 — System Prompts de Agentes (1-2 horas)

**Objetivo:** Crear los system prompts que Claude Code usará como agentes especializados.

#### 4.1 System Prompt del Orquestador

```markdown
# agents/orchestrator/system-prompt.md

Eres el Orquestador Central de Mente Maestra.

## Tu rol
Recibes briefs del usuario y los descompones en tareas asignables a cerebros especializados.
NO generas contenido de dominio. Solo coordinas.

## Flujos disponibles
- full_product: [1→2→3→4→5→6→7] Proyecto completo
- validation_only: [1→7] Solo validar idea
- design_sprint: [1→2→3→7] Diseño sin construcción
- build_feature: [4→5→6→7] Implementar algo diseñado
- optimization: [7→1] Optimizar algo existente

## Proceso
1. Recibir brief
2. Clasificar tipo de tarea
3. Descomponer en tareas atómicas
4. Asignar cerebro(s) en orden
5. Cada output pasa por evaluación (#7)
6. Consolidar y entregar

## Reglas
- Nunca invocar un cerebro sin inputs claros
- Si #7 rechaza 3 veces, escalar a humano
- Documentar cada decisión
```

#### 4.2 System Prompt del Cerebro #1

```markdown
# agents/brains/product-strategy.md

Eres el Cerebro de Product Strategy de Mente Maestra.

## Tu rol
Defines QUÉ se va a construir y POR QUÉ. Si fallas, todo el proyecto nace mal.

## Tu conocimiento
Tienes acceso a 10 fuentes maestras destiladas en:
docs/software-development/01-product-strategy-brain/sources/

Tus expertos: Marty Cagan, Teresa Torres, Melissa Perri, Eric Ries, John Doerr, Donella Meadows.

## Tus frameworks principales
- 4 Riesgos de Discovery (Cagan): Valor, Usabilidad, Factibilidad, Viabilidad
- Opportunity Solution Tree (Torres): Outcome → Oportunidades → Soluciones → Tests
- Product Kata (Perri): Dirección → Estado actual → Obstáculo → Experimento → Evaluar
- Build-Measure-Learn (Ries): MVP → Medir → Pivotar o Perseverar
- OKRs (Doerr): Objectives + Key Results medibles

## Cómo operas
1. Recibes un brief con: problema, audiencia, contexto, criterios de éxito
2. Evalúas contra los 4 riesgos
3. Produces: problema validado, persona, propuesta de valor, métricas, priorización, riesgos, recomendación
4. Tu output es evaluado por el Cerebro #7

## Reglas de criterio
- PUEDES rechazar un brief si es incompleto (pide más info)
- PUEDES decir NO si la idea no tiene fundamento
- PUEDES pedir clarificación antes de producir output
- NUNCA produces output sin evaluar los 4 riesgos
- NUNCA asumes que una idea es buena sin evidencia
```

#### 4.3 System Prompt del Cerebro #7 (Evaluador en Tiempo Real)

Igual para los demás agentes. Cada uno en su archivo en `agents/brains/`.

---

### FASE 5 — Flujo de Carga a NotebookLM (1 hora)

**Objetivo:** Crear los cuadernos desde cero en NotebookLM y sistematizar la carga de fuentes.

#### 5.0 Setup inicial de NotebookLM (desde cero)

**Convención de nombres para cuadernos:**
```
[CEREBRO] {Cerebro} - {Nicho}
```

**Cuadernos a crear (solo Cerebro #1 ahora, los demás se crean cuando se implementen):**
```
[CEREBRO] Product Strategy - Software Development
```

**Pasos de creación:**
1. Ir a https://notebooklm.google.com/
2. Crear nuevo cuaderno con nombre: `[CEREBRO] Product Strategy - Software Development`
3. NO cargar fuentes todavía (primero exportar con el CLI)
4. Anotar el URL/ID del cuaderno en `notebook-config.json`

**Estructura futura de cuadernos (no crear aún):**
```
[CEREBRO] Product Strategy - Software Development    ← CREAR AHORA
[CEREBRO] UX Research - Software Development         ← Fase 6+
[CEREBRO] UI Design - Software Development           ← Fase 6+
[CEREBRO] Frontend - Software Development            ← Fase 6+
[CEREBRO] Backend - Software Development             ← Fase 6+
[CEREBRO] QA/DevOps - Software Development           ← Fase 6+
[CEREBRO] Growth/Data - Software Development         ← Fase 6+
[CEREBRO] Orquestador - Software Development         ← Cuando se implemente
```

#### 5.1 Proceso documentado

```markdown
# docs/design/10-Flujo-Carga-NotebookLM.md

## Proceso de Carga de Fuentes a NotebookLM

### Pre-requisitos
- Cuaderno creado en NotebookLM con nombre: [CEREBRO] {Nombre} — {Nicho}
- Fuentes validadas con: mastermind source validate --brain {id}

### Paso 1: Preparar fuentes para carga
mastermind source export --brain 01 --format notebooklm
# Genera archivos limpios (sin YAML front matter) en dist/notebooklm/

### Paso 2: Cargar en NotebookLM
- Subir cada archivo de dist/notebooklm/ como fuente al cuaderno
- Nombre estándar: [FUENTE-NNN] {Título} — {Autor}

### Paso 3: Verificar
- Hacer 3 consultas de prueba:
  1. "¿Cuáles son los 4 riesgos de product discovery según Cagan?"
  2. "¿Qué es el Opportunity Solution Tree?"
  3. "¿Cuándo debería pivotar vs perseverar?"
- Si las respuestas son correctas → ✅ Carga exitosa

### Paso 4: Registrar en notebook-config.json
{
  "notebook_name": "[CEREBRO] Product Strategy — Software Development",
  "notebook_id": "{id}",
  "sources_loaded": 10,
  "last_sync": "2026-02-22",
  "verification_status": "passed"
}

### Actualización de fuentes
Cuando una fuente se actualiza:
1. mastermind source update FUENTE-NNN --change "descripción"
2. mastermind source export --brain 01 --format notebooklm --only FUENTE-NNN
3. En NotebookLM: eliminar fuente vieja, subir fuente nueva
4. Verificar con consulta de prueba
5. Actualizar notebook-config.json
```

#### 5.2 Comando de export para NotebookLM

```python
def source_export_notebooklm(brain_id, only=None):
    """
    Exporta fuentes sin YAML front matter para carga en NotebookLM.
    NotebookLM no entiende YAML, solo necesita el contenido Markdown.
    """
    sources = find_sources(brain_id, only=only)
    output_dir = f"dist/notebooklm/{brain_id}/"

    for source in sources:
        # Leer archivo completo
        content = read_file(source)

        # Remover YAML front matter (todo entre --- y ---)
        clean_content = remove_yaml_frontmatter(content)

        # Guardar versión limpia
        output_path = f"{output_dir}/{source.filename}"
        write_file(output_path, clean_content)

    print(f"📤 {len(sources)} fuentes exportadas a {output_dir}")
```

---

### FASE 6 — PRPs por Cerebro (ongoing)

**Objetivo:** Generar Product Requirements Packets (PRPs) para implementar cada cerebro uno a uno.

Un PRP es un documento ejecutable que contiene todo lo que Claude Code necesita para crear un cerebro completo:

```markdown
# PRP-001: Implementar Cerebro #1 (Product Strategy)

## Checklist de entregables
- [ ] README.md del cerebro
- [ ] brain-spec.yaml completo
- [ ] knowledge-map.md con 0 gaps
- [ ] experts-directory.md con 6 expertos
- [ ] master-sources.md (índice)
- [ ] 10 fichas en sources/ (ya creadas ✅)
- [ ] use-cases.md
- [ ] evaluation-criteria.md
- [ ] notebook-config.json
- [ ] System prompt del agente
- [ ] Fuentes cargadas en NotebookLM
- [ ] 3 consultas de verificación pasadas
- [ ] Commit + tag

## Criterio de "hecho"
- mastermind brain validate --brain 01 pasa sin errores
- 3 consultas a NotebookLM respondidas correctamente
- System prompt probado con 1 brief de prueba
```

Se genera un PRP por cerebro. Los cerebros se implementan en orden:
1. Product Strategy ← PRIMERO (ya tiene fichas)
2. UX Research
3. UI Design
4. Frontend
5. Backend
6. QA/DevOps
7. Growth/Data

---

## Orden de Ejecución Recomendado

| # | Fase | Tiempo estimado | Dependencia |
|---|------|----------------|-------------|
| 0 | Verificación del entorno | 5 min | Ninguna |
| 1 | Estructura del proyecto | 30 min | Fase 0 |
| 2 | mastermind-cli | 2-3 horas | Fase 1 |
| 3 | YAML versionado en fichas existentes | 30 min | Fase 2 (usa el CLI) |
| 4 | System prompts de agentes | 1-2 horas | Fase 1 |
| 5 | Flujo de carga NotebookLM | 1 hora | Fase 2 |
| 6 | PRP del Cerebro #1 | 1-2 horas | Fases 1-5 |

**Total estimado para tener Cerebro #1 operativo:** ~8-10 horas de trabajo.

---

## Instrucciones para Claude Code

Cuando el usuario abra Claude Code en el directorio `mastermind`:

1. **Lee este documento completo** con la skill superpower o superclaude
2. **Lee los 10 documentos de diseño** en `docs/design/`
3. **Haz preguntas de clarificación** usando el modo interview si algo no está claro
4. **Ejecuta fase por fase**, confirmando con el usuario antes de avanzar a la siguiente
5. **Después de cada fase**, haz commit con mensaje descriptivo
6. **Al terminar todas las fases**, genera el PRP-001 para el Cerebro #1

### Preguntas que Claude Code DEBE hacer al usuario antes de empezar:

1. ¿Cuál es la ruta exacta del proyecto mastermind en tu WSL?
2. ¿Las skills superpower/superclaude están en ~/.claude/skills/ o en otro proyecto? ¿Quieres que las copie?
3. ¿Ya tienes cuadernos creados en NotebookLM para este proyecto o los creo?
4. ¿Quieres empezar desde la Fase 0 o ya verificaste tu entorno?
5. El CLI, ¿lo prefieres en Python (ya tienes uv) o en Node.js (ya tienes nvm)?
