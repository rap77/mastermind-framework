# Brain-02 UX Research — Phase 07: The Nexus

**Date:** 2026-03-22
**Source:** mm orchestrate run --use-mcp

---

## User Journeys

### Journey 1: Real-time Monitoring
El usuario entra a The Nexus y ve el "Ghost Architecture" idle. Al triggerear una task, el Coordinator (brain-08) se ilumina primero, seguido por los satélites activados en secuencia via WebSocket. El usuario observa las animaciones Hybrid Flow para trackear la progresión lógica del DAG — feedback inmediato sobre la salud de la orquestación.

### Journey 2: Post-Mortem Analysis
Después del `task_completed`, el sistema entra en Cooldown Mode. El usuario usa keyboard shortcuts ([V] o [R]) para navegar el Ghost Trace history stack, revisando snapshots de brain states en el `brainStore`. Esto permite "bridge the Gulf of Evaluation" — interpretar cómo se llegó al estado final sin reiniciar el proceso.

---

## Pain Points

### Cognitive Overload en High-Concurrency
Con 24 brains emitiendo eventos simultáneos, el usuario puede experimentar "firehose effect". Si la jerarquía visual no distingue entre primary path illumination y secondary status updates, el usuario luchará para escanear la info más crítica.

**Mitigation:** Star topology natural mapping ya resuelve esto — el Coordinator siempre es el foco primario. Los brains satélites de nichos inactivos deben estar a 5% opacidad durante ejecución.

### Ambiguous Signifiers
Si los "niche colors" en los edges animados no están claramente mapeados a significados de estado (data transfer vs. simple trigger), el usuario puede tener un mental model incorrecto de la orquestación.

**Mitigation:** Redundant State Communication — nunca comunicar estado solo por color. Siempre combinar color + icono + label.

---

## Opportunities

### Natural Mapping de la Star Topology
Posicionar el Coordinator como hub central crea un **natural mapping** que coincide con el modelo conceptual del usuario ("controller y satellites"). Reduce el tiempo de comprensión del sistema.

### Progressive Disclosure via Side Panel
El canvas permanece minimalista. El shadcn/ui Sheet con live-binding a estados detallados permite deep-dive on-demand sin contaminar la vista principal.

---

## Research Methodology

- **Evaluative Research** via Heuristic Evaluation — Nielsen's principles: Visibility of System Status + Error Prevention
- **Guerrilla Testing** con 5 usuarios → identifica ~85% de usability issues de performance (60fps) y cognitive load
- **Assumption Mapping** para validar que Star Topology coincide con el mental model del target audience (power-user developers)

---

## Screen Flows

1. **NexusCanvas (Idle) → NexusCanvas (Active):** Nodes en blueprint → WS signal en brainStore → nodo transiciona a "Illuminated" con neon glow
2. **NexusCanvas (Active) → Side Panel:** User clickea nodo → Sheet slide-out → logs WS en tiempo real + config, sin perder el estado visual del DAG

---

## Key UX Decisions para el Planner

- Jerarquía visual: Coordinator siempre el foco más brillante (hub de atencion)
- Progressive disclosure: canvas minimalista + Side Panel on-demand
- Ghost Architecture idle: nunca canvas vacío — "el sistema está listo"
- Cooldown Mode: time for reflection, no interrumpir con auto-redirect
- Error states: redundant communication (color + icono + texto)
