---
source_id: "FUENTE-311"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Designing for Dark Mode — Guía Consolidada"
author: "Compilación: Material Design 3 (Google) + Human Interface Guidelines (Apple) + Viget Research"
expert_id: "EXP-311"
type: "guide"
language: "es"
year: 2024
url: "https://m3.material.io/styles/color/dark-theme"
skills_covered: ["H1", "H5"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada con destilación completa"
      - "Formato adaptado a estándar del MasterMind Framework"
      - "Cubre gap de Dark Mode identificado en v1.0"
status: "active"

# Metadatos específicos del Cerebro #3
habilidad_primaria: "Dark Mode Design & Tematización Avanzada"
habilidad_secundaria: "Color Systems para Múltiples Contextos & Tokens Semánticos"
capa: 2
capa_nombre: "Frameworks Operativos — Tematización"
relevancia: "ALTA — El dark mode es hoy una expectativa estándar del usuario, no una feature premium"
---

# FUENTE-311 — Designing for Dark Mode
## Guía Consolidada | Material Design 3 + Apple HIG + Mejores Prácticas

---

## Tesis Central

> El dark mode no es "poner todo en negro". Es un sistema de color paralelo con sus propias reglas de contraste, elevación, saturación y composición. Un dark mode bien diseñado no invierte colores; reinterpreta la jerarquía visual en un contexto de baja luminosidad.

El 82% de usuarios activan dark mode cuando está disponible. No es una feature opcional; es una expectativa del producto moderno.

---

## Principios Fundamentales

### Principio 1 — Dark Mode No es Inversión de Colores

El error más común: `filter: invert(1)` en CSS o simplemente intercambiar negro y blanco.

**Por qué falla:**
- Los colores saturados (azul #0066FF) invertidos se vuelven naranjas (#FF9900) — incoherente con el brand
- Las imágenes y fotos quedan distorsionadas
- Las sombras (que en light mode van hacia abajo) pierden su semántica
- El contraste puede empeorar, no mejorar

**La aproximación correcta:** Dos sistemas de tokens paralelos que comparten los tokens primitivos pero mapean diferente en los semánticos.

### Principio 2 — Fondos Dark No son Negros Puros

```
❌ MAL: Fondo = #000000 (negro puro)
✅ BIEN: Fondo = #121212 (Material) o #1C1C1E (Apple)
```

**Por qué:**
- Negro puro causa un efecto "smearing" en pantallas OLED cuando el texto blanco se mueve
- El contraste excesivo (negro + blanco puro) fatiga los ojos más que un gris oscuro
- Los colores de elevación (superficies sobre el fondo) necesitan espacio para diferenciarse

**Escala de fondos dark mode (Material Design 3):**
```
Nivel 0 — Fondo base:        #121212
Nivel 1 — Superficie:        #1E1E1E (+8% blanco de overlay)
Nivel 2 — Superficie elevada: #222222 (+12% blanco)
Nivel 3 — Cards / Dialogs:   #272727 (+16% blanco)
Nivel 4 — App bars:          #2C2C2C (+24% blanco)
```

### Principio 3 — La Saturación Debe Reducirse en Dark Mode

Los colores altamente saturados en fondo oscuro causan efecto de vibración visual (especialmente azules y rojos puros).

```
Light mode: Primary = #1976D2 (saturación alta)
Dark mode:  Primary = #90CAF9 (mismo matiz, saturación reducida, luminosidad aumentada)
```

**Regla:** En dark mode, usar tonos más claros y menos saturados de los colores de marca para que no "vibren" contra el fondo oscuro.

### Principio 4 — La Elevación se Comunica con Luz, no Sombras

En light mode: la elevación se comunica con sombras (más sombra = más alto).
En dark mode: las sombras son casi invisibles sobre fondos oscuros.

**Solución de Material Design:** Usar overlays de color blanco semitransparente para indicar elevación.
```
Elemento más elevado → Surface más clara (más overlay)
Elemento menos elevado → Surface más oscura (menos overlay)
```

**Regla para el Cerebro #3:** En dark mode, rediseñar la semántica de elevación. Las sombras de light mode no se transfieren; necesitan tokens específicos para dark.

### Principio 5 — Contraste en Dark Mode Tiene Sus Propias Reglas

En dark mode, el contraste excesivo también es un problema. El texto blanco (#FFFFFF) sobre negro puro (#000000) da 21:1 de contraste — demasiado para lectura cómoda prolongada.

**Rango recomendado para texto en dark mode:**
- Texto principal: contraste 15.8:1 (no máximo, cómodo)
- Texto secundario: contraste 7:1 (WCAG AAA)
- Texto terciario/disabled: contraste 4.5:1 (WCAG AA mínimo)

---

## Framework Principal — Sistema de Tokens para Dark Mode

### Arquitectura de Tokens de 3 Capas

```
CAPA 1 — PRIMITIVOS (valores absolutos, no cambian entre temas)
  ├── color.blue.100: #E3F2FD
  ├── color.blue.200: #BBDEFB
  ├── color.blue.400: #42A5F5
  ├── color.blue.700: #1976D2
  ├── color.blue.900: #0D47A1
  └── (completa la paleta de cada color)

CAPA 2 — SEMÁNTICOS (mapean primitivos a roles; CAMBIAN por tema)
  Light Mode:
    ├── color.primary: color.blue.700 (#1976D2)
    ├── color.on-primary: color.white (#FFFFFF)
    ├── color.primary-container: color.blue.100 (#E3F2FD)
    └── color.on-primary-container: color.blue.900 (#0D47A1)

  Dark Mode:
    ├── color.primary: color.blue.200 (#BBDEFB)  ← más claro, menos saturado
    ├── color.on-primary: color.blue.900 (#0D47A1) ← oscuro sobre claro
    ├── color.primary-container: color.blue.900 (#0D47A1) ← invertido
    └── color.on-primary-container: color.blue.100 (#E3F2FD)

CAPA 3 — COMPONENTE (referencian semánticos; NUNCA valores directos)
  └── button.background: color.primary
  └── button.text: color.on-primary
```

### Tabla de Mapeo Light → Dark (Material Design 3)

| Token semántico | Light Mode | Dark Mode |
|-----------------|-----------|-----------|
| `color.background` | #FAFAFA | #121212 |
| `color.surface` | #FFFFFF | #1E1E1E |
| `color.surface-variant` | #F5F5F5 | #2C2C2C |
| `color.on-background` | #1C1B1F | #E6E1E5 |
| `color.on-surface` | #1C1B1F | #E6E1E5 |
| `color.outline` | #79747E | #938F99 |
| `color.primary` | #6750A4 | #D0BCFF |
| `color.on-primary` | #FFFFFF | #381E72 |
| `color.error` | #B3261E | #F2B8B5 |
| `color.on-error` | #FFFFFF | #601410 |

### Checklist de Dark Mode para el Cerebro #3

```
TOKENS
☐ ¿Todos los tokens semánticos tienen valor para dark mode?
☐ ¿Los colores de brand tienen versión dark con saturación reducida?
☐ ¿Los tokens de elevación son específicos por tema?
☐ ¿Los tokens de sombra tienen versión dark (normalmente más transparentes)?

FONDOS Y SUPERFICIES
☐ ¿El fondo base es ~#121212 (no negro puro)?
☐ ¿Hay escala de elevación visible en dark (diferencia entre superficie y fondo)?
☐ ¿Los cards y modals tienen suficiente diferencia con el fondo?

TIPOGRAFÍA
☐ ¿El texto principal está sobre #E6E1E5 (no blanco puro)?
☐ ¿El texto secundario tiene contraste ≥ 4.5:1 en dark?
☐ ¿El texto disabled es visible pero claramente diferenciado del secundario?

COLORES DE ESTADO
☐ ¿El color de error en dark es más claro/pastel (#F2B8B5) que en light?
☐ ¿El color de éxito en dark también es versión clara?
☐ ¿Los colores de estado son distinguibles entre sí en dark mode?

IMÁGENES E ÍCONOS
☐ ¿Las imágenes tienen ligera reducción de brillo en dark mode?
☐ ¿Los íconos de color se adaptan o tienen versión dark?
☐ ¿Los logos tienen versión para fondo oscuro?

COMPONENTES ESPECÍFICOS
☐ ¿Los inputs tienen borde visible en dark (el fondo del input vs. el fondo de página)?
☐ ¿Los separadores/dividers tienen suficiente contraste en dark?
☐ ¿Los overlays (tooltips, dropdowns) tienen fondo oscuro apropiado?
```

---

## Casos por Componente

### Inputs en Dark Mode

```
PROBLEMA: Input con fondo blanco en light mode se convierte en un
          "agujero" de luz en dark mode.

SOLUCIÓN MATERIAL:
  Light: fondo blanco, borde outline sutil
  Dark: fondo surface-variant (#2C2C2C), borde outline visible

SOLUCIÓN APPLE:
  Light: fondo gris claro
  Dark: fondo gris oscuro pero más claro que el fondo de página
```

### Cards en Dark Mode

```
PROBLEMA: En light mode, el card se diferencia por sombra.
          En dark mode, la sombra no se ve.

SOLUCIÓN: El card tiene background surface (#1E1E1E) sobre
          background (#121212) — la diferencia de tono crea la separación.

OPCIÓN ALTERNATIVA: Borde sutil (outline) de 1px en el card en dark mode.
```

### Gráficas y Datos en Dark Mode

```
PROBLEMA: Los colores de datos diseñados para light (saturados, medios)
          se ven mal en dark (demasiado agresivos o invisibles).

SOLUCIÓN: Paleta de datos con 2 versiones:
  Light: #1976D2, #388E3C, #F57C00, #D32F2F (saturados, medios)
  Dark:  #90CAF9, #A5D6A7, #FFCC80, #EF9A9A (claros, pastel)
```

---

## Anti-Patrones de Dark Mode

**ADM-01 — Solo cambiar el fondo a negro sin ajustar nada más**
Todos los colores de texto, botones, estados siguen siendo los del light mode. Resultado: algunos contrastan demasiado, otros son invisibles.

**ADM-02 — Imágenes sin tratamiento**
Las fotografías brillantes se ven descontextualizadas en un fondo oscuro. Necesitan una sutil reducción de brillo o un vignette.

**ADM-03 — Colores de acento sin versión dark**
El azul primario #0066FF en dark mode vibra agresivamente contra el fondo oscuro y puede no pasar el contraste adecuado.

**ADM-04 — Estado "disabled" invisible en dark**
El gris que se usaba para disabled en light mode puede desaparecer contra fondos oscuros. Necesita su propio token.

**ADM-05 — Sombras copiadas de light mode sin ajuste**
`box-shadow: 0 4px 8px rgba(0,0,0,0.5)` en dark mode es invisible. Las sombras en dark necesitan mayor opacidad o reemplazarse por overlays de color.

---

## Conexión con el Cerebro #3

| Habilidad del Cerebro #3 | Aporte de esta fuente |
|--------------------------|----------------------|
| Design Tokens & sistema de color | Arquitectura de 3 capas + mapeo completo light/dark |
| Escalabilidad del design system | Un sistema de tokens bien diseñado soporta dark mode sin rediseño |
| Handoff limpio a Frontend (#4) | Especificación de tokens por tema; no valores hardcodeados |
| Contraste y accesibilidad | Reglas de contraste específicas para dark mode |

## Preguntas que el Cerebro #3 puede responder con esta fuente

1. ¿Cuál es el valor correcto de este token en dark mode?
2. ¿Cómo estructura la paleta de elevación en dark mode?
3. ¿Este color de brand tiene suficiente contraste en dark mode?
4. ¿Cómo adapto el sistema de sombras para dark mode?
5. ¿Qué pasa con las imágenes y fotos en dark mode?
6. ¿Cómo defino los tokens para que el switch light/dark sea automático?
