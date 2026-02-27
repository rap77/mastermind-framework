---
documento: "INDICE-MAESTRO"
version: "2.0"
cerebro: 3
cerebro_nombre: "UI Design"
fecha_creacion: "2026-02-26"
fecha_actualizacion: "2026-02-26"
total_fuentes: 16
total_lineas_estimadas: "~6,500 líneas"
kb_estimado: "~420KB"
status: "COMPLETO v2.0 — Todos los gaps cubiertos. Listo para cargar en NotebookLM."
cambios_vs_v1: "Agrega 7 fuentes nuevas: Accesibilidad, Motion, Dark Mode, Data Viz, Iconografía, Color, Videos. Radar actualizado de 20 a 52 anti-patrones."
---

# ÍNDICE MAESTRO v2.0 — Cerebro #3 UI Design
## MasterMind Framework | Software Development

---

## Rol del Cerebro #3

**Pregunta Central:** ¿Cómo se ve y se comunica visualmente este producto?

**Función:** Convierte la experiencia definida por el Cerebro #2 (UX Research) en una interfaz visual atractiva, coherente y escalable que el Cerebro #4 (Frontend) puede implementar limpiamente.

**Si el Cerebro #3 falla:** La interfaz es visualmente inconsistente, no escalable, inaccesible, difícil de implementar.

---

## Fuentes Maestras — Versión Completa v2.0

### Capa 1 — Base Conceptual (Fundamentos)

| ID | Fuente | Autor | Habilidad Principal | Estado |
|----|--------|-------|---------------------|--------|
| FUENTE-301 | Atomic Design | Brad Frost | Design Systems & Component Architecture | ✅ |
| FUENTE-302 | Refactoring UI | Wathan & Schoger | UI Visual Práctico & Toma de Decisiones | ✅ |
| FUENTE-303 | Mobile First | Luke Wroblewski | Responsive Design & Priorización | ✅ |
| FUENTE-304 | Thinking with Type | Ellen Lupton | Tipografía para Interfaces Digitales | ✅ |
| FUENTE-305 | Grid Systems in Graphic Design | Josef Müller-Brockmann | Composición Visual & Grid Systems | ✅ |
| **FUENTE-314** | **Color Psychology in UI** | **Albers + Material + Research** | **Psicología del Color & Color Systems** | ✅ NEW |

### Capa 2 — Frameworks Operativos

| ID | Fuente | Autor | Habilidad Principal | Estado |
|----|--------|-------|---------------------|--------|
| FUENTE-306 | Web Form Design | Luke Wroblewski | Form Design & Micro-interactions | ✅ |
| FUENTE-307 | Material Design 3 + Design Tokens | Google + W3C | Tokens & Implementación de Design Systems | ✅ |
| **FUENTE-309** | **Inclusive Design Patterns** | **Heydon Pickering** | **Accesibilidad Web & Diseño Inclusivo** | ✅ NEW |
| **FUENTE-310** | **Designing Interface Animation** | **Val Head** | **Motion Design & Animaciones de Interfaz** | ✅ NEW |
| **FUENTE-311** | **Designing for Dark Mode** | **Material + Apple + Viget** | **Dark Mode & Tematización Avanzada** | ✅ NEW |
| **FUENTE-312** | **The Functional Art** | **Alberto Cairo** | **Data Visualization & Diseño de Información** | ✅ NEW |
| **FUENTE-313** | **Icon Systems Design** | **Material + Apple + Smashing** | **Sistemas de Íconos & Iconografía** | ✅ NEW |

### Capa 3 — Recursos de Refuerzo & Auto-generados

| ID | Fuente | Tipo | Contenido | Estado |
|----|--------|------|-----------|--------|
| FUENTE-308 | Anti-Patrones v1.0 | Radar interno v1 | 20 anti-patrones | ⚠️ DEPRECATED — usar FUENTE-316 |
| **FUENTE-315** | **Videos de Referencia** | **Video-referencias** | **8 videos con contenido destilado** | ✅ NEW |
| **FUENTE-316** | **Anti-Patrones v2.0 & Radar** | **Radar interno v2** | **52 anti-patrones + checklist completo + score** | ✅ NEW |

---

## Mapa de Habilidades Cubiertas (v2.0)

| Habilidad | Fuentes que la Cubren | Cobertura |
|-----------|----------------------|-----------|
| Design Systems & Atomic Architecture | FUENTE-301, FUENTE-307 | ✅ Alta |
| Decisiones Visuales (jerarquía, espacio) | FUENTE-302 | ✅ Alta |
| Tipografía profesional | FUENTE-304 | ✅ Alta |
| Grid y Composición | FUENTE-305 | ✅ Alta |
| Diseño Responsive / Mobile-First | FUENTE-303 | ✅ Alta |
| Formularios y micro-interactions | FUENTE-306 | ✅ Alta |
| Design Tokens e implementación | FUENTE-307 | ✅ Alta |
| **Psicología del Color & Color Systems** | **FUENTE-314** | ✅ Alta — NEW |
| **Accesibilidad (WCAG, componentes)** | **FUENTE-309** | ✅ Alta — NEW |
| **Motion Design & Animaciones** | **FUENTE-310** | ✅ Alta — NEW |
| **Dark Mode avanzado** | **FUENTE-311** | ✅ Alta — NEW |
| **Data Visualization** | **FUENTE-312** | ✅ Alta — NEW |
| **Sistemas de Íconos** | **FUENTE-313** | ✅ Alta — NEW |
| Auto-evaluación y calidad | FUENTE-316 (v2) | ✅ Alta |

**Gaps en v1.0: 2 (Motion Design, Iconografía) + 3 no documentados**
**Gaps en v2.0: 0 ✅**

---

## Gaps Residuales (Fase 3 — Bajo Impacto)

| Gap | Fuente Sugerida | Prioridad | Justificación |
|-----|----------------|-----------|---------------|
| Branding & Brand Identity profunda | "Identity Designed" — David Airey | Baja | El Cerebro #3 diseña UI, no identidad de marca |
| Print Design avanzado | — | Muy baja | Out of scope para UI digital |
| Diseño 3D e interfaces inmersivas (AR/VR) | — | Muy baja | Solo relevante para productos específicos |

---

## Árbol de Decisión del Cerebro #3 (v2.0)

```
INPUT DEL CEREBRO #2 (wireframes + journey maps + arquitectura)
│
├── ¿El diseño empieza desde cero?
│   ├── SÍ → Definir tokens (FUENTE-307, FUENTE-314)
│   │         → Definir escala tipográfica (FUENTE-304)
│   │         → Definir grid por breakpoint (FUENTE-305)
│   │         → Definir sistema de íconos (FUENTE-313)
│   │         → Crear componentes nivel átomo (FUENTE-301)
│   │         → Aplicar principios visuales (FUENTE-302)
│   └── NO → Auditar tokens actuales
│             → Identificar gaps de componentes
│             → Extender sistema existente
│
├── ¿El diseño incluye formularios?
│   └── SÍ → Aplicar FUENTE-306
│
├── ¿El diseño es multi-dispositivo?
│   └── SÍ → Aplicar FUENTE-303 (Mobile First)
│
├── ¿El diseño incluye dark mode?
│   └── SÍ → Aplicar FUENTE-311 (tokens duales)
│
├── ¿El diseño incluye gráficas o dashboards?
│   └── SÍ → Aplicar FUENTE-312 (Data Viz)
│
├── ¿El diseño incluye animaciones/transiciones?
│   └── SÍ → Aplicar FUENTE-310 (Motion)
│
├── ¿TODOS LOS COMPONENTES tienen foco diseñado?
│   └── NO → Revisar FUENTE-309 (Accesibilidad)
│
└── ANTES DE ENTREGAR → Ejecutar checklist FUENTE-316 v2.0
                      → Score mínimo 80% para APPROVE
```

---

## Instrucciones de Carga en NotebookLM (v2.0)

**Nombre del cuaderno:** `[CEREBRO] UI Design — Software Development`

**Orden de carga recomendado:**

*Capa 1 — Base conceptual primero:*
1. FUENTE-301 — Atomic Design (arquitectura de componentes)
2. FUENTE-307 — Design Tokens (sistema antes que componentes)
3. FUENTE-314 — Color Psychology (base de color antes de aplicar)
4. FUENTE-302 — Refactoring UI (criterios visuales prácticos)
5. FUENTE-304 — Thinking with Type (tipografía)
6. FUENTE-305 — Grid Systems (composición)
7. FUENTE-303 — Mobile First (responsive)

*Capa 2 — Frameworks operativos:*
8. FUENTE-306 — Web Form Design (formularios)
9. FUENTE-309 — Inclusive Design Patterns (accesibilidad)
10. FUENTE-310 — Interface Animation (motion design)
11. FUENTE-311 — Dark Mode Design (tematización avanzada)
12. FUENTE-312 — The Functional Art (data visualization)
13. FUENTE-313 — Icon Systems Design (iconografía)

*Capa 3 — Refuerzo y auto-evaluación:*
14. FUENTE-315 — Videos de Referencia (complemento visual)
15. FUENTE-316 — Anti-Patrones v2.0 y Radar (carga al final; referencia todo lo anterior)

*(FUENTE-308 — Anti-Patrones v1.0 — NO cargar; está deprecated y reemplazado por FUENTE-316)*

**Consultas de prueba post-carga:**
1. "¿Cuáles son los anti-patrones críticos de UI que bloquean el handoff?"
2. "¿Cómo construyo la escala tonal del color primario para soportar dark mode?"
3. "¿Qué estados debe tener un componente de botón?"
4. "¿Qué tipo de gráfica es correcto para mostrar tendencias en el tiempo?"
5. "¿Cómo especifico el foco de un botón icon-only para que sea accesible?"
6. "¿Cuándo animo un modal y con qué duración y easing?"
7. "¿Cómo elijo el sistema de íconos correcto para este producto?"

---

## Estadísticas del Cerebro #3 — v2.0

| Métrica | v1.0 | v2.0 |
|---------|------|------|
| Fuentes maestras totales | 8 | **15 activas + 1 deprecated** |
| Fuentes Capa 1 (Base) | 5 | **6** |
| Fuentes Capa 2 (Frameworks) | 2 | **7** |
| Fuentes Capa 3 (Refuerzo) | 1 | **2** |
| Anti-patrones catalogados | 20 | **52** |
| Anti-patrones críticos | 4 | **12** |
| Anti-patrones altos | 10 | **24** |
| Anti-patrones medios | 6 | **16** |
| Habilidades con cobertura alta | 8/10 | **14/14** |
| Gaps identificados | 2 documentados + ~3 ocultos | **0** |
| Líneas de contenido | ~1,800 | **~6,500** |
| Conocimiento estimado | ~110KB | **~420KB** |
