---
source_id: "FUENTE-313"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Icon Systems Design — Guía Consolidada"
author: "Compilación: Material Symbols (Google) + Apple SF Symbols + Smashing Magazine"
expert_id: "EXP-313"
type: "guide"
language: "es"
year: 2024
url: "https://fonts.google.com/icons"
skills_covered: ["H3", "H5"]
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
      - "Cubre gap de Iconografía identificado en v1.0"
status: "active"

# Metadatos específicos del Cerebro #3
habilidad_primaria: "Sistemas de Íconos & Iconografía para UI"
habilidad_secundaria: "Coherencia de Íconos & Accesibilidad Visual"
capa: 2
capa_nombre: "Frameworks Operativos — Iconografía"
relevancia: "MEDIA-ALTA — Los íconos sin sistema producen inconsistencia visual inmediata"
---

# FUENTE-313 — Icon Systems Design
## Guía Consolidada | Material Symbols + Apple SF Symbols + Best Practices

---

## Tesis Central

> Los íconos no son decoración. Son vocabulario visual. Como cualquier vocabulario, debe ser coherente: mismas reglas, mismo estilo, mismo peso visual. Un sistema de íconos bien diseñado es invisible — el usuario simplemente "entiende". Un sistema roto hace que el usuario se detenga a descifrar.

La primera decisión de íconos no es qué ícono usar, sino **qué sistema de íconos usar**. El sistema determina las reglas; los íconos son consecuencia.

---

## Principios Fundamentales

### Principio 1 — Un Solo Sistema por Producto

El error más común: mezclar íconos de Feather con íconos de Material con íconos propios. Cada uno tiene su propio grid, grosor de trazo, radio de esquina. El resultado es incoherencia visual percibida como "poco profesional".

**Regla:** Elegir un sistema y mantenerlo consistentemente. Si se necesitan íconos custom, crearlos siguiendo las mismas reglas del sistema elegido.

### Principio 2 — El Grid Define Todo

Los íconos profesionales se diseñan en un grid específico que garantiza consistencia óptica.

```
GRID ESTÁNDAR PARA ÍCONOS:
  Canvas: 24x24px (el más común) o 20x20px
  Área segura (safe area): 20x20px dentro del canvas
  Zona de sangrado (bleed): 2px por lado (elementos que pueden tocar el borde)
  Pixel grid: los trazos se alinean a píxeles completos (no medios píxeles)

PESOS DE TRAZO (stroke width):
  Regular: 1.5-2px (para 24px canvas)
  Bold: 2-3px
  Light: 1-1.5px
  → Consistente en TODOS los íconos del sistema
```

### Principio 3 — Coherencia Óptica vs Coherencia Matemática

Dos cuadrados del mismo tamaño numérico no se ven del mismo tamaño que dos círculos del mismo tamaño numérico. El círculo parece más pequeño.

**Corrección óptica en íconos:**
- Los círculos deben ser ligeramente más grandes que los cuadrados de la "misma talla"
- Los triángulos necesitan ser aún más grandes
- Las formas irregulares se ajustan visualmente, no matemáticamente

### Principio 4 — Metáforas Universales y Metáforas Culturales

Algunos íconos son universales (lupa = buscar, casa = home). Otros son culturales o contextuales.

**Íconos universalmente reconocidos:**
- 🔍 Lupa → Buscar
- 🏠 Casa → Inicio / Home
- ✉️ Sobre → Email / Mensajes
- ⚙️ Engranaje → Configuración
- ☰ Hamburger → Menú
- ✕ X → Cerrar

**Íconos problemáticos (ambiguos):**
- 💾 Diskette → Guardar (generación Z puede no reconocerlo)
- 🔔 Campana → Notificaciones (o alertas, o silencio)
- ♥ Corazón → Like, favorito, o salud
- 📌 Pin → Fijar, guardar, ubicación

**Regla:** Si el ícono es ambiguo, siempre acompañarlo de un label de texto, al menos en el primer uso.

### Principio 5 — Tamaño Mínimo y Área Táctil

```
TAMAÑOS DE RENDERIZADO COMUNES:
  16px → Íconos en texto, badges, muy pequeños
  20px → Íconos en UI densa (tablas, listas compactas)
  24px → Tamaño estándar (el más común en UI)
  32px → Íconos medianos, navegación secundaria
  40-48px → Íconos de acciones primarias en móvil

ÁREA TÁCTIL (diferente del tamaño visual):
  El área táctil del ícono debe ser siempre mínimo 44x44px
  El ícono visual puede ser 24px pero el hitbox debe ser 44x44px
  → En Figma: el frame del componente es 44x44, el ícono dentro es 24x24
```

---

## Framework — Sistema de Íconos del Cerebro #3

### Paso 1: Elegir el Sistema Base

| Sistema | Estilo | Plataforma | Cuándo usar |
|---------|--------|------------|-------------|
| Material Symbols (Google) | Outlined, Filled, Rounded, Sharp, Two-tone | Web, Android | Productos con Material Design o web generales |
| SF Symbols (Apple) | Variantes de peso | iOS, macOS | Exclusivo Apple ecosystem |
| Heroicons (Tailwind) | Outline, Solid | Web | Proyectos con Tailwind CSS |
| Feather Icons | Outline | Web | Productos minimalistas, fintech |
| Lucide | Outline | Web | Fork de Feather, más íconos |
| Phosphor Icons | 6 pesos | Web, React Native | Proyectos que necesitan mucha variedad |

**Criterios de selección:**
- ¿El producto ya usa un design system? → Usar los íconos de ese sistema
- ¿Es web sin sistema? → Material Symbols o Heroicons
- ¿Es iOS? → SF Symbols
- ¿Necesita íconos muy custom? → Sistema base + extensión custom

### Paso 2: Definir los Tokens de Íconos

```yaml
icon-system:
  grid: 24px
  style: "outlined"  # o filled, rounded, etc.
  stroke-width: 1.5px
  corner-radius: 2px

  sizes:
    sm: 16px
    md: 20px
    base: 24px
    lg: 32px
    xl: 48px

  colors:
    default: color.on-surface
    muted: color.on-surface-variant
    primary: color.primary
    error: color.error
    success: color.success
    inverse: color.on-primary  # sobre fondos de color
```

### Paso 3: Catálogo de Íconos Requeridos (Mínimo Viable)

```
NAVEGACIÓN
☐ Home / Inicio
☐ Back / Atrás
☐ Close / Cerrar (X)
☐ Menu / Hamburger (o equivalente)
☐ More options / Tres puntos

ACCIONES PRIMARIAS
☐ Search / Buscar
☐ Add / Agregar (+)
☐ Edit / Editar
☐ Delete / Eliminar
☐ Save / Guardar
☐ Share / Compartir
☐ Download / Descargar
☐ Upload / Subir

ESTADOS Y FEEDBACK
☐ Success / Check ✓
☐ Error / X o !
☐ Warning / ⚠
☐ Info / i
☐ Loading / Spinner (animado)
☐ Empty state / Ilustración o ícono específico

CONTENIDO
☐ User / Perfil
☐ Notifications / Campana
☐ Settings / Engranaje
☐ Filter / Embudo
☐ Sort / Ordenar
☐ Visible / Eye
☐ Hidden / Eye-off
```

### Paso 4: Íconos Custom — Cuándo y Cómo

**Cuándo crear íconos custom:**
- El sistema base no tiene el ícono necesario
- El concepto es muy específico del dominio del producto
- Hay un ícono de marca registrada del producto

**Cómo crearlos (respetando el sistema):**
1. Usar el mismo canvas (24x24px)
2. Usar el mismo grosor de trazo (1.5px)
3. Usar el mismo radio de esquina
4. Diseñar en el mismo estilo (outlined, filled, etc.)
5. Verificar que se vea coherente junto a íconos del sistema base

---

## Especificación de Handoff para Íconos

En el handoff al Cerebro #4 (Frontend), especificar para cada ícono:

```
ÍCONO: [nombre en el sistema, ej: "search"]
SISTEMA: Material Symbols
TAMAÑO VISUAL: 24px
ÁREA TÁCTIL: 44x44px (si es interactivo)
COLOR TOKEN: color.on-surface
ARIA-LABEL: "Buscar" (si es el único contenido del botón)
ARIA-HIDDEN: true (si hay texto visible que lo describe)
```

---

## Anti-Patrones de Sistemas de Íconos

**ASI-01 — Mezcla de sistemas (Feather + Material + custom sin reglas)**
Cada sistema tiene su propio peso visual y grid. Mezclarlos produce incoherencia inmediata.

**ASI-02 — Íconos sin label en funciones no estándar**
Un ícono de "lupa" puede aceptarse sin label. Un ícono de "filtro de inteligencia artificial" no puede.

**ASI-03 — Todos los íconos a 16px**
A 16px, los detalles finos desaparecen. Los íconos deben tener una versión simplificada para tamaños pequeños.

**ASI-04 — Área táctil = tamaño del ícono**
Un ícono de 24px con área táctil de 24px produce errores de tap constantes en móvil.

**ASI-05 — Íconos de color sin semántica**
Si un ícono es azul solo porque "se ve bien", no comunica nada. Si es azul porque "es una acción primaria", sí.

**ASI-06 — Sin estado hover/active para íconos interactivos**
Un ícono sin estado hover se siente no interactivo. El usuario duda si es clickeable.

---

## Conexión con el Cerebro #3

| Habilidad del Cerebro #3 | Aporte de esta fuente |
|--------------------------|----------------------|
| Coherencia visual del sistema | Un solo sistema de íconos con reglas claras |
| Handoff a Frontend (#4) | Especificación de nombre, tamaño, área táctil, color, aria |
| Accesibilidad | Reglas de aria-label vs aria-hidden por contexto |
| Design Tokens | Tokens de tamaño y color de íconos integrados al sistema |

## Preguntas que el Cerebro #3 puede responder con esta fuente

1. ¿Qué sistema de íconos es el correcto para este producto?
2. ¿Este ícono necesita label de texto o es suficientemente reconocible?
3. ¿Cuál es el área táctil correcta para este ícono en móvil?
4. ¿Cómo especifico este ícono para que el frontend lo implemente correctamente?
5. ¿Este ícono custom sigue las mismas reglas que el sistema base?
6. ¿Qué aria-label necesita este ícono?
