---
source_id: "FUENTE-318"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Web Typography Guidelines - Best Practices"
author: "Material Design, Apple HIG, WCAG"
expert_id: "EXP-318"
type: "documentation"
language: "en"
year: 2023
distillation_date: "2026-03-02"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-02"
changelog:
  - version: "1.0.0"
    date: "2026-03-02"
    changes:
      - "Destilación inicial completa"
status: "active"
---

# Web Typography Guidelines

## 1. Principios Fundamentales

> **P1: La legibilidad precede a la estética** - La tipografía debe ser legible primero; la expresión artística viene después.

> **P2: La jerarquía visual se logra con contraste** - Diferencias de tamaño, peso y color crean jerarquía, no solo una sola dimensión.

> **P3: El contexto define las reglas** - La tipografía para mobile es diferente de desktop; headings diferentes de body text.

> **P4: La consistencia crea familiaridad** - Un sistema tipográfico consistente reduce carga cognitiva y mejora usabilidad.

## 2. Frameworks y Metodologías

### Type Scale (Escala Tipográfica)

**Major Third (1.250):**
```css
--font-size-xs: 0.64rem;    /* 10.24px */
--font-size-sm: 0.80rem;    /* 12.80px */
--font-size-base: 1.00rem;  /* 16.00px */
--font-size-md: 1.25rem;    /* 20.00px */
--font-size-lg: 1.56rem;    /* 24.96px */
--font-size-xl: 1.95rem;    /* 31.20px */
--font-size-2xl: 2.44rem;   /* 39.06px */
--font-size-3xl: 3.05rem;   /* 48.83px */
```

**Perfect Fourth (1.333):**
```css
--font-size-base: 1rem;     /* 16px */
--font-size-lg: 1.33rem;    /* 21.33px */
--font-size-xl: 1.77rem;    /* 28.44px */
--font-size-2xl: 2.36rem;   /* 37.81px */
--font-size-3xl: 3.16rem;   /* 50.63px */
```

### Line Height (Leading)

| Context | Line Height | Fórmula |
|---------|-------------|---------|
| Body text | 1.5–1.6 | Font size × 1.5 |
| Headings | 1.1–1.3 | Font size × 1.2 |
| Small text | 1.6–1.7 | Font size × 1.65 |

### Line Length (Measure)

- **Optimal**: 60–75 caracteres (incluyendo espacios)
- **Maximum**: 90 caracteres para texto largo
- **Minimum**: 35 caracteres para legibilidad

### Spacing System (Vertical Rhythm)

```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.50rem;  /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1.00rem;  /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.50rem;  /* 24px */
--space-8: 2.00rem;  /* 32px */
--space-10: 2.50rem; /* 40px */
--space-12: 3.00rem; /* 48px */
```

## 3. Modelos Mentales

**Modular Scale**
- Usa ratios consistentes para todos los tamaños
- Crea armonía visual matemática
- Evita tamaños arbitrarios

**Vertical Rhythm**
- Todo está alineado a una grilla vertical
- Espaciado consistente entre elementos
- Múltiplos de un base unit (ej: 8px grid)

**Contraste de Valor**
- El contraste de luminosidad es más importante que el color
- Mínimo WCAG AA: 4.5:1 para texto normal
- Mínimo WCAG AAA: 7:1 para texto largo

## 4. Criterios de Decisión

### Selección de Fuentes

| Tipo | Características | Use Cases |
|------|----------------|-----------|
| Serif | Tradicional, autoridad | Long-form content, publicaciones |
| Sans-serif | Moderno, limpio | UI, apps, web general |
| Display | Decorativo, expresivo | Headings, marketing |
| Monospace | Técnico, código | Code, datos técnicos |

### Web Fonts vs System Fonts

**System Fonts (faster, native feel):**
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
             Roboto, Helvetica, Arial, sans-serif;
```

**Web Fonts (brand, control):**
- Google Fonts, Adobe Fonts, Typekit
- Trade-off: Control de brand vs performance
- Usa font-display: swap para FOUT/FOIT

**Hybrid Approach:**
- System fonts para body text (performance)
- Web fonts para headings (brand differentiation)

### Responsive Typography

```css
/* Base size on mobile */
html { font-size: 16px; }

/* Larger on desktop */
@media (min-width: 1024px) {
  html { font-size: 18px; }
}

/* Scale everything proportionally */
h1 { font-size: 3rem; } /* 48px mobile → 54px desktop */
```

## 5. Anti-patrones

❌ **Demasiadas fuentes en un sistema** - Máximo 2-3 familias; más que eso crea inconsistencia visual.

❌ **Tamaño de fuente fijo en pixels** - Usa rem/em para accesibilidad y escalabilidad.

❌ **Sin contraste de valor suficiente** - No dependas solo del color para contraste; verifica luminosidad.

❌ **Line-height inadecuado** - Demasiado tight (menos de 1.3) o demasiado loose (más de 1.7) reduce legibilidad.

❌ **Justificar texto en web** - Justification crea "rivers" de espacio blanco irregular; usa left-align.

❌ **Usar all-caps para largo** - All-caps reduce legibilidad 15-20%; solo para short labels/acronyms.

## Accessibility Considerations

- **Font size**: Permitir al usuario resize hasta 200% sin romper layout
- **Text spacing**: Permitir ajustar letter-spacing, word-spacing, line-height
- **Font overrides**: Respetar preferencias de usuario para fuentes custom
- **Color contrast**: Verificar con herramientas (WebAIM Contrast Checker)
- **Dyslexia-friendly**: Algunas fonts (OpenDyslexic) ayudan; evitar fonts decorativas

## Technical Implementation

**CSS Variables para Typography System:**
```css
:root {
  /* Font families */
  --font-primary: 'Inter', system-ui, sans-serif;
  --font-secondary: 'Georgia', serif;
  --font-mono: 'Fira Code', monospace;

  /* Sizes (Major Third scale) */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;

  /* Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line heights */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-loose: 1.75;
}
```

## Referencias

- **Material Design Typography**: https://m3.material.io/styles/typography
- **Apple HIG Typography**: https://developer.apple.com/design/human-interface-guidelines/typography
- **WCAG 2.1 Contrast**: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum
- **Butterick's Practical Typography**: https://practicaltypography.com
