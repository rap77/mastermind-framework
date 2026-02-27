---
source_id: "FUENTE-307"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Material Design 3 + Design Tokens (W3C Standard)"
author: "Google Design Team + W3C Design Tokens Working Group"
expert_id: "EXP-307"
type: "documentation"
language: "en"
year: 2023
url: "https://m3.material.io"
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
status: "active"

# Metadatos específicos del Cerebro #3
habilidad_primaria: "Design Tokens & Implementación de Design Systems"
habilidad_secundaria: "Tematización y Consistencia Cross-Platform"
capa: 2
capa_nombre: "Frameworks — Design Systems de Producción"
relevancia: "ALTA — Los tokens son el puente entre Figma y código; sin ellos el design system muere en el handoff"
---

# FUENTE-307 — Material Design 3 + Design Tokens
## Google Design + W3C | El Puente entre Diseño y Código

---

## Tesis Central

> Un design system sin tokens es una colección de imágenes. Un design system con tokens es una fuente de verdad que vive tanto en Figma como en el código. Los tokens son el lenguaje compartido que hace posible que el diseño y el desarrollo hablen el mismo idioma.

Material Design 3 no es solo un conjunto de componentes bonitos; es una demostración a escala de cómo se construye un sistema de diseño que puede ser implementado, mantenido y evolucionado por equipos grandes durante años.

---

## 1. PRINCIPIOS FUNDAMENTALES

**P1 — Design Tokens: la abstracción entre intención y valor**
Un token es una variable con nombre semántico que mapea a un valor visual.
NO: `color: #1976D2` (un valor)
SÍ: `color-primary: #1976D2` (un token)
MEJOR: `color-button-primary-background: {color-primary}` (token de componente que referencia token global)

**P2 — Los tokens tienen jerarquía**
Los tokens globales definen todos los valores posibles del sistema.
Los tokens de semántica/alias definen el propósito de cada valor.
Los tokens de componente definen cómo se usan en componentes específicos.
Esta jerarquía permite cambiar un color global y ver el efecto en cascada.

**P3 — El sistema de temas es una consecuencia natural de los tokens**
Si los componentes usan tokens de semántica (no valores directos), cambiar el tema es solo cambiar el mapeo de tokens. Light mode → dark mode es redefinir 20 tokens, no 2000 cambios manuales.

**P4 — Material Design como caso de estudio, no como restricción**
M3 no es obligatorio de implementar; es el mejor ejemplo público de cómo se piensa un design system de escala. Sus principios (elevación, color roles, motion, typography scale) son aplicables independientemente de si el producto usa Material o no.

**P5 — La especificación W3C de tokens permite interoperabilidad**
Los tokens en formato estándar (JSON/DTCG) pueden exportarse de Figma y consumirse directamente en código con herramientas como Style Dictionary. Esto elimina la capa de "traducción manual" del handoff.

---

## 2. FRAMEWORKS Y METODOLOGÍAS

### Framework 1: Jerarquía de Design Tokens

```
NIVEL 1 — GLOBAL TOKENS (Primitive / Raw)
  Todos los valores posibles del sistema, sin contexto semántico
  Nomenclatura: {categoría}-{escala}

  Ejemplos:
  color-blue-100: #E3F2FD
  color-blue-500: #2196F3
  color-blue-900: #0D47A1

  spacing-4: 4px
  spacing-8: 8px
  spacing-16: 16px

  font-size-12: 12px
  font-size-16: 16px
  font-weight-400: 400
  font-weight-700: 700

NIVEL 2 — SEMANTIC / ALIAS TOKENS
  Tokens que tienen propósito pero no especifican componente
  Nomenclatura: {propósito}-{variante}-{estado}
  Mapean a Global Tokens, no a valores directos

  Ejemplos:
  color-primary: {color-blue-500}
  color-primary-hover: {color-blue-700}
  color-background-page: {color-neutral-50}
  color-text-primary: {color-neutral-900}
  color-text-secondary: {color-neutral-600}
  color-text-disabled: {color-neutral-400}
  color-border-default: {color-neutral-200}
  color-error: {color-red-600}
  color-success: {color-green-600}

NIVEL 3 — COMPONENT TOKENS
  Tokens específicos de un componente; mapean a Semantic Tokens
  Nomenclatura: {componente}-{elemento}-{propiedad}-{estado}

  Ejemplos:
  button-primary-background-default: {color-primary}
  button-primary-background-hover: {color-primary-hover}
  button-primary-text-default: {color-on-primary}
  button-primary-border-radius: {radius-md}

  input-background-default: {color-background-input}
  input-border-default: {color-border-default}
  input-border-focus: {color-primary}
  input-border-error: {color-error}
  input-text-placeholder: {color-text-secondary}
```

### Framework 2: Sistema de Color M3 (Color Roles)

Material Design 3 introduce "Color Roles" — un sistema donde cada color tiene un rol semántico con un "on-color" para texto/iconos:

```
ROLES DE COLOR EN M3:

Primary          → Acción principal, CTA, elementos de énfasis
On Primary       → Texto/iconos sobre Primary (contraste garantizado)
Primary Container → Variante de baja énfasis del primary
On Primary Container → Texto/iconos sobre Primary Container

Secondary        → Apoyo al primary, énfasis medio
On Secondary     → Texto/iconos sobre Secondary

Tertiary         → Contraste complementario al primary
On Tertiary      → Texto/iconos sobre Tertiary

Surface          → Fondos de cards, sheets, dialogs
On Surface       → Texto/iconos sobre Surface
Surface Variant  → Fondos alternativos de menor énfasis
On Surface Variant → Texto sobre Surface Variant

Background       → Fondo base de la app
On Background    → Texto sobre Background

Error            → Estados de error
On Error         → Texto/iconos sobre Error

Outline          → Borders, divisores
Outline Variant  → Borders sutiles

CÓMO APLICARLO:
→ Nunca usar colores hex directamente en componentes
→ Siempre referenciar un Color Role
→ El "On" color garantiza contraste WCAG automáticamente

PARA DARK MODE:
→ Solo redefinir el mapeo de Color Roles a valores hex
→ Los componentes no cambian; los tokens cambian
```

### Framework 3: Elevación y Sombras en M3

M3 usa "tonal elevation" (elevación tonal) en lugar de sombras puras para dark mode:

```
SISTEMA DE ELEVACIÓN:

Level 0: Sin elevación (superficie base)
Level 1: Sombra muy sutil (4dp) → Chips, Cards no interactivos
Level 2: Sombra pequeña (8dp) → Cards interactivos, Filled buttons
Level 3: Sombra media (12dp) → FABs, Navigation Drawers
Level 4: Sombra alta (16dp) → Modals
Level 5: Sombra máxima (24dp) → Bottom Sheets completos

EN LIGHT MODE:
  → Sombra caja (box-shadow) con opacidades variables

EN DARK MODE:
  → Sombras son menos visibles en oscuro
  → M3 usa "surface tint" (tinte con color primario) para comunicar elevación
  → Mayor nivel = más tinte del color primario en el fondo
```

### Framework 4: Exportación de Tokens (Flujo Figma → Código)

```
HERRAMIENTAS Y FLUJO:

1. FIGMA (Diseño)
   → Variables de Figma (2023+): reemplazo de estilos, soporte nativo de tokens
   → Plugin "Tokens Studio" para gestión avanzada
   → Exportar como JSON formato DTCG (Design Token Community Group)

2. STYLE DICTIONARY (Transformación)
   → Input: tokens en JSON
   → Output: CSS custom properties, SCSS variables, JS/TS constants, iOS plist, Android XML
   → Configurar transformaciones por plataforma

3. CÓDIGO (Consumo)
   CSS:  var(--color-primary)
   SCSS: $color-primary
   JS:   tokens.colorPrimary
   iOS:  colorPrimary

4. SINCRONIZACIÓN
   → Cuando diseñador cambia token en Figma → export JSON → Style Dictionary transforma
   → Developer consume la nueva versión de los tokens
   → Cambio de 1 token se propaga automáticamente a toda la app
```

---

## 3. MODELOS MENTALES

**MM1 — "¿Qué cambia si cambia esto?"**
Antes de decidir si algo es un token global, semántico o de componente, pregunta: si cambio este valor, ¿qué más debería cambiar automáticamente? Si la respuesta es "todo el sistema", es global. Si es "todos los elementos primarios", es semántico. Si es "solo este componente", es de componente.

**MM2 — "Los tokens son el contrato entre diseño y desarrollo"**
Cuando diseñador y developer usan el mismo token name, están hablando del mismo valor. Cuando el diseñador cambia un token, el developer lo ve en su código. El token es el acuerdo; el valor es la implementación.

**MM3 — "Dark mode es un reemplazo de mapeos, no de diseños"**
Si tienes que rediseñar componentes para dark mode, los tokens están mal configurados. Un sistema bien tokenizado produce dark mode cambiando 20-30 mapeos de tokens; los componentes en sí no cambian.

---

## 4. CRITERIOS DE DECISIÓN

**CD1 — ¿Cuándo adoptar Material Design vs. crear sistema propio?**
Adoptar M3: cuando el tiempo es crítico, el equipo es pequeño, el producto es utilitario/interno.
Crear propio: cuando la identidad de marca es diferenciadora, el sistema de M3 choca con los principios visuales del producto, o el equipo tiene capacidad de mantener el sistema.
Adoptar M3 como base y personalizar: el caso más común y recomendado; usar la arquitectura de M3 con los tokens de marca propia.

**CD2 — ¿Variables de Figma o plugin de tokens?**
Variables de Figma nativas (2023+): suficiente para la mayoría de productos, mejor integración, más simple.
Tokens Studio plugin: cuando necesitas multi-platform output, gestión de múltiples temas, integración con repositorio git.
Regla: empezar con variables nativas; migrar a plugin cuando la complejidad lo requiera.

**CD3 — ¿Cuántos tokens necesita un sistema?**
Sistema pequeño (startup, MVP): 30-50 tokens semánticos + tokens de componentes básicos.
Sistema mediano (producto establecido): 100-200 tokens.
Sistema enterprise (multi-producto): 500+ tokens con estructura compleja.
Regla: empezar mínimo y crecer cuando el sistema lo demande; no crear tokens para casos que no existen.

---

## 5. ANTI-PATRONES

**AP1 — "Valores hardcodeados en componentes"**
Síntoma: el componente button tiene `color: #1976D2` directamente.
Consecuencia: cambiar el color primario requiere buscar y reemplazar en todos los componentes.
Corrección: `color: var(--color-primary)` — el componente referencia el token, nunca el valor.

**AP2 — "Tokens sin semántica"**
Síntoma: tokens como `blue-500` usados directamente en componentes.
Consecuencia: cuando el primario cambia de azul a verde, `blue-500` sigue siendo azul aunque ya no sea el primario. El sistema se rompe.
Corrección: El componente usa `color-primary`, que mapea a `blue-500`. Cuando el primario cambia, solo cambia el mapeo de `color-primary`.

**AP3 — "Un token por cada posibilidad"**
Síntoma: `button-primary-padding-top`, `button-primary-padding-right`, `button-primary-padding-bottom`, `button-primary-padding-left` como tokens separados.
Consecuencia: el sistema se vuelve inmanejable; 500 tokens para un sistema de 20 componentes.
Corrección: `button-primary-padding` con un valor shorthand. Granularidad cuando hay variación real, no por principio.

**AP4 — "Dark mode como afterthought"**
Síntoma: el dark mode se añade al final del proyecto manualmente, pantalla por pantalla.
Consecuencia: inconsistencias entre pantallas, alto costo de mantenimiento, probablemente siempre incompleto.
Corrección: Diseñar el sistema de color con dark mode en mente desde el inicio; los Color Roles de M3 son un excelente modelo.

---

## 6. CASOS Y EJEMPLOS REALES

**Caso 1: Airbnb — Implementación de Design Tokens a escala**
Situación: Airbnb con 3 plataformas (web, iOS, Android) y un equipo de 30+ diseñadores necesitaba coherencia sin fricción.
Solución: Sistema de tokens centralizado con exportación automatizada a cada plataforma.
Resultado: Un cambio de color de marca se propaga a las 3 plataformas en horas, no semanas. La coherencia cross-platform mejoró mediblemente.

**Caso 2: Shopify Polaris — Dark Mode con Tokens**
Situación: Añadir dark mode al Admin de Shopify afectando cientos de componentes.
Solución: Con la arquitectura de tokens en lugar, dark mode fue redefinir los mapeos de ~40 tokens semánticos.
Resultado: Dark mode lanzado sin rediseñar ningún componente individual. El trabajo fue de ingeniería (tokens), no de diseño.

**Caso 3: Google Material You (M3) — Tematización dinámica**
Situación: Android 12+ genera una paleta de color personalizada basada en el wallpaper del usuario.
Implementación: M3 con Color Roles permite que las apps adopten automáticamente la paleta del sistema.
Resultado: Las apps Material 3 se "personalizan" con el color del usuario sin código adicional de los desarrolladores de la app. Solo posible porque los componentes usan Color Roles, no valores directos.

---

## Conexión con el Cerebro #3

| Habilidad del Cerebro #3 | Aporte de esta fuente |
|--------------------------|----------------------|
| Crear sistemas de diseño escalables con tokens | Framework completo de jerarquía de tokens |
| Garantizar handoff limpio a Frontend (#4) | Flujo Figma → JSON → Código con herramientas |
| Diseñar para dark mode y tematización | Color Roles y tematización por tokens |
| Especificar elevación y sombras sistemáticamente | Sistema de elevación de M3 |

## Preguntas que el Cerebro #3 puede responder con esta fuente

1. ¿Cómo estructuro los tokens de este design system en 3 niveles?
2. ¿Qué Color Roles necesito definir para este producto?
3. ¿Cómo implemento dark mode sin rediseñar componentes?
4. ¿Cómo exporto los tokens de Figma al código?
5. ¿Cuántos tokens necesita este sistema de diseño?
