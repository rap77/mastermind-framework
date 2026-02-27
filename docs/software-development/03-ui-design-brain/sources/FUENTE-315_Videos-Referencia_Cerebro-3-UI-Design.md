---
source_id: "FUENTE-315"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Videos de Referencia — Recursos en Video del Cerebro #3"
author: "Brad Frost + Adam Wathan + Femke van Schoonhoven + Figma Config Talks"
expert_id: "EXP-315"
type: "video-collection"
language: "en"
year: 2024
url: "Múltiples — ver catálogo dentro de la ficha"
skills_covered: ["H1", "H3", "H5"]
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
habilidad_primaria: "Aprendizaje Visual & Refuerzo de Conceptos"
habilidad_secundaria: "Casos de Estudio en Video & Workflows Reales"
capa: 3
capa_nombre: "Refuerzo Visual — Videos"
relevancia: "MEDIA — Los videos de referencia son complemento, no fuente primaria"
---

# FUENTE-315 — Videos de Referencia
## Cerebro #3 UI Design | Catálogo de Videos por Tema

---

## Propósito de Esta Ficha

Los videos de referencia no reemplazan las fuentes primarias (libros, guías), pero son el complemento ideal para:
- Ver conceptos en acción (no solo leer sobre ellos)
- Onboarding rápido antes de usar la fuente completa
- Actualización continua (los videos de conferencias como Figma Config son anuales)
- Casos de estudio en tiempo real de diseñadores expertos

**Nota para NotebookLM:** Esta ficha contiene las descripciones y contenidos destilados de los videos, no los videos en sí. NotebookLM no puede reproducir video.

---

## Catálogo de Videos por Tema

---

### Tema 1 — Design Systems & Atomic Design

**VIDEO-315-01**
**Título:** "Building a Design System from Scratch" — Brad Frost
**URL:** https://www.youtube.com/watch?v=EK-pHkc5EL4
**Duración:** ~45 minutos
**Nivel:** Intermedio-Avanzado

**Contenido destilado:**
- Demostración en vivo de cómo Brad Frost construye un design system desde átomos
- El proceso de auditoría de un interfaz existente para encontrar patrones repetidos
- Cómo nombrar los componentes para que tengan sentido tanto para diseñadores como para developers
- El momento crítico: cuándo extraer un componente vs. cuándo mantener el one-off
- Integración de Storybook con Figma para sincronizar design y código

**Insight clave:** Brad demuestra que el 80% de los componentes de cualquier aplicación son variaciones de 20 componentes base. Identificar esos 20 es el trabajo real del design system.

**Cuándo ver este video:** Antes de iniciar un design system desde cero, o cuando se está auditando un sistema existente.

---

**VIDEO-315-02**
**Título:** "The Messy Edges of Design Systems" — Figma Config 2023
**URL:** https://www.youtube.com/watch?v=LKs2YeKMSCY
**Duración:** ~30 minutos
**Nivel:** Avanzado

**Contenido destilado:**
- Por qué los design systems nunca están "terminados" (y no deberían estarlo)
- Los 3 tipos de componentes que siempre causan conflicto en equipos: los "casi iguales", los de excepciones, y los de una sola pantalla
- Cómo manejar el versionado de componentes cuando el producto está en producción
- La tensión entre flexibilidad (creatividad del diseñador) y consistencia (coherencia del sistema)

**Insight clave:** Un buen design system no es rígido — tiene "zonas de flexibilidad" documentadas. El problema no es tener excepciones; el problema es que las excepciones no están documentadas.

---

### Tema 2 — Decisiones Visuales Prácticas (Refactoring UI)

**VIDEO-315-03**
**Título:** "Designing Without a Mockup" — Adam Wathan & Steve Schoger
**URL:** https://www.youtube.com/watch?v=3C_22eBWpjg
**Duración:** ~60 minutos
**Nivel:** Intermedio

**Contenido destilado:**
- El proceso de Adam Wathan tomando un diseño "feo" y aplicando principios de Refactoring UI en tiempo real
- Cómo la jerarquía visual se construye con espacio, tamaño y peso (no color)
- El squint test en acción: cerrar los ojos y ver qué elementos siguen visibles
- El error de usar demasiados bordes y separadores cuando el espacio puede hacer el mismo trabajo
- Cómo los colores de texto deben variar (no todos el mismo negro) para indicar jerarquía de información

**Insight clave:** En el 80% de los casos de "este diseño se ve mal", el problema es jerarquía visual, no color ni tipografía. Arreglar la jerarquía primero.

---

**VIDEO-315-04**
**Título:** "Every Layout - CSS Layout Patterns" — Heydon Pickering & Andy Bell
**URL:** https://every-layout.dev (más recurso que video, pero tiene demos interactivas)
**Duración:** Referencia continua
**Nivel:** Intermedio

**Contenido destilado:**
- Layouts CSS que funcionan en cualquier tamaño de pantalla sin media queries
- El Stack: separación vertical entre elementos (el patrón más útil del diseño)
- El Sidebar: layout de dos columnas que "colapsa" en móvil de forma automática
- El Cluster: elementos inline que se envuelven naturalmente
- El Center: centrado máximo con ancho controlado

**Insight clave:** Los mejores layouts de UI se describen por su comportamiento intrínseco, no por sus breakpoints. "Wrap cuando no quepas" es mejor que "a 768px, cambia a una columna".

---

### Tema 3 — Process & Workflow de UI Design

**VIDEO-315-05**
**Título:** "A Designer's Process" — Femke van Schoonhoven
**URL:** https://www.youtube.com/c/femkedesign
**Duración:** Series (10-20 min por video)
**Nivel:** Principiante-Intermedio

**Contenido destilado:**
- Cómo Femke va de brief → wireframes → diseño visual en Figma
- El proceso de exploración antes de comprometerse con una dirección visual
- Cómo documentar decisiones de diseño para que el equipo entienda el "por qué"
- Preparar archivos de Figma para handoff a developers (nomenclatura, auto-layout, componentes)
- Recibir feedback de stakeholders y cómo incorporarlo sin perder la visión del diseño

**Insight clave:** El proceso de diseño UI que funciona tiene 3 fases distintas: explorar muchas opciones (divergir), elegir una dirección (converger), refinar en detalle (ejecutar). Saltarse la fase de exploración produce diseños seguros pero mediocres.

---

**VIDEO-315-06**
**Título:** "Design Systems at Scale" — Figma Config 2024
**URL:** https://www.figma.com/community/video/config-2024
**Duración:** ~40 minutos
**Nivel:** Avanzado

**Contenido destilado:**
- Cómo empresas como Spotify, Airbnb y Linear gestionan design systems con múltiples equipos
- La gobernanza del design system: quién puede contribuir, quién aprueba cambios
- Variables y tokens en Figma 4.0 para multi-theme en tiempo real
- El "design system score": cómo medir la adopción del sistema en el equipo
- Sincronización entre el design system en Figma y el código en GitHub

**Insight clave:** Un design system sin gobernanza definida deteriora en 6 meses. La pregunta crítica es: "¿Quién tiene autoridad para agregar un componente nuevo?"

---

### Tema 4 — Accesibilidad en Video

**VIDEO-315-07**
**Título:** "Web Accessibility Perspectives" — W3C WAI
**URL:** https://www.w3.org/WAI/perspective-videos/
**Duración:** ~1 minuto por video (serie de 10)
**Nivel:** Principiante

**Contenido destilado:**
- 10 videos de 1 minuto cada uno que muestran cómo diferentes usuarios interactúan con la web
- Keyboard navigation: un usuario que no puede usar mouse
- Texto alternativo: un usuario ciego usando lector de pantalla en un e-commerce
- Contraste: una persona mayor con baja visión leyendo noticias
- Captions: un usuario sordo viendo un tutorial en video

**Insight clave para el Cerebro #3:** Ver a usuarios reales interactuar con interfaces inaccessibles es más persuasivo que cualquier argumento teórico. Este es el video para mostrar cuando alguien dice "la accesibilidad no es prioridad".

---

### Tema 5 — Color y Dark Mode

**VIDEO-315-08**
**Título:** "Designing for Dark Mode" — Material Design YouTube
**URL:** https://www.youtube.com/watch?v=C_rCETRdmns
**Duración:** ~15 minutos
**Nivel:** Intermedio

**Contenido destilado:**
- Por qué #000000 no es el fondo correcto para dark mode (smearing en OLED)
- La elevación con overlays en lugar de sombras
- Cómo las superficies claras comunican "más cerca" en dark mode
- La saturación de colores en fondos oscuros (reducirla, no aumentarla)
- Demo en vivo del Material Theme Builder generando paleta dual automáticamente

**Insight clave:** El dark mode no es un "modo oscuro" — es un sistema de color alternativo completo. El objetivo no es que se vea oscuro, sino que sea cómodo de leer en condiciones de baja luz.

---

## Índice Rápido — Video por Situación

| Situación | Video Recomendado |
|-----------|-------------------|
| Estoy iniciando un design system | VIDEO-315-01 (Brad Frost) |
| Mi diseño "se ve mal" y no sé por qué | VIDEO-315-03 (Refactoring UI) |
| Necesito hacer el handoff a frontend | VIDEO-315-05 (Femke - process) |
| Me piden implementar dark mode | VIDEO-315-08 (Material Design) |
| Necesito convencer a alguien de accesibilidad | VIDEO-315-07 (W3C WAI) |
| El design system tiene conflictos de gobernanza | VIDEO-315-06 (Figma Config Scale) |
| El layout no se adapta bien en móvil | VIDEO-315-04 (Every Layout) |

---

## Conexión con el Cerebro #3

| Video | Refuerza la fuente |
|-------|-------------------|
| VIDEO-315-01, 02, 06 | FUENTE-301 (Atomic Design), FUENTE-307 (Tokens) |
| VIDEO-315-03, 04 | FUENTE-302 (Refactoring UI), FUENTE-305 (Grid) |
| VIDEO-315-05 | Proceso general del Cerebro #3 |
| VIDEO-315-07 | FUENTE-309 (Accesibilidad) |
| VIDEO-315-08 | FUENTE-311 (Dark Mode), FUENTE-307 (Tokens) |
