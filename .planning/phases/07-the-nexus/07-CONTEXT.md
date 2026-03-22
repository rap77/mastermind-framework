# Phase 07: The Nexus - Context

**Gathered:** 2026-03-22
**Status:** Ready for brain consultation + planning

<domain>
## Phase Boundary

The Nexus es un monitor de ejecución en tiempo real y atlas del sistema. Users ven el DAG de orquestación de 24 cerebros (star topology: Coordinator como hub, brains como satélites), observan cómo se iluminan durante la ejecución via WebSocket, e inspeccionan cada nodo individualmente. Historial de ejecuciones pasadas, timeline scrubbing, y variable injection son fuera de scope — pertenecen a Phase 08.

</domain>

<decisions>
## Implementation Decisions

### Entry Point & Navigation

- **Ruta propia:** `/nexus` — pantalla dedicada, URL shareable, estado persistente en refresh
- **Navegación desde Command Center:** Al submitear un brief, navegación inmediata a `/nexus` — arrancar con Nexus Skeleton mientras el backend procesa; cuando llega el `task_id`, los nodos reales emergen del esqueleto
- **Complejidad de la animación de entrada:** Depende del tiempo — puede simplificarse a navigate inmediato si la Speculative Animation agrega riesgo
- **Scope de tasks:** Live-First — muestra la task activa de la sesión actual; footer con flechas `[<] [>]` para navegar entre tasks de la sesión (Zustand en memoria, sin backend); redirige a Strategy Vault para historial histórico
- **Sin auto-redirect:** Al terminar una task, el Nexus NO navega automáticamente a otra pantalla

### Idle State (Ghost Architecture)

- **Canvas no vacío:** Al entrar sin task activa, mostrar los 24 nodos en "Blueprint" style — líneas punteadas, opacidad 20%, sin colores de nicho — cargados desde `GET /api/brains` (ya existe)
- **Interactivo en idle:** Clic en nodo → Side Panel con config estática del cerebro (nombre, nicho, capabilities list del YAML, con qué otros brains del nicho suele trabajar)
- **Transición a active:** Al iniciar un brief, los nodos involucrados se iluminan con color de nicho; el resto se desvanece a 5% de opacidad
- **Session counter por nodo:** Badge pequeño mostrando cuántas veces fue invocado en la sesión actual (Zustand en memoria)

### Post-Execution (Cooldown Mode)

- **Graph persiste:** Al recibir `task_completed`, el Nexus entra en modo Read-Only (Ghost Trace) — nodos quedan visibles con su estado final
- **Visual shift:** Background del canvas cambia de azul oscuro a gris casi negro para indicar que ya no es live monitor
- **Edges solidifican:** `animated: false`, estado final: verde+glow (success), línea punteada roja parpadeante (error)
- **Floating Action Bar (FAB):** Aparece al completar con 3 acciones:
  - `[Enter]` → volver al Command Center
  - `[V]` → ver en Strategy Vault (Phase 08 destino, link por ahora)
  - `[R]` → re-ejecutar (ver "Day 2" abajo)
- **Keyboard-first:** Auto-focus en FAB al completar — shortcuts activos sin necesidad de mouse
- `[Esc]` → limpia el Ghost Trace, vuelve a Ghost Architecture sin salir de `/nexus`

### Node Detail (Side Panel)

- **Posición:** Panel lateral derecho fijo — canvas se achica ~30% al abrirse
- **Datos en ejecución:** Status badge (idle/active/complete/error), último evento WS recibido, timestamp, niche context (otros brains activos del mismo nicho)
- **Datos en idle:** Config estática del cerebro (nombre, nicho, capabilities del YAML)
- **Actualización:** Live-binding via `useBrainState(id)` — panel actualiza en tiempo real sin re-fetch
- **Click en nodo Coordinator:** Muestra cuántos brains invocó, estado de orquestación general
- `nodrag nopan` en todos los elementos interactivos dentro del nodo (NEX-03)

### Edge Animations (Hybrid Flow)

- **Base:** React Flow `animated: true` nativo (stroke-dashoffset) — 60fps garantizado
- **Estilo:** Neon glow via Tailwind 4 `drop-shadow` + color del nicho activo; dirección cambia (outgoing = instrucción del Coordinator, incoming = respuesta del brain)
- **Velocidad sintética:** CSS `transition-timing-function: ease-in` basado en tiempo transcurrido desde que el nodo entró en PROCESSING — sin datos de latencia del backend
- **Data-Latching post-complete:**
  - `active` → flujo animado con color de nicho
  - `complete` → `animated: false`, glow estático verde (cable "lleno")
  - `error` → línea punteada roja parpadeante (`animate-pulse`)
- **Topología:** Star — Coordinator como hub central (nodo más grande, glow constante), 24 brains como satélites; agrupados visualmente por color de nicho

### Ghost Trace (Data Prep)

- **State Snapshots en brainStore:** Durante ejecución, push de `{ timestamp, brainStates: Map snapshot }` a un `historyStack` array en Zustand con cada evento WS
- **No UI de scrubbing en Phase 07** — data disponible para inspección en consola; UI timeline → Phase 08

### Claude's Discretion

- Exacta implementación del Nexus Skeleton (animación de partículas vs. skeleton nodes genéricos)
- Algoritmo dagre — radial layout vs. hierarchical (elegir el que quede mejor visualmente con 24 nodos)
- Exact stroke-width y drop-shadow values para el neon glow
- Cómo manejar la sesión nav footer (`[<] [>]`) si solo hay 1 task en sesión

</decisions>

<specifics>
## Specific Ideas

- **"Orchestrator Star":** El Coordinator tiene un glow constante (siempre encendido). Es visualmente el corazón. Los 23 cerebros son satélites que "despiertan" cuando el Coordinator les da paso.
- **"Ghost Architecture":** El estado idle NO es una pantalla muerta. Es el mapa del sistema — líneas punteadas, azul tenue, esperando activación. Como un circuito sin corriente.
- **"The Cooldown":** Cuando la task termina, el canvas se "enfría" — colores se apagan gradualmente, cables quedan con glow suave. Hay una barra flotante (FAB) con shortcuts tipo Raycast.
- **Color-coding por nicho:** Neon cyan para Software (7 brains), neon purple para Marketing (16 brains), zinc/white para Master Coordinator. Los edges heredan el color del nicho activo.
- **Side panel como "Ficha Técnica":** En idle, el panel muestra las capabilities del brain como una lista. El usuario puede preparar su brief sabiendo exactamente qué "poderes" tiene cada cerebro.

## Day 2 Features (dentro de Phase 07, baja prioridad)

- **[R] Contextual Re-Run:** `BriefInputModal` como overlay sobre el Nexus en Cooldown, pre-poblado con el último brief. Reutiliza el componente existente. Si el tiempo apremia → simplificar a link al Command Center.
- **Speculative Navigation completa:** Zoom-out del Bento Grid → travel animation → Nexus Skeleton → emerge. Si complejo → simplificar a navigate inmediato + Skeleton visible al cargar.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets

- `brainStore.ts` — Map<brainId, BrainState> + `useBrainState(id)` selector: base para leer estado de cada nodo en tiempo real. Extender con `historyStack` para Ghost Trace.
- `wsStore.ts` + `WSBrainBridge.tsx` — WS connection ya probada. The Nexus subscribes al mismo store.
- `BriefInputModal.tsx` — Reutilizable para el Contextual Re-Run ([R] en Cooldown FAB).
- `shadcn/ui Card` (`/components/ui/card.tsx`) — Base para BrainNode custom en React Flow.
- `shadcn/ui Sheet` — Candidato para el Side Panel derecho (drawer lateral).
- `react-query.tsx` — TanStack Query provider ya configurado (misma arquitectura que Phase 06).

### Established Patterns

- **Per-brain selectors:** `useBrainState(id)` — pattern a replicar en BrainNode (no re-renders en cascada)
- **Zod validation antes de Zustand:** WS events se validan con `WSMessageSchema.safeParse()` antes de actualizar el store
- **RAF batching:** `updateBrain()` usa `requestAnimationFrame` para batch updates — resuelto el Immer pattern
- **TanStack Query para server state:** `GET /api/brains` data → React Query; WS events → Zustand
- **NODE_TYPES a module level** (ya en REQUIREMENTS.md, NEX-01): evita re-renders infinitos del canvas

### Integration Points

- `/nexus` route necesita un nuevo `page.tsx` bajo `apps/web/src/app/(protected)/nexus/`
- `BriefInputModal.tsx` → al submitear, navegar a `/nexus` (modificar el `onSubmit` handler)
- `WSBrainBridge` → montar en el layout de `/nexus` igual que en Command Center
- Backend: `GET /api/tasks/{id}/graph` necesita validar/extender para incluir `layout_positions`

### Backend Gap

- `tasks.py:97` — `TODO: Integrate with Coordinator.orchestrate()` — el Coordinador no se ejecuta al crear una task. Plan 07-01 debe evaluar si el graph endpoint puede funcionar con el estado actual o si necesita mock data mientras tanto.

</code_context>

<deferred>
## Deferred Ideas

- **Timeline Scrubbing UI** — Barra inferior para rebobinar el estado del DAG. Data (historyStack) se captura en Phase 07; la UI va en Phase 08 Strategy Vault.
- **Heatmap de uso histórico** — Requiere `/api/brains/usage` endpoint (no existe). Phase 08 con datos reales de DB.
- **Variable injection at runtime** — Inyectar parámetros al proceso Python desde el panel. Requiere nueva API de control de ejecución. Phase 09+.
- **Data Particles (custom SVG)** — Puntos de luz viajando por edge paths. Deferido por riesgo de 60fps con 24 nodos. Evaluar post-Phase 07.
- **WS events con `duration_ms` y `payload_kb`** — Extender schema para velocidad/grosor real de edges. Deferred para no romper WS schema estable. Phase 08.
- **Deep linking:** `/nexus?task=123&focus=brain-7` — Focus automático en nodo específico. Phase 08.
- **Parallel Routes (@slot)** — Nexus y Command Center coexistiendo simultáneamente en dos monitores. Phase 08 o v2.2.

</deferred>

---

*Phase: 07-the-nexus*
*Context gathered: 2026-03-22*
*Discussed: Entry Point, Idle State, Node Detail Panel, Edge Animations, Ghost Trace*
