# brain-02 (UX Research) — Phase 06 Command Center Consultation

**Date:** 2026-03-20
**Brain:** brain-02-ux-research
**Notebook:** ea006ece-00a9-4d5c-91f5-012b8b712936

---

## User Journeys

### Journey 1: Navegación por Nicho
El usuario ingresa al Command Center y, gracias al semantic clustering, su carga cognitiva se reduce al identificar 3 grupos lógicos (Master, Software, Marketing) en lugar de 24 elementos, aplicando chunking para manejar memoria de trabajo.

### Journey 2: Interacción y Diagnóstico
Al localizar una brain tile en Software, usuario hace hover para activar Ghost Context. Sistema proporciona feedback inmediato vía animaciones Cyberpunk y datos WebSocket.

---

## Pain Points

### 1. Sobrecarga en Nicho de Marketing
Marketing tiene 16 tiles, violando Ley de Miller (5-9 elementos) y Ley de Hick.

### 2. Falta de Signifiers en Reposo
Ghost Context corre riesgo de ocultar affordances.

### 3. Inaccesibilidad en Mobile
Mini-grid 3x8 viola Ley de Fitts (targets < 44x44px).

---

## Opportunities

### 1. Sub-clustering para Marketing
Dividir 16 elementos en sub-categorías (Analytics, Social, Ads).

### 2. Signifiers de Estado Persistentes
Pulsos de color/íconos sutiles visibles ANTES del hover.

---

## Screen Flows

### Flow 1: Dashboard → Foco en Nicho
Clic en encabezado de nicho → otros clusters se colapsan (Progressive Disclosure).

### Flow 2: Tile → Modal Expandido
Clic → modal línea única → Shift+Enter → expande detalles.

---

## Research Methodology

1. Evaluación Heurística (Nielsen H8, H6)
2. Guerrilla Usability Testing (5 usuarios)
3. Assumption Mapping (estética Cyberpunk vs legibilidad)

---

## Answers to Questions

### Q1: ¿Semantic clustering mitiga Miller's Law?
**Parcialmente.** Marketing (16) necesita sub-clustering.

### Q2: ¿Ghost Context + hover es suficiente?
**NO.** Falta signifiers persistentes.

### Q3: ¿Mobile: Lista prioritaria vs mini-grid?
**SÍ, lista es mejor.** Mini-grid viola Fitts's Law.

### Q4: ¿Collapse/expand por nicho es right abstraction?
**SÍ confirmado.**

---

*Saved: 2026-03-20*
