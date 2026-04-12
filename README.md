# MasterMind Framework

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/rap77/mastermind-framework)

## Monorepo Structure

```
apps/
  api/          → Python FastAPI + CLI (brain orchestration)
  web/          → Next.js 16 dashboard (in development)
docker/
  api/          → Dockerfile for API service
  web/          → Dockerfile for web service
  postgres/     → PostgreSQL + pgvector (v3.0 migration)
docker-compose.yml      → production
docker-compose.dev.yml  → development (hot reload)
```
[![Python](https://img.shields.io/badge/python-3.14+-blue)](https://python.org)

> **Arquitectura Cognitiva Modular para Cerebros Especializados**

MasterMind es una arquitectura para crear "cerebros" especializados alimentados con conocimiento destilado de expertos mundiales. Cada cerebro domina un dominio específico y colabora con otros mediante un orquestador central y un evaluador crítico.

## Arquitectura

```
Brief del Usuario
    ↓
Orquestador Central (clasifica y asigna)
    ↓
Cerebro(s) Especializado(s) + NotebookLM (MCP)
    ↓
Cerebro #7 (Evaluador Crítico - meta-cerebro)
    ↓
Aprobado → Entrega | Rechazado → Iteración
```

### Los 8 Cerebros (Nicho: Software Development)

| # | Cerebro | Rol | Expertos Clave |
|---|---------|-----|----------------|
| 1 | Product Strategy | Define QUÉ y POR QUÉ | Cagan, Torres, Perri, Ries, Doerr |
| 2 | UX Research | Define la EXPERIENCIA | Norman, Nielsen, Krug, Young, Hall |
| 3 | UI Design | Define lo VISUAL | Frost, Wathan, Wroblewski, Lupton |
| 4 | Frontend | CONSTRUYE la interfaz | Simpson, Comeau, Osmani, Dodds |
| 5 | Backend | CONSTRUYE la lógica | Jin, Martin, Kleppmann, Xu, Fowler |
| 6 | QA/DevOps | GARANTIZA estabilidad | Kim, Forsgren, Humble, Majors, Crispin |
| 7 | Growth/Data | EVOLUCIONA todo | Munger, Kahneman, Tetlock, Hormozi |
| **8** | **Master Interviewer** | **DESCUBRE requisitos reales** | **Fitzpatrick, Voss, Stanier, Torres** |

---

## MM-Flow: Multi-Project Orchestration Engine

**MM-Flow** es el sistema de orquestación inteligente que reemplaza GSD. Diseñado para:

- 🎯 **Multi-proyecto:** Ejecutar mastermind + prosell-sass en paralelo usando la misma PostgreSQL
- 🤖 **Multi-backend:** Cambiar automáticamente entre Claude, OpenRouter, z.ai basado en tokens disponibles AHORA
- 🌙 **Night Mode:** Dejar un proyecto ejecutando 8 horas sin intervención mientras duermes
- 📊 **Smart Token Management:** Prioriza z.ai (5 resets/día), fallback a OpenRouter, Claude como último recurso
- 🔐 **Row-Level Security:** Org A no puede ver datos de Org B, incluso en DB compartida

### Arquitectura MM-Flow

```
┌─────────────────────────────────────────┐
│     MM-Flow Smart Backend Manager       │
│  (Consulta PostgreSQL cada 5 minutos)   │
└─────────────────────────────────────────┘
        ↓
        ├─→ Query: "¿Quién tiene MÁS tokens disponibles AHORA?"
        │
        ├─→ Mastermind proyecto:
        │   Claude: 85K/100K (85%) ← Usándose
        │   OpenRouter: 128K/128K (100%) ← Standby
        │   z.ai: 150K/200K (75%) ← Standby
        │
        ├─→ Prosell-sass proyecto:
        │   z.ai: 120K/200K (60%) ← Usándose
        │   OpenRouter: 100K/128K (78%)
        │   Claude: AGOTADO
        │
        └─→ DECISIÓN AUTOMÁTICA:
            • Si Claude < 5K tokens → switchea a OpenRouter
            • Si OpenRouter < 5K tokens → usa z.ai
            • Checkpoint automático ANTES de cambiar
            • Brain #7 valida output en AMBOS proyectos

┌─────────────────────────────────────────┐
│      PostgreSQL (Shared mastermind_bd)  │
├─────────────────────────────────────────┤
│ • organizations (2: acme-corp, prosell) │
│ • projects (2: mastermind, paperclip-v3)│
│ • backend_sessions (tracking tokens)    │
│ • mm_flow_state (fase actual + status)  │
│ • context_checkpoints (snapshots)       │
│ • brain_consultations (audit trail)     │
│ • RLS: org_id aísla datos automáticamente│
└─────────────────────────────────────────┘
```

---

## Quick Start

### Instalación Universal (Recomendado)

**¡No necesitas Python instalado!** El instalador lo hace todo por vos.

#### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.sh | bash
```

#### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/rap77/mastermind-framework/master/install.ps1 | iex
```

**Lo que hace el instalador:**
1. ✅ Verifica dependencias (git, curl)
2. ✅ Instala uv (package manager)
3. ✅ Descarga Python 3.14 automáticamente
4. ✅ Clona el repositorio
5. ✅ Instala MasterMind globalmente
6. ✅ Configura PATH para usar `mm` y `mastermind` desde cualquier lugar

---

### Instalación Manual (si ya tenés Python 3.14+)

```bash
# Clonar repositorio
git clone https://github.com/rap77/mastermind-framework.git
cd mastermind-framework

# Instalar dependencias
uv sync

# Instalar CLI globalmente
uv tool install -e .

# Verificar instalación
mastermind info
```

---

### Instalación en Otro Proyecto

```bash
# En cualquier proyecto existente
cd /path/to/your-project

# Inicializar MasterMind
mastermind install init

# El framework crea .mastermind/ con config local
```

## CLI Reference

```bash
# === Gestión de Fuentes de Conocimiento ===
mastermind source new              # Crear nueva fuente
mastermind source list             # Listar todas las fuentes
mastermind source validate         # Validar formato YAML
mastermind source export           # Exportar fuentes a NotebookLM

# === Estado de Cerebros ===
mastermind brain status            # Estado de todos los cerebros
mastermind brain status <id>       # Estado de cerebro específico
mastermind brain validate          # Validar system prompts
mastermind brain package           # Empaquetar cerebro para distribución

# === Orquestación ===
mastermind orchestrate run "brief"           # Ejecutar flujo completo
mastermind orchestrate run --dry-run "brief" # Ver plan sin ejecutar
mastermind orchestrate run --flow validation_only "brief"
mastermind orchestrate run --use-mcp "brief" # Usar NotebookLM real

# === Memory & Learning ===
mastermind eval list [--limit N]         # Listar evaluaciones recientes
mastermind eval show <EVAL-ID>           # Mostrar detalle de evaluación
mastermind eval find <project>           # Buscar por proyecto
mastermind eval search <keyword>         # Búsqueda por keyword
mastermind eval stats                    # Estadísticas de evaluaciones

# === Framework ===
mastermind framework status         # Estado del framework
mastermind framework release        # Preparar release

# === Instalación ===
mastermind install init             # Inicializar en proyecto
mastermind install status           # Ver estado de instalación
mastermind install uninstall        # Desinstalar de proyecto

# === Info ===
mastermind info                     # Mostrar información del framework
```

### Ejemplos de Uso

```bash
# Validar idea de producto
mastermind orchestrate run --flow validation_only \
  "Quiero crear una app para encontrar compañeros de viaje"

# Ver plan de ejecución sin ejecutar
mastermind orchestrate run --dry-run \
  "Necesito rediseñar el onboarding de mi SaaS"

# Usar cerebros específicos
mastermind orchestrate run --flow design_sprint \
  "Diseñar UI para dashboard de analytics"
```

## Claude Code Slash Commands

El framework incluye **slash commands** para usar directamente desde Claude Code con el namespace `mm:`:

### Discovery (Brain #8)

```bash
/mm:discovery "<brief vago>"  # Entrevista estructurada para clarificar requisitos
```

**Ejemplo:**
```bash
/mm:discovery "quiero una app moderna"
# → Brain #8 detecta ambigüedad
# → Conduce entrevista de 10-15 preguntas
# → Genera brief clarificado + recomendaciones de cerebros #1-7
```

### Consulta de Cerebros

```bash
/mm:ask-product    # Consulta cerebro Producto (qué y por qué)
/mm:ask-ux         # Consulta cerebro UX Research
/mm:ask-design     # Consulta cerebro UI Design
/mm:ask-frontend   # Consulta cerebro Frontend
/mm:ask-backend    # Consulta cerebro Backend
/mm:ask-qa         # Consulta cerebro QA/DevOps
/mm:ask-growth     # Consulta cerebro Growth/Data
/mm:ask-all        # Consulta TODOS los cerebros como equipo
```

### Gestión de Proyectos

```bash
/mm:project-audit      # Análisis completo de 7 cerebros
/mm:audit              # Alias rápido de project-audit
```

### PRDs y Especificaciones

```bash
/mm:lite-prd-generator  # Convierte idea en PRD demo-grade
/mm:prd-clarifier       # Refina y clarifica PRD existente
/mm:generate-prp        # Crea PRP (Project Requirements Plan)
/mm:execute-prp         # Ejecuta PRP existente
```

### MM-Flow: Multi-Project Orchestration CLI

MM-Flow es el motor que controla ejecución multi-proyecto, backend switching inteligente, y night mode.

#### Setup Inicial

```bash
# Cargar credenciales de los 3 backends
source ~/.claude/backends.sh && export_all_credentials

# Verificar que tenés acceso a todos
check_credentials_status
# Output:
# 🔍 Backend credential status:
#   ✅ Claude
#   ✅ OpenRouter
#   ✅ z.ai
```

#### Inicialización de Proyectos

```bash
# Inicializar mastermind (usa Claude como backend principal)
mm-flow init --org acme-corp --project mastermind
# → Crea ~/.mm-flow/.context.json
# → Resuelve org_id + project_id desde PostgreSQL
# → Listo para ejecutar

# Inicializar prosell-sass (usa z.ai como backend principal)
mm-flow init --org prosell-sass --project paperclip-v3
# → Crea segundo context.json
# → Aislado por RLS en la DB
```

#### Ejecución Normal (Fase por Fase)

```bash
# Ejecutar una fase en vivo
mm-flow execute-phase --phase 19

# Qué ocurre:
# 1. Carga context de ~/.mm-flow/.context.json
# 2. Consulta PostgreSQL: ¿cuántos tokens tiene CADA backend AHORA?
# 3. Selecciona el que tenga MÁS disponibles
# 4. Ejecuta fase, checkpointea cada 10K tokens consumidos
# 5. Si backend < 5K tokens → switchea automáticamente
# 6. Brain #7 valida output antes de guardar
# 7. Actualiza mm_flow_state en PostgreSQL
```

#### 🌙 Night Mode: Ejecución Autónoma (Dormir mientras ejecuta)

**Ideal para:** Fases largas que toman 4-8 horas. Vos dormís, el framework trabaja.

```bash
# Lanzar mastermind a ejecutar toda la noche
mm-flow night-run --project mastermind --phase 19 --max-hours 8

# Qué ocurre:
# • Comienza a las 22:00, se detiene automáticamente a las 6:00 AM
# • LOOP cada 5 minutos:
#   1. Check: ¿hay tokens disponibles en ALGÚN backend?
#   2. Si NO → espera, retry cada 30s (máx 3 intentos)
#   3. Si SÍ → ejecuta siguiente subtask de la fase
#   4. Checkpointea estado en PostgreSQL
#   5. Brain #7 valida output
#      • Si aprobado → continúa
#      • Si rechazado → skip a próximo subtask
# • Safeguards integrados:
#   - Si tokens en TODOS los backends < 10K → PAUSE (safe mode)
#   - Si 3 errores no-recoverable consecutivos → PAUSE
#   - Log completo en ~/.mm-flow/night-run-$(date +%Y-%m-%d).log

# Ejemplo: dos proyectos en paralelo
# Terminal 1:
mm-flow night-run --project mastermind --phase 19 --max-hours 8

# Terminal 2 (el mismo comando funciona, data aislada por org_id):
mm-flow night-run --project paperclip-v3 --phase 1 --max-hours 8

# Ambos usan la misma PostgreSQL, pero RLS garantiza que no se ven datos
```

#### Monitoreo en Tiempo Real

```bash
# Ver estado actual de tokens en TODOS los backends
mm-flow status

# Output esperado:
# Project: mastermind (org_id: acme-corp)
# ┌──────────┬─────────────┬────────┬────────────┬────────────┐
# │ Backend  │ Tokens Used │ Limit  │ Available  │ Hours Reset│
# ├──────────┼─────────────┼────────┼────────────┼────────────┤
# │ claude   │ 85,000      │100,000 │ 15,000 (15%)│ 18.5h    │
# │ openr.   │ 20,000      │128,000 │ 108,000(84%)│ 23.2h    │
# │ z.ai     │ 150,000     │200,000 │ 50,000(25%)│ 4.8h★    │
# └──────────┴─────────────┴────────┴────────────┴────────────┘
# ★ = próximo reset en 4h48m (z.ai tiene 5 resets/día)
#
# Current: z.ai (mejor disponible AHORA)
```

#### Debugging & Logs

```bash
# Ver logs en tiempo real de night-run
tail -f ~/.mm-flow/night-run-2026-04-13.log

# Típico log output:
# 2026-04-13 22:15:23 [INIT] Night run started: mastermind/phase-19, max 8 hours
# 2026-04-13 22:15:24 [CHECK] z.ai: 150K available | Claude: 15K | OpenRouter: 108K
# 2026-04-13 22:15:24 [SELECT] Using z.ai (150K > others)
# 2026-04-13 22:15:30 [EXEC] Subtask 1/50: "Analyze requirements"
# 2026-04-13 22:15:45 [BRAIN7] ✓ Approved output (confidence: 0.92)
# 2026-04-13 22:15:45 [CHECKPOINT] Saved progress: 1/50 subtasks done
# 2026-04-13 22:20:30 [TOKENS] Consumed 25K tokens, z.ai now at 125K
# ... (repeat every 5 min until 6:00 AM)
# 2026-04-14 06:00:00 [PAUSE] Max hours reached, stopping
# 2026-04-14 06:00:00 [SUMMARY] Progress: 28/50 subtasks (56%), safe to resume tomorrow
```

#### PostgreSQL: Ver Estado Interno

```bash
# Conectar a la DB
docker exec mastermind-postgres-1 psql -U postgres -d mastermind_bd

# Ver qué está pasando en mastermind
SELECT * FROM mm_flow_state WHERE project_id = (SELECT id FROM projects WHERE slug = 'mastermind') ORDER BY created_at DESC LIMIT 1;

# Ver tokens consumidos por cada backend
SELECT backend, tokens_used, tokens_limit, 100.0 * tokens_used / tokens_limit as pct_used
FROM backend_sessions
WHERE project_id = (SELECT id FROM projects WHERE slug = 'mastermind')
ORDER BY tokens_used DESC;

# Ver últimos checkpoints (snapshots antes de backend switches)
SELECT checkpoint_reason, created_at FROM context_checkpoints
WHERE project_id = (SELECT id FROM projects WHERE slug = 'mastermind')
ORDER BY created_at DESC LIMIT 5;
```

---

### Mejora de Prompts

```bash
/mm:improve-prompt       # Transforma prompts genéricos en detallados
/mm:ux-spec-to-prompt    # Convierte specs UX en prompts de construcción
```

### Instalación en Proyectos Externos

```bash
# Copiar todos los comandos mm:
cp -r /path/to/mastermind/.claude /path/to/your-project/

# O solo los comandos:
cp -r /path/to/mastermind/.claude/commands/mm /path/to/your-project/.claude/commands/
```

**Ver documentación completa:** `.claude/README.md`

## Sistema de Memoria y Aprendizaje

El framework **recuerda todas las evaluaciones** del cerebro y permite aprender de experiencias pasadas.

```bash
# Ver evaluaciones guardadas
mastermind eval list

# Buscar evaluaciones de un proyecto específico
mastermind eval find prosell-sass

# Buscar por keyword
mastermind eval search "cold-start"

# Ver detalle de una evaluación
mastermind eval show EVAL-2026-03-07-001
```

### Lo que el Framework Aprende

- **Evaluaciones:** Cada vez que el cerebro #7 evalúa, se guarda automáticamente
- **Patrones:** El framework detecta patrones (ej: "Cold Start en 60% de B2C mobile apps")
- **Contexto:** Evaluaciones futuras usan contexto histórico para mejorar decisiones
- **Mejora Continua:** Los cerebros se vuelven más inteligentes con cada proyecto

### Arquitectura de Memoria

```
mastermind-memory/
├── evaluations/
│   ├── hot/       # Últimos 30 días (completo)
│   ├── warm/      # 30-90 días (resumido)
│   ├── cold/      # +90 días (solo patrones)
│   └── archive/   # +1 año (comprimido)
│
└── vector-db/    # Fase 4: Búsqueda semántica (futuro)
```

Para más detalles ver [PRP-009: Memory & Learning System](PRPs/PRP-009-memory-learning-system.md).

- [Stack Tecnológico Estándar](docs/STACK-TECNOLOGICO.md) ⭐
- [PRD Principal](docs/design/00-PRD-MasterMind-Framework.md)
- [Guía de Instalación](tools/mastermind-cli/INSTALL.md)
- [CLI Reference](docs/CLI-REFERENCE.md)
- [Orchestrator Guide](docs/ORCHESTRATOR-GUIDE.md)

## Development Status

| Componente | Estado |
|------------|--------|
| CLI v1.1.0 | ✅ Completo |
| 8 Cerebros | ✅ Activos (132 fuentes) |
| Orquestador | ✅ Funcional |
| Testing Suite | ✅ 31/31 tests passing |
| Installation | ✅ Funcional |
| **Memory System** | ✅ **Fase 1 + 2: Evaluation + Interview Logger** |
| **Brain #8** | ✅ **Master Interviewer / Discovery** |

## Roadmap

| PRP | Descripción | Estado |
|-----|-------------|--------|
| PRP-000 | Initial Setup & Project Structure | ✅ Completo |
| PRP-001 | mastermind-cli Implementation | ✅ Completo |
| PRP-002 | YAML Versioning en Fichas | ✅ Completo |
| PRP-003 | System Prompts de Agentes | ✅ Completo |
| PRP-004 | NotebookLM Integration | ✅ Completo |
| PRP-005 | Brain #7 Evaluator | ✅ Completo |
| PRP-006 | Orchestrator Core | ✅ Completo |
| PRP-008 | Orchestrate Command | ✅ Completo |
| PRP-009 | Memory & Learning System | ✅ **Fase 1: Evaluation Logger** |
| PRP-011 | Brain #8 Core Infrastructure | ✅ Completo |
| PRP-012 | Brain #8 NotebookLM Setup | ✅ Completo |
| PRP-013 | Brain #8 Orchestrator Integration | ✅ Completo |
| PRP-014 | Brain #8 Slash Command (/mm:discovery) | ✅ Completo |
| PRP-015 | Brain #8 Learning System | ✅ Completo |
| PRP-016 | Brain #8 Testing & Polish | ✅ Completo |
| **PRP-017** | **Release v1.1.0** | ✅ **Completo** |

**Próximas Fases (Memory System):**
- Fase 3: SQLite Migration
- Fase 4: Vector Database + RAG

## License

Copyright © 2026 MasterMind Framework. All rights reserved.

---

**Versión:** 1.1.0 | **Estado:** Production Ready
