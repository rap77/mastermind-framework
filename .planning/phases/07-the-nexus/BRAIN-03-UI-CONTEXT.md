# Brain-03 UI Design — Phase 07: The Nexus

**Date:** 2026-03-22

---

## Visual Language
Cyber-Blueprint War Room. Dark mode, high-contrast. Forma sigue función — elementos visuales solo existen para comunicar datos o cambios de estado.

## Color Palette
- `#64FFDA` — Neon Cyan: hub activo (Coordinator) + nodos iluminados
- `#8892B0` — Muted Slate: ghost idle states + secondary edges
- `#FF3D00` — Vivid Red-Orange: error states + high-priority alerts
- `#0B0C10` — Deep Obsidian background (no pure black — evita OLED smearing)
- `#E6E1E5` — Off-White: texto high-contrast

## Typography
- Heading: Inter 700 Bold
- Body: Inter 400 Regular
- Mono: JetBrains Mono — Brain IDs + WS event logs en tiempo real

## Spacing
8px base grid. Escala: 4-8-16-24-32-48-64. Elimina layout shifts.

## Components

### NexusBrainNode
5 estados: Blueprint (dashed, 20% opacity), Active (neon glow), Error (pulsing red-orange), Cooldown (solidified), Disabled. `nodrag nopan` en todos los elementos internos.

### HybridFlowEdge
"Meaningful Motion" — dirección comunica flujo de datos. Live: "data pulse" neon. Cooldown: "Data-Latched" con glow permanente.

### EventSidePanel
shadcn/ui Sheet, right-aligned fixed. Jerarquía visual: headings grandes para KPIs, monospace para event streams. Info crítica visible en < 3 segundos.

## Design Principles
1. **Hierarchy through Illumination** — color/glow reservados para elementos activos. Idle = grayscale blueprint
2. **Redundant State Communication** — nunca solo color. Siempre color + icono + label
3. **Motion as Communication** — animaciones 100-300ms, propósito funcional. Siempre respetar `prefers-reduced-motion`
