# Phase 06: Command Center - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

## Phase Boundary

**Command Center** — Bento Grid visual de 24 cerebros + modal de brief input estilo Raycast. Los usuarios pueden ver el estado en vivo de todos los cerebros y enviar briefs desde una interfaz de comandos rápida (Cmd+K). El Bento Grid se organiza por nichos (Software/Marketing/Master) con clustering visual inteligente. El modal soporta menciones @ jerárquicas, comandos slash (/), y feedback visual en tiempo real de qué cerebros se ejecutarán.

**Scope:** NO incluye The Nexus (DAG), Strategy Vault, Engine Room, o UX Polish — esas son fases 7 y 8.

---

## Implementation Decisions

### Layout del Bento Grid

**Dynamic Semantic Clusters (Priority Hub)**
- Brain Master (orquestador) ocupa tile doble/triple en el centro como "Sol" del sistema
- 23 cerebros restantes se agrupan por Nicho alrededor del Master
- Cerebros activos se expanden levemente o brillan con borde Magic UI
- Cerebros idle se mantienen compactos

**Semantic Glow & Ghost Headers (Hybrid Approach)**
- Títulos sutiles en tipografía monospace (estilo terminal) por grupo
- Cuando un nicho entra en acción, contenedor completo emite Glow del color del nicho
- Color coding por nicho:
  - Master (1): zinc-100 (Neutral/Silver) — Steady Pulse
  - Software (7): cyan-400 (Electric Blue) — Scanning Line
  - Marketing (16): purple-500 (Royal Purple) — Glow Expansion

**Hybrid Smart Spacing (Context-Aware)**
- gap-2 interno entre tiles del mismo nicho
- gap-8 entre contenedores de nicho
- Separación semántica visual (Gestalt de Agrupación)

**Interactive Pulse Mode (Mobile Contextual)**
- Header: resumen visual de nichos (🟢1 🔵7 🟣16)
- Body: cerebros active/error arriba con detalle completo
- Idle: agrupados en acordeón colapsable por nicho al final

### Contenido del Brain Tile

**Ghost Context (Interactive Minimal)**
- Visual: Minimalista (Icono + Nombre + Punto de color)
- Funcional: Al hover o active, aparecen métricas + niche tag con transición suave

**Semantic Polymorphism (Métricas Inteligentes)**
- Detecta tipo de cerebro y cambia métrica automáticamente:
  - Estrategia (LLM): Tokens/sec + Model Name (ej. "14 t/s | Claude 3.5")
  - Inventario (Scripts): Progress % + Items Found (ej. "65% | 12 autos")
  - Infraestructura (DevOps): Latency + CPU/RAM del contenedor
- Sparkline de Magic UI para actividad últimos 30s

**Focus Elevation (Semantic Scale)**
- Idle: Grid unit 1x1 minimalista
- Active: Se eleva (shadow) + expande (Grid unit 2x1 o 2x2) desplazando vecinos
- Revela Semantic Polymorphism + mini-log en tiempo real
- Usa layoutId de Framer Motion para transiciones fluidas

**Tactical Quick-Actions (Direct Control)**
- Overlay de acción minimalista al hover
- ACTIVE: STOP + FOLLOW LOGS (mini-popover stream en vivo)
- IDLE/ERROR: RETRY/START + EDIT CONFIG (YAML)
- Extra: COPY OUTPUT si terminó exitoso
- React 19 Server Actions para disparar a FastAPI

### Animaciones de Estado

**Adaptive Cyberpunk (Performance-First Glow)**
- Reposo: Minimalista con Tailwind 4 (ahorra GPU)
- Acción: Cinemático con Magic UI BorderBeam + gradientes neón solo en tiles active
- Crítico: Error emite pulso rojo orgánico que ilumina vecinos (Ambient Glow)
- Economía de Atención: Brillo solo donde hay trabajo

**Neural Connectivity Pulse (Ghost Pulse) — Idle**
- Solo icono + punto de estado tienen latido de opacidad (0.4 ↔ 1.0) cada 4-5s
- Los 23 cerebros NO pulsan al mismo tiempo (delay aleatorio)
- Si WebSocket se desconecta, pulso se detiene + icono se vuelve gris
- Optimización GPU: Solo anima icono pequeño

**Neural Activity Pulse & Flow — Active**
- Magic UI BorderBeam (luz neón recorre perímetro)
- Velocidad dinámica: ∝ carga (tokens/seg)
- Shimmer interno (opacity 0.05) para volumen
- Detección de "Stalling": Luz estática/lenta = proceso colgado

**Glitch & Static Pulse — Error**
- Shake inicial + estado Glitch (parpadeo rojo/cian rápido)
- BorderBeam rojo neón, velocidad x3
- Glitch se calma tras 3s, deja borde rojo pulsante constante
- Diferenciación clara de "roto" vs "terminado"

### Modal de Brief Input

**Semantic Auto-Expand (Input Inteligente)**
- Estado inicial: Single-line 60px, font-mono (comandos rápidos)
- Comportamiento: Si supera una línea o Shift+Enter → expande a textarea auto-ajustable (máx 400px)
- Visual: Borde brilla (ring-1) del color del nicho seleccionado predominantemente

**Hierarchical Smart-Select (Cascada de Menciones)**
- Contexto de Nicho: @ sugiere nichos primero, al elegir marca visualmente cerebros en Bento Grid
- Refinamiento Individual: @marketing/inst... muestra cerebros específicos de ese grupo
- Multi-Select: @software @marketing-lead selecciona grupo + específico
- Sincronización Zustand: Tiles reaccionan con resplandor suave mientras escribes

**Intent-Aware Context (Comandos con Payload)**
- Comandos de Acción: /scrape, /analyze, /deploy
- Encadenamiento: /scrape @inventory [url] → comando = función, mención = target, resto = payload
- Transformación Visual: Input cambia color según comando (azul /deploy, naranja /analyze)
- Bypass LLM: Comandos se envían directo como WS Event, ahorra tiempo/dinero

**Semantic Execution Ghost (Pre-vuelo Técnico)**
- Targeting Visual: Mini-avatares Lucide de cerebros seleccionados, nicho con multiplicador ([📢 Marketing x16])
- Costo de Operación: Estimación dinámica de peso de tarea (Low/Med/High)
- Dry Run Path: Línea font-mono tenue traduce natural a función interna: -> strategy.analyze(context: "honda_civic")

### Claude's Discretion

- Exacta implementación de Framer Motion layoutId para Focus Elevation
- Duración exacta de transiciones Tailwind 4
- Implementación específica de Sparkline (Magic UI vs custom)
- Tamaño exacto de tiles en Grid units (1x1, 2x1, 2x2)

---

## Specific Ideas

**Niche-Based Clustering (Agrupación Inteligente)**
- No son 24 cuadros al azar — se agrupan por función (Inventory, Marketing, Strategy)
- Cerebros de mismo nicho comparten contenedor visual con bordes animados cuando trabajan coordinados
- Magic UI Animated Beam conecta visualmente nichos (línea de luz del Master al cluster)

**Priority Hub Architecture**
- Brain Master como "Sol" central — tile doble o triple
- Nichos orbitan alrededor del Master
- Cerebros activos se expanden/brillan, idle se compactan

**Supervisión Pasiva**
- Reconocimiento Periférico: Destello púrpura desde rabillo del ojo = Marketing terminó tarea
- No necesitás cambiar de pestaña para saber estado

**useOptimistic (React 19)**
- Si clic en Retry, icono empieza a girar inmediatamente
- UI se siente instantánea antes de que WebSocket confirme recepción

**Zod Schemas meta: {}**
- Backend FastAPI puede enviar campo meta: {} en WS events
- Frontend Next.js 16 interpreta para dibujar contador correcto (tokens vs progress vs CPU)

---

## Existing Code Insights

### Reusable Assets

**Components (apps/web/src/components/):**
- `components/ui/card.tsx` — shadcn/ui Card para tiles
- `components/ui/button.tsx` — shadcn/ui Button para acciones
- `components/ui/input.tsx` — shadcn/ui Input para modal
- `components/ws/WSBrainBridge.tsx` — WebSocket bridge ya implementado

**Stores (apps/web/src/stores/):**
- `brainStore.ts` — Map<brainId, BrainState> con useBrainState(id) selector
- `wsStore.ts` — WebSocket connection management
- RAF batching ya implementado (WS-02 requirement cumplido)

**Types (apps/web/src/types/api.ts):**
- `BrainEventSchema` — brain_id, status (idle/active/complete/error), timestamp
- `WSMessageSchema` — task_update_batch envelope

**Libraries:**
- Zustand 5 + Immer (state management)
- Tailwind 4 (styling)
- shadcn/ui (base components)
- Magic UI (Bento Grid, BorderBeam, animations)
- React 19 (useOptimistic, useTransition)
- Framer Motion (layout animations)
- Lucide React (icons)
- cmdk (command palette)

### Established Patterns

**Targeted Selectors:** `useBrainState(id)` previene cascade re-renders (WS-03)

**RAF Batching:** brainStore acumula eventos y los drena antes de cada paint (60fps)

**Zod Validation:** WS events validados antes de actualizar Zustand

**JWT Auth:** httpOnly cookies + Server Components ya implementados (Phase 05)

### Integration Points

**Frontend Route:** `/` (War Room) en `apps/web/src/app/(protected)/page.tsx`

**Backend API:**
- `GET /api/brains` — BE-01 gap, debe implementarse en 06-01
- `POST /api/tasks` — submit brief
- WebSocket: `ws://api:8000/ws` — ya conectando en wsStore

**Data Flow:**
1. Usuario abre Command Center → GET /api/brains (popula grid inicial)
2. Usuario escribe brief → Modal muestra preview
3. Usuario presiona Enter → POST /api/tasks → taskId
4. WebSocket recibe task_update_batch → brainStore.updateBrain() → tiles animan

---

## Deferred Ideas

**None** — Discussion stayed within phase scope. Niche-Based Clustering fue integrado naturalmente en las decisiones de layout y no es scope creep.

---

*Phase: 06-command-center*
*Context gathered: 2026-03-20*
