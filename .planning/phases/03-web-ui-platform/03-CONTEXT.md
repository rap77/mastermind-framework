# Phase 3: Web UI Platform - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

## Phase Boundary

Full-featured web dashboard with real-time progress visualization and multi-user session support. This phase transforms the CLI-only framework into a production-ready platform with browser-based orchestration, live progress monitoring, and HTTP API for external integrations.

**Out of scope:**
- Real-time collaborative editing — separate phase
- Multi-tenant SaaS infrastructure — single-tenant deployment only
- Mobile apps — web-first with mobile-responsive CSS
- Advanced ML features (v3.0+)

**Requirements mapeados:** UI-01 a UI-10, ARCH-03, PAR-08, PERF-02 a PERF-04 (15 requirements)

## Implementation Decisions

### Autenticación & Sesiones

**Mecanismo Híbrido:**
- **Web UI**: JWT (Access token 30min + Refresh token 24h con rotación)
  - Refresh Token Rotation para revocación segura
  - "Remember me" extiende refresh token a 7 días
- **CLI**: API Keys (Personal Access Tokens)
  - Token de larga duración generado desde dashboard
  - `Authorization: Bearer <token>` header
  - Una sola configuración con `mm auth login --key=...`

**Storage: Encrypted DB Store (Vault Pattern)**
- Todo en SQLite: `users` table + `api_keys` table + `sessions` table
- Campos sensibles encriptados en reposo (ENV_VAR clave maestra)
- Relaciones SQL: users ↔ api_keys ↔ executions
- Consistente con Phase 2 (SQLite para task state)

**User Management: Single → Multi Evolution**
- Phase 3: Admin user por defecto (primer arranque pide crearlo)
- Sin RBAC, password recovery, email validation por ahora
- Foco 100% en Dashboard + WebSockets perfectos
- Multi-user UI para Phase 4

**Session Timeout: Hybrid Context-Aware**
- **CLI**: API Key persistente (no expira, protegido por Linux user)
- **Web UI**: 1 hora inactividad + Silent Refresh durante ejecución brains
- Pestaña cerrada → sesión muere en 30 min
- Ejecución en curso → timeout extendido automáticamente

### Dashboard Layout & UI

**Layout: Hybrid Command Center (IDE Style)**
- **Sidebar izquierdo**: Navegación rápida entre flujos (colapsable)
- **Bento Grid central**: KPIs + Grafo DAG protagonista
- **Panel inferior**: Logs en tiempo real del brain seleccionado (colapsable)

**Organización de tarjetas Bento Grid:**
- **60%**: Grafo DAG interactivo (23 nodos)
- **20%**: Métricas de Salud (fallos, latencia)
- **20%**: Proveedores (rate limiting Claude/NotebookLM)

**Visualización de Brains: Layered Dependency Tree**
- Estilo CI/CD (GitHub Actions, Jenkins)
- Brains organizados en stages verticales (orden topológico)
- Conexiones fluyen izquierda → derecha
- Camino crítico visible instantáneamente

**Estados en tiempo real (nodos):**
- 🔳 **Gris (Pending)**: Esperando dependencias
- 🔵 **Azul Animado (Running)**: Procesando (spinner/progress bar)
- 🟢 **Verde (Completed)**: Éxito (hover = resumen output)
- 🔴 **Rojo (Failed)**: Error (nodo palpita + botón "Analyze Root Cause")
- 🟡 **Amarillo (Skipped)**: Blast radius (dependencia falló)

**Librería de grafo:** React Flow (backend-agnostic, D3-based)

**Theme: System-Adaptive (Fluid)**
- Detección automática de preferencia OS/navegador
- Acentos dinámicos por estado:
  - Gris azulado en reposo
  - Verde esmeralda cuando todo va bien
  - Rojo neón si hay fallo crítico

**Paleta "Cyber-Modern":**
- Fondos profundos (#0F172A)
- Bordes sutiles + "glow" suave
- Tipografía: JetBrains Mono o Geist Mono

**Densidad: Semantic Density (Contextual)**
- **Grafo DAG**: Spacious (entender conexiones)
- **Logs + Tabla Estados**: Compact (máximo dato visible)
- **Zoom-dependent density**:
  - Alejado: solo colores
  - Acercado: IDs, tiempos, estados detallados

### Real-time Updates

**Streaming Strategy: Smart Focus + Throttled UI (300ms)**
- **Solo streaming detallado** del brain seleccionado/en foco
- **Los otros 22 brains**: solo metadata (estado, progreso)
- **Batch update** cada 300ms con un solo JSON
- **Browser rendering**: 1 update por 300ms vs 23×60 por segundo

**Implementación técnica:**
```python
# Backend accumula tokens por brain_id
buffer = {brain_id: [] for brain_id in brains}

# Cada 300ms, envía SSE batch
for event in accumulated_events:
    if event.brain_id == focused_brain:
        send_full_chunk(event.tokens)  # Streaming detallado
    else:
        send_metadata(event.status, event.progress)  # Solo estado
```

**Reconexión: Ghost Mode 3-Tier**
| Duración del corte | Estrategia |
|-------------------|------------|
| **< 30s** | Server buffer (~100 events en memoria) → reconexión transparente |
| **30s - 5min** | Ghost Mode (UI desaturada + contador "hace Xs") → Resync desde SQLite |
| **> 5min** | Manual refresh / error |

**Ghost Mode visual:**
- UI desaturada (opacity 0.6)
- Contador "Last sync: 2m ago" pulsando
- Al volver: **resaltar cambios** que ocurrieron offline ("Brain #7 completó mientras no estabas")
- Overlay sutil "Reconnecting..." sin bloquear

**Fallback: Smart Degradation (Hybrid Polling)**
- SSE fail → auto-switch a polling
- **Frecuencia adaptativa:**
  - 23 brains running → polling agresivo (1-2s)
  - Sistema idle tras 3 intentos sin cambios → polling relajado (10s)
  - Nueva interacción del usuario → vuelve a agresivo
- Reutiliza endpoints GET /api/tasks/state del Ghost Mode
- Compatible con cualquier proxy/firewall

**Server Buffer:**
- **100 events (~30s)** en memoria (deque maxlen=100)
- Reconexión < 30s → reenvía último historial
- Reconexión > 30s → falla a Ghost Mode
- Overhead: ~50KB en memoria por task

**Resync desde SQLite:**
- SQLite de Phase 2 tiene historial completo de transiciones
- Server no necesita mantener nada en memoria
- Reconnect con `last_event_id` → server consulta tabla de transiciones

### Observability & Debugger

**Logs Panel: Fixed Bottom Drawer**
- Drawer colapsable tipo terminal (WSL2/CLI familiar)
- **Filter pill**: "All Brains" → click nodo → "Filter: Brain #5"
- **Multitasking**: ver grafo arriba + logs abajo
- Scroll automático al último log (opcional)

**Trace Back: Ripple Effect (Hover Insight)**
- Hover sobre nodo fallido → atenúa todo excepto camino de ancestros
- Visualización del fallo:
  - 🔴 Nodo palpita con glow rojo
  - 🔗 Líneas de conexión rojas y más gruesas
  - 📋 Bottom Drawer resalta último error del primer ancestro fallido
- Botón "Analyze Root Cause" aparece solo cuando hay fallo
- Al pulsar: zoom al origen + ilumina camino completo

**SQLite Inspector: Interactive SQL Console**
- Panel con área de texto para queries SQL
- `SELECT * FROM brain_states WHERE status = 'failed'`
- Resultados en rejilla dinámica
- **Exportar:** CSV / JSON
- **Corrección manual:** si brain stuck en "running" → cambiar a "failed"
- Solo lectura sugerido (para evitar corrupción)

### Mobile Responsiveness

**Estrategia: Tactical Mirror (Hybrid)**
- **Móvil**: List-View vertical + botón flotante para Snapshot estático
- **Desktop**: Grafo interactivo completo

**List-View (mobile):**
- Encabezado "Estado Global" (ej: "Running 15/23")
- Lista ordenada por flujo de ejecución
- Indicadores grandes: ✅❌🔵 círculos de colores
- Touch en elemento → expande mini-viewer con últimas 5 líneas de log
- Botón flotante → Snapshot estático del grafo (imagen/SVG)

**Desktop First Priority:**
- **90% foco**: Bento Grid, Grafo interactivo, Logs en monitor estándar
- **Responsividad sutil**: Tailwind CSS para mobile utilizable (sin obsesión)
- **WSL2 Workflow**: dashboard como monitor secundario mientras programas
- **Móvil como salvavidas**: verificar si proceso terminó desde la cocina

**Architectura Note:**
- API & CLI son la prioridad (Headless-First)
- Dashboard es consumidor más, no el core
- Framework = herramienta de productividad para developer, no app de consumo

### Claude's Discretion

- Valor exacto de throttling (300ms es razonable, pero puede ajustarse)
- Tamaño del server buffer (100 events ~30s)
- Umbral exacto de Ghost Mode (30s, 5min pueden ajustarse)
- Frecuencia de polling adaptativo (1s, 2s, 10s - configurable)
- Diseño exacto del Snapshot estático (PNG, SVG, PDF)
- Cantidad de líneas en mini-viewer móvil (5 es sugerencia)

## Specific Ideas

- "Quiero evitar que un glitch de red de 2 segundos arruine 10 minutos de trabajo" → Ghost Mode con buffer
- "Cuando estoy en el móvil, solo quiero saber: ¿Falló algo?" → List-View con indicadores grandes
- "Zira es mi monitor secundario mientras programa" → Desktop First, mobile como salvavidas
- "WSL2 me programó para mirar abajo buscando output" → Fixed Bottom Drawer tipo terminal

**Referencias técnicas:**
- GitHub Actions CI/CD pipeline visualization
- VS Code split view (editor + terminal)
- Jenkins blue ocean dashboard
- Linear issue cards density

## Existing Code Insights

### Reusable Assets

**Phase 2 (Parallel Execution):**
- `mastermind_cli/state/database.py` → SQLite async connection (WAL mode)
- `mastermind_cli/state/models.py` → `TaskRecord`, `TaskState` Pydantic models
- `mastermind_cli/state/repositories.py` → `TaskRepository` (CRUD operations)
- `mastermind_cli/orchestrator/dependency_resolver.py` → Kahn's algorithm (topological sort)
- `mastermind_cli/orchestrator/brain_executor.py` → `ParallelExecutor` con TaskGroup

**Phase 1 (Type Safety):**
- `mastermind_cli/types/coordinator.py` → `CoordinatorRequest`, `CoordinatorResponse`
- `mastermind_cli/types/parallel.py` → `FlowConfig`, `TaskState`, `ProviderConfig`
- Pydantic v2 models con discriminated unions para YAML configs

### Established Patterns

- **Async/await**: todo el código usa asyncio + aiosqlite
- **Pydantic validation**: runtime validation en todos los boundaries
- **SQLite persistence**: WAL mode, async operations
- **YAML configs**: brains.yaml, flows.yaml, providers.yaml

### Integration Points

**FastAPI backend:**
- `mastermind_cli/api/` → nuevo módulo para FastAPI app
- WebSocket endpoint: `/ws/tasks/{task_id}` → SSE events
- REST endpoints: `/api/tasks/{id}`, `/api/tasks/{id}/state`
- Auth endpoints: `/api/auth/login`, `/api/auth/refresh`

**State Store:**
- Reutilizar `TaskRepository` de Phase 2
- Agregar tabla `users`, `api_keys`, `sessions` para auth
- Agregar tabla `events` para SSE buffering (opcional, puede ser solo memoria)

**Frontend:**
- Static files en `mastermind_cli/web/` (HTMX + Alpine.js)
- O React/Svelte app separado en `web/` directory
- Integración con FastAPI static files

## Deferred Ideas

**Out of scope para Phase 3:**
- Real-time collaborative editing (v3.0+)
- Multi-tenant SaaS infrastructure
- Native mobile apps (iOS/Android)
- Advanced ML features (auto-improvement)
- Hot-reload de brains sin restart

**Noted para roadmap backlog:**
- Type-aware auto-completion en Web UI (Monaco editor)
- Custom metrics dashboard (success rate, brain usage charts)
- Template library para reusable execution patterns
- Granular permissions (per-brain, per-niche RBAC)

---

*Phase: 03-web-ui-platform*
*Context gathered: 2026-03-13*
