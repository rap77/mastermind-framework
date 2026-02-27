---
source_id: "FUENTE-316"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Anti-Patrones Consolidados v2.0 & Radar de Calidad Actualizado — Cerebro #3"
author: "Auto-generado | MasterMind Framework"
expert_id: "N/A"
type: "radar-interno"
language: "es"
year: 2026
skills_covered: ["H1", "H2", "H3", "H4", "H5"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "2.0.0"
last_updated: "2026-02-26"
changelog:
  - version: "2.0.0"
    date: "2026-02-26"
    changes:
      - "Ficha creada con 52 anti-patrones (vs 20 en v1)"
      - "Agrega 6 categorías nuevas: Accesibilidad, Motion, Dark Mode, Data Viz, Iconografía, Color"
      - "Formato adaptado a estándar del MasterMind Framework"
      - "Reemplaza completamente a FUENTE-308"
status: "active"
replaces: "FUENTE-308"

# Metadatos específicos del Cerebro #3
generado_de: ["FUENTE-301", "FUENTE-302", "FUENTE-303", "FUENTE-304", "FUENTE-305", "FUENTE-306", "FUENTE-307", "FUENTE-309", "FUENTE-310", "FUENTE-311", "FUENTE-312", "FUENTE-313", "FUENTE-314", "FUENTE-315"]
capa: 3
capa_nombre: "Radar — Auto-generado v2.0"
relevancia: "CRÍTICA — Reemplaza FUENTE-308. Incorpora todos los anti-patrones de las 15 fuentes del cerebro"
---

# FUENTE-316 — Anti-Patrones Consolidados v2.0 & Radar de Calidad
## Cerebro #3 — UI Design | Sistema de Auto-Evaluación Completo

---

## Propósito

Esta ficha reemplaza y supera a FUENTE-308. Es el mecanismo de auto-evaluación del Cerebro #3 con todos los anti-patrones incorporados de las 15 fuentes maestras. Antes de cualquier handoff al Cerebro #4 (Frontend), ejecutar este radar completo.

**Total de anti-patrones: 52**
- 🔴 CRÍTICOS (bloquean el handoff): **12**
- 🟠 ALTOS (requieren revisión): **24**
- 🟡 MEDIOS (reducen calidad): **16**

---

## 🔴 ANTI-PATRONES CRÍTICOS — Bloquean el handoff

### SISTEMA & TOKENS (de FUENTE-301, 307)

**AC-01 — Sin design system / sin componentes definidos**
Diseño de pantallas sin definir los componentes reutilizables. Frontend improvisa; resultado inconsistente.
*Corrección: Definir mínimo átomos y moléculas antes de entregar.*

**AC-02 — Valores visuales hardcodeados sin tokens**
Colores hex directos (#1976D2) sin mapeo a tokens semánticos. El sistema muere en el primer cambio de color.
*Corrección: Todo valor de color, espaciado y tipografía debe referenciar un token.*

**AC-03 — Sin estados de componentes (solo happy path)**
Componentes sin estados: loading, error, empty, disabled. El developer los inventa; el resultado es incoherente.
*Corrección: 5 estados mínimos por componente interactivo.*

### ACCESIBILIDAD (de FUENTE-309)

**AC-04 — Contraste de texto que falla WCAG AA**
Texto con ratio < 4.5:1 (normal) o < 3:1 (grande). El producto excluye usuarios con baja visión.
*Corrección: Verificar contraste de TODOS los textos, incluyendo placeholders y texto deshabilitado.*

**AC-05 — outline:none sin sustituto de foco**
CSS que elimina el foco sin reemplazarlo. Bloquea completamente a usuarios de teclado.
*Corrección: Diseñar estado :focus para CADA elemento interactivo.*

**AC-06 — Inputs sin labels (solo placeholder)**
El placeholder desaparece al escribir. El usuario pierde la referencia. Nunca reemplaza al label.
*Corrección: Cada campo con label visible, asociado via for/id.*

**AC-07 — Información transmitida solo por color**
Estados de error, éxito, warning sin ícono ni texto. El 8% de usuarios con daltonismo no recibe la información.
*Corrección: Color + ícono + texto para cada estado.*

### DARK MODE (de FUENTE-311)

**AC-08 — Dark mode implementado sin sistema de tokens**
El dark mode se "improvisa" sin tokens duales. Resultado: inconsistencia masiva entre componentes.
*Corrección: Si el producto soporta dark mode, los tokens deben tener valor para cada tema ANTES del handoff.*

### FORMULARIOS (de FUENTE-306)

**AC-09 — Formularios sin validación inline**
La validación solo ocurre en submit. El usuario completa todo y descubre errores al final.
*Corrección: Diseñar validación campo a campo, activada on-blur.*

### DATA VISUALIZATION (de FUENTE-312)

**AC-10 — Eje Y truncado en gráficas de barras**
Exagera diferencias. Distorsiona la lectura de datos. Comunica algo falso.
*Corrección: El eje Y siempre empieza en cero para gráficas de barras.*

**AC-11 — Gráfica sin pregunta definida**
La visualización intenta responder 3 preguntas a la vez y no responde ninguna bien.
*Corrección: Cada gráfica responde exactamente una pregunta, especificada en su título.*

### COLOR (de FUENTE-314)

**AC-12 — Mismo color para estado de error y para acción primaria**
El usuario aprende a ignorar el rojo o siente ansiedad al ver el CTA.
*Corrección: Los colores de estado (error, éxito, warning) nunca coinciden con el color primario.*

---

## 🟠 ANTI-PATRONES ALTOS — Reducen calidad significativamente

### LAYOUT & COMPOSICIÓN (de FUENTE-302, 305)

**AA-01 — Layout sin grid definido**
Posicionamiento sin sistema de columnas. Frontend no puede implementar limpiamente.

**AA-02 — Jerarquía visual plana o confusa**
Squint test falla: no hay elemento claramente más importante. Usuario no sabe qué hacer.

**AA-10 — Sin especificación de espaciado**
Sin valores de padding/margin del sistema. Developer improvisa; resultado inconsistente.

### TIPOGRAFÍA (de FUENTE-304)

**AA-03 — Más de 3 familias tipográficas**
Incoherencia visual, mayor tiempo de carga, personalidad de marca fragmentada.

**AA-09 — Text justificado en contenido digital**
Crea "rivers" de espacio, reduce legibilidad, especialmente en móvil.

**AA-17 — Escala tipográfica con tamaños arbitrarios**
Textos de 13px, 17px, 22px sin relación de escala. Jerarquía visual incoherente.

### MOBILE (de FUENTE-303)

**AA-04 — Diseño sin versión móvil**
Solo existe desktop. El 60%+ de usuarios móviles recibe experiencia degradada.

**AA-05 — Touch targets menores a 44px**
Errores de tap frecuentes. Especialmente problemático para usuarios con motricidad reducida.

### FORMULARIOS (de FUENTE-306)

**AA-06 — Labels solo en placeholder**
(También crítico en contexto de accesibilidad; aquí como alto en contexto de UX general)
Cuando el usuario empieza a escribir, pierde la referencia del campo.

**AA-07 — Mensajes de error genéricos**
"Campo inválido" no enseña al usuario cómo corregir. Abandono de formulario.

### COLOR (de FUENTE-302, 307, 314)

**AA-08 — Más de 5 colores distintos en una pantalla**
Sin sistema; cada sección tiene un color diferente. Sensación de producto sin criterio.

**AA-18 — Color primario de marca como fondo principal**
El color de acción pierde poder cuando ocupa el 60% de la interfaz.

**AA-19 — Grises sin tonalizar (gris puro con color saturado)**
Los neutrales de gris puro se ven "plásticos" junto a primarios de color. Falta de cohesión.

### MOTION (de FUENTE-310)

**AA-20 — Animaciones sin especificación de easing**
El developer usa `linear` por default. Las transiciones se sienten robóticas.

**AA-21 — Micro-interacciones con duración > 500ms**
El usuario siente que la UI es lenta. Cada ms de espera innecesaria es frustración.

**AA-22 — Sin especificación de prefers-reduced-motion**
El frontend no sabe qué hacer con usuarios que tienen sensibilidad al movimiento.

### ICONOGRAFÍA (de FUENTE-313)

**AA-23 — Mezcla de sistemas de íconos**
Feather + Material + custom sin reglas. Cada sistema tiene diferente peso visual y grid.

**AA-24 — Íconos sin area táctil de 44px**
El ícono visual puede ser 24px pero el hitbox debe ser 44x44px en móvil.

---

## 🟡 ANTI-PATRONES MEDIOS — Reducen calidad pero no bloquean

### SISTEMA & COMPONENTES

**AM-01 — Nomenclatura de componentes inconsistente**
Mismo componente con nombres diferentes en distintas pantallas. Confusión en handoff.

**AM-02 — Íconos sin semántica de color**
Ícono azul "porque se ve bien", no porque comunique algo. El color debe tener función.

### TIPOGRAFÍA

**AM-03 — Body text menor a 16px**
Legibilidad reducida, especialmente en móvil y en usuarios mayores.

**AM-04 — Line-height del body fuera de 1.4-1.75**
Menor a 1.4: texto muy comprimido. Mayor a 1.75: las líneas se separan demasiado.

### DARK MODE

**AM-05 — Dark mode no considerado**
Si el producto lo necesita, el trabajo de adaptación posterior será mayor e inconsistente.

**AM-06 — Fondo de dark mode en negro puro (#000000)**
Causa smearing en pantallas OLED. El fondo correcto es ~#121212.

**AM-07 — Imágenes sin tratamiento en dark mode**
Las fotos brillantes se ven fuera de contexto en fondo oscuro.

### DATA VISUALIZATION

**AM-08 — Pie chart con más de 5 categorías**
El ojo humano no puede comparar ángulos con precisión. Usar barras horizontales.

**AM-09 — Gráficas 3D**
Las perspectivas 3D distorsionan proporciones. Siempre usar 2D.

**AM-10 — Títulos que describen en vez de concluir**
"Ventas por mes" vs. "Las ventas crecieron 23% en Q4". El primero no aporta contexto.

**AM-11 — KPIs sin variación comparativa**
Números sin referencia temporal o de benchmark son contexto-less.

### MOTION

**AM-12 — Animación decorativa sin función**
Movimiento que no orienta, da feedback, crea continuidad ni narra. Es ruido.

**AM-13 — Stagger demasiado largo (> 500ms total)**
El usuario percibe que la página "carga lento" aunque los datos estén disponibles.

**AM-14 — Animaciones en loop sin control de pausa**
Viola WCAG 2.2.2 y es molesta para todos los usuarios.

### ICONOGRAFÍA

**AM-15 — Íconos ambiguos sin label de texto**
Un ícono custom o poco estándar sin label fuerza al usuario a adivinar su función.

**AM-16 — Tamaño de renderizado de ícono sin versión simplificada**
A 16px, los íconos con muchos detalles finos se vuelven ilegibles.

---

## Checklist de Calidad — Pre-Entrega al Cerebro #4 (Versión Completa v2.0)

```
SISTEMA Y TOKENS
☐ ¿Paleta de colores con tokens semánticos y primitivos separados?
☐ ¿Tokens tienen valor para light mode Y dark mode (si aplica)?
☐ ¿Escala de espaciado definida (múltiplos de 4 u 8px)?
☐ ¿Escala tipográfica con ratio matemático?
☐ ¿Los componentes referencian tokens, nunca valores directos?

COMPONENTES
☐ ¿Componentes principales identificados y nombrados consistentemente?
☐ ¿Cada componente interactivo tiene sus 5+ estados?
☐ ¿Hay empty states para listas y secciones de contenido?
☐ ¿Componentes alineados a Atomic Design (átomo/molécula/organismo)?
☐ ¿Se especificó el elemento semántico HTML de cada componente?

LAYOUT Y GRID
☐ ¿Grid definido para cada breakpoint relevante?
☐ ¿Layouts siguen el sistema de columnas?
☐ ¿El espaciado usa la escala definida?

TIPOGRAFÍA
☐ ¿Máximo 2 familias tipográficas?
☐ ¿Body text ≥ 16px?
☐ ¿Line-height del body entre 1.4 y 1.75?
☐ ¿Contraste de todos los textos pasa WCAG AA (4.5:1)?
☐ ¿Incluye placeholders y texto deshabilitado en la verificación?

MOBILE & RESPONSIVE
☐ ¿Existe diseño para al menos 2 breakpoints?
☐ ¿Touch targets ≥ 44x44px?
☐ ¿La navegación es accesible con el pulgar?

FORMULARIOS (si aplica)
☐ ¿Todos los campos tienen label visible?
☐ ¿Hay estados de error con mensajes específicos y accionables?
☐ ¿Validación inline diseñada (no solo on-submit)?
☐ ¿Los inputs usan el tipo correcto para cada dato?

ACCESIBILIDAD
☐ ¿Estado :focus diseñado para CADA elemento interactivo?
☐ ¿El diseño no depende SOLO del color para comunicar estado?
☐ ¿Los elementos interactivos tienen nombre accesible especificado?
☐ ¿Se especificó semántica HTML / ARIA roles para componentes complejos?

MOTION Y ANIMACIONES (si aplica)
☐ ¿Cada animación tiene propósito funcional definido?
☐ ¿Duraciones y easing especificados?
☐ ¿Versión de prefers-reduced-motion especificada?
☐ ¿Las animaciones en loop tienen control de pausa?

DARK MODE (si aplica)
☐ ¿Todos los tokens tienen valor para dark mode?
☐ ¿El fondo dark es ~#121212 (no negro puro)?
☐ ¿Los colores de marca tienen versión dark con saturación reducida?
☐ ¿Las imágenes tienen tratamiento para dark mode?

DATA VISUALIZATION (si aplica)
☐ ¿Cada gráfica responde una sola pregunta?
☐ ¿El tipo de gráfica corresponde al tipo de dato?
☐ ¿El eje Y de barras empieza en cero?
☐ ¿La paleta de datos es distinguible para daltonismo (patrón + color)?
☐ ¿Los títulos de gráficas concluyen, no solo describen?

ICONOGRAFÍA (si aplica)
☐ ¿Se usa un solo sistema de íconos?
☐ ¿Los íconos custom siguen las mismas reglas del sistema base?
☐ ¿Los íconos de función tienen aria-label especificado?
☐ ¿Los íconos decorativos tienen aria-hidden especificado?

ESPECIFICACIÓN PARA HANDOFF
☐ ¿Los componentes tienen nombres que el developer entiende?
☐ ¿Están especificados breakpoints y comportamiento responsive?
☐ ¿Las animaciones tienen especificación técnica completa?
☐ ¿Los íconos tienen sistema, tamaño, área táctil y aria especificados?
☐ ¿Los colores de datos tienen paleta dual (light/dark)?
```

---

## Score de Evaluación del Output v2.0

| Categoría | Peso | Criterio de Aprobación |
|-----------|------|------------------------|
| Sistema de tokens completo (dual si hay dark mode) | 20% | Tokens definidos para todos los roles, light y dark |
| Estados de componentes completos | 15% | Mínimo 5 estados por componente interactivo |
| Accesibilidad: contraste + foco + no solo color | 20% | 100% textos verificados, foco diseñado, estados con ícono+texto |
| Diseño mobile presente | 10% | Al menos 2 breakpoints |
| Especificación de handoff completa | 10% | Nomenclatura, HTML semántico, aria, animaciones |
| Tipografía con sistema | 5% | Escala + máx 2 familias + contraste |
| Grid definido | 5% | Sistema de columnas por breakpoint |
| Motion especificado (si aplica) | 5% | Duración + easing + reduced-motion |
| Data viz correcta (si aplica) | 5% | Tipo correcto + eje Y + 1 pregunta por gráfica |
| Iconografía coherente (si aplica) | 5% | Un sistema + aria correcto |

**APROBACIÓN:**
- Score > 80%: **APPROVE** — Pasa a Cerebro #4
- Score 60-80%: **CONDITIONAL** — Pasa con notas de corrección documentadas
- Score < 60%: **REJECT** — Requiere revisión antes de continuar

---

## Preguntas de Auto-Evaluación del Cerebro #3 (v2.0)

1. ¿El Frontend puede implementar esto sin tomar decisiones de diseño por su cuenta?
2. ¿Si el color primario cambia mañana, cuántos archivos hay que modificar? (respuesta correcta: 1)
3. ¿Qué pasa cuando no hay datos? ¿Error? ¿Carga? ¿Lo diseñé?
4. ¿Un usuario con baja visión puede usar este diseño?
5. ¿Un usuario zurdo en el metro con teléfono de 5.5" puede completar la tarea principal?
6. ¿Un usuario de teclado puede navegar toda la interfaz?
7. ¿Las animaciones tienen propósito o son decoración?
8. ¿Las gráficas responden una pregunta cada una?
9. ¿Los íconos son coherentes entre sí?
10. ¿Este diseño es coherente con los outputs del Cerebro #2 (UX) y #1 (Strategy)?

---

## Conexión con otros Cerebros

| Cerebro | Relación |
|---------|----------|
| Cerebro #2 (UX Research) | INPUT: wireframes, journey maps, arquitectura. El #3 los convierte en interfaz visual. Conflicto → escalar al humano. |
| Cerebro #4 (Frontend) | OUTPUT: componentes con estados, tokens, grid, motion, íconos, accesibilidad especificada. El #4 implementa exactamente lo que el #3 entrega. |
| Cerebro #7 (Growth & Data) | EVALUADOR: mide si el diseño produce los resultados esperados. Si no, retroalimenta al #3. |

---

## Registro de Precedentes del Cerebro #3

*(Se actualiza con cada conflicto resuelto)*

```yaml
precedents: []
# Formato:
# - id: "PREC-3XX"
#   date: "YYYY-MM-DD"
#   conflict_between: ["brain-03-ui-design", "brain-04-frontend"]
#   issue: "descripción del conflicto"
#   resolution: "qué se decidió"
#   rule_created: "regla que aplica a futuras situaciones"
#   applies_to: ["brain-03-ui-design", "brain-04-frontend"]
```
