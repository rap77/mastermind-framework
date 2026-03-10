---
source_id: "FUENTE-308"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Anti-Patrones y Radar de Calidad — Cerebro #3 UI Design"
author: "Auto-generado | MasterMind Framework"
expert_id: "N/A"
type: "radar-interno"
language: "es"
year: 2026
skills_covered: ["H1", "H2", "H3", "H4", "H5"]
distillation_date: "2026-02-26"
distillation_quality: "complete"
loaded_in_notebook: true
version: "1.0.1"
last_updated: "2026-02-26"
changelog:
  - version: "1.0.1"
    date: "2026-02-26"
    changes:
      - "Marcado como DEPRECATED - reemplazado por FUENTE-316"
      - "Formato adaptado a estándar del MasterMind Framework"
  - version: "1.0.0"
    date: "2026-02-25"
    changes:
      - "Ficha creada con 20 anti-patrones"
status: "deprecated"
replaced_by: "FUENTE-316"

# Metadatos específicos del Cerebro #3
generado_de: ["FUENTE-301", "FUENTE-302", "FUENTE-303", "FUENTE-304", "FUENTE-305", "FUENTE-306", "FUENTE-307"]
capa: 3
capa_nombre: "Radar — Auto-generado (DEPRECATED)"
relevancia: "CRÍTICA — Mecanismo de auto-evaluación. REEMPLAZADO POR FUENTE-316"
---

# FUENTE-308 — Anti-Patrones y Radar de Calidad
## Cerebro #3 — UI Design | Sistema de Auto-Evaluación

---

## Propósito

Esta ficha es el mecanismo de evaluación interna del Cerebro #3. Antes de entregar cualquier output al Cerebro #4 (Frontend Architecture) o al Cerebro #7 (Growth & Data), el Cerebro #3 verifica sus decisiones contra este radar.

---

## Catálogo Consolidado de Anti-Patrones del Cerebro #3

### 🔴 CRÍTICOS — Bloquean el handoff; el output no puede avanzar

**AC-01 — Sin design system / sin componentes definidos**
Fuente: FUENTE-301 (Atomic Design)
Síntoma: Diseño de pantallas sin definir los componentes reutilizables que las componen.
Impacto: Frontend (#4) improvisa los componentes; resultado inconsistente e inimplementable.
Corrección requerida: Definir mínimo los átomos y moléculas clave antes de entregar.

**AC-02 — Valores visuales hardcodeados sin sistema de tokens**
Fuente: FUENTE-307 (Design Tokens)
Síntoma: Diseño con colores hex específicos (#1976D2) sin mapeo a tokens semánticos.
Impacto: El design system muere en el primer cambio de color; el handoff produce código frágil.
Corrección requerida: Definir tokens mínimos (color, espaciado, tipografía) antes de entregar.

**AC-03 — Sin estados de componentes (solo happy path)**
Fuente: FUENTE-301, FUENTE-306
Síntoma: Componentes diseñados solo en estado default; sin loading, error, empty, disabled.
Impacto: El developer inventa los estados; el resultado es visualmente inconsistente.
Corrección requerida: Para cada componente interactivo, entregar los 5 estados básicos.

**AC-04 — Contraste de texto que falla WCAG AA**
Fuente: FUENTE-302, FUENTE-304
Síntoma: Texto con ratio de contraste menor a 4.5:1 (normal) o 3:1 (grande).
Impacto: El producto es inaccesible para usuarios con baja visión; riesgo legal en algunos mercados.
Corrección requerida: Verificar contraste de TODOS los textos antes de entregar.

---

### 🟠 ALTOS — Reducen calidad significativamente; requieren revisión

**AA-01 — Layout sin grid definido**
Fuente: FUENTE-305 (Grid Systems)
Síntoma: Posicionamiento de elementos sin referencia a un sistema de columnas.
Impacto: Frontend no puede implementar el layout limpiamente; resultado difiere del diseño.

**AA-02 — Jerarquía visual plana o confusa**
Fuente: FUENTE-302 (Refactoring UI)
Síntoma: Al hacer squint test, no hay un claro elemento de mayor importancia.
Impacto: El usuario no sabe qué hacer o mirar primero; métricas de conversión bajan.

**AA-03 — Más de 3 familias tipográficas**
Fuente: FUENTE-304 (Thinking with Type)
Síntoma: El diseño usa 4+ fuentes diferentes.
Impacto: Incoherencia visual, mayor tiempo de carga, personalidad de marca fragmentada.

**AA-04 — Diseño sin versión móvil**
Fuente: FUENTE-303 (Mobile First)
Síntoma: Solo existe el diseño desktop; el móvil "se ve después".
Impacto: El 60%+ de usuarios móviles recibe una experiencia degradada.

**AA-05 — Touch targets menores a 44px**
Fuente: FUENTE-303 (Mobile First)
Síntoma: Botones, links o elementos interactivos con área táctil menor a 44x44px en móvil.
Impacto: Errores de tap frecuentes; especialmente problemático para usuarios con motricidad reducida.

**AA-06 — Formularios con labels solo en placeholder**
Fuente: FUENTE-306 (Web Form Design)
Síntoma: Los campos de formulario no tienen label visible; el hint está solo en el placeholder.
Impacto: Cuando el usuario escribe, pierde la referencia de qué está llenando.

**AA-07 — Mensajes de error genéricos**
Fuente: FUENTE-306 (Web Form Design)
Síntoma: "Campo inválido" o "Por favor revisa los campos".
Impacto: El usuario no sabe qué corregir; abandono de formulario.

**AA-08 — Más de 5 colores distintos en una pantalla**
Fuente: FUENTE-302 (Refactoring UI), FUENTE-307 (Material Design)
Síntoma: Colores que no siguen un sistema; cada sección tiene un color diferente.
Impacto: Incoherencia visual, falta de jerarquía clara, sensación de producto sin criterio.

**AA-09 — Text justificado en contenido digital**
Fuente: FUENTE-304 (Thinking with Type)
Síntoma: Párrafos con alineación justificada.
Impacto: "Rivers" de espacio, legibilidad reducida, peor en móvil.

**AA-10 — Diseño sin especificación de espaciado**
Fuente: FUENTE-302 (Refactoring UI), FUENTE-305 (Grid Systems)
Síntoma: El diseño no especifica padding, margins o gaps con valores del sistema.
Impacto: El developer improvisa el espaciado; resultado inconsistente.

---

### 🟡 MEDIOS — Reducen calidad pero no bloquean

**AM-01 — Nomenclatura de componentes inconsistente**
Fuente: FUENTE-301 (Atomic Design)
Síntoma: Mismos componentes llamados diferente en distintas pantallas.
Impacto: Confusión en handoff; el developer no sabe si son el mismo componente.

**AM-02 — Cursor de texto en elementos no textuales sin explicación**
Fuente: FUENTE-302 (Refactoring UI)
Síntoma: Elementos que parecen texto estático pero son interactivos (o viceversa).
Impacto: El usuario no detecta la interactividad; baja tasa de engagement.

**AM-03 — Escala tipográfica con tamaños arbitrarios**
Fuente: FUENTE-304 (Thinking with Type)
Síntoma: Textos de 13px, 17px, 22px sin relación entre sí.
Impacto: Jerarquía visual incoherente, difícil de mantener.

**AM-04 — Sombras idénticas para todos los elementos**
Fuente: FUENTE-302 (Refactoring UI)
Síntoma: La misma sombra en cards, modals, botones y dropdowns.
Impacto: Se pierde la semántica de elevación que las sombras comunican.

**AM-05 — Dark mode no considerado**
Fuente: FUENTE-307 (Design Tokens)
Síntoma: No hay mención de dark mode en el diseño.
Impacto: Si el producto lo necesita, el trabajo de implementación será mayor y más inconsistente.

**AM-06 — Sin especificación de animaciones y transiciones**
Síntoma: El diseño no especifica qué transición ocurre entre estados.
Impacto: El developer inventa las animaciones; pueden ser inconsistentes o incorrectas.

---

## Checklist de Calidad — Pre-Entrega al Cerebro #4

Antes de marcar como "completo" y entregar a Frontend Architecture, verificar:

```
SISTEMA Y TOKENS
☐ ¿Se definió una paleta de colores con tokens semánticos?
☐ ¿Hay escala de espaciado definida (múltiplos de 4 o 8px)?
☐ ¿Hay escala tipográfica con ratio?
☐ ¿Los componentes referencian tokens, no valores directos?

COMPONENTES
☐ ¿Se identificaron y nombraron los componentes principales?
☐ ¿Cada componente interactivo tiene sus 5 estados? (default, hover, active, disabled, error)
☐ ¿Hay empty states para listas y secciones de contenido?
☐ ¿Los componentes están alineados al Atomic Design (átomo/molécula/organismo)?

LAYOUT Y GRID
☐ ¿Se definió el grid para cada breakpoint relevante?
☐ ¿Los layouts siguen el sistema de columnas?
☐ ¿El espaciado usa la escala definida?

TIPOGRAFÍA
☐ ¿Se usan máximo 2 familias tipográficas?
☐ ¿El body text es mínimo 16px?
☐ ¿El line-height del body es entre 1.5 y 1.75?
☐ ¿Contraste de todos los textos pasa WCAG AA?

MÓVIL
☐ ¿Existe diseño para al menos 2 breakpoints?
☐ ¿Touch targets son mínimo 44x44px?
☐ ¿La navegación es accesible con el pulgar?

FORMULARIOS (si aplica)
☐ ¿Todos los campos tienen label visible (no solo placeholder)?
☐ ¿Hay estados de error con mensajes específicos?
☐ ¿Los inputs usan el tipo correcto para cada dato?

ACCESIBILIDAD
☐ ¿Contraste mínimo 4.5:1 en texto normal, 3:1 en texto grande?
☐ ¿El diseño no depende SOLO del color para comunicar estado?
☐ ¿Los elementos interactivos son distinguibles visualmente?

ESPECIFICACIÓN PARA HANDOFF
☐ ¿Los componentes tienen nombres que el developer entiende?
☐ ¿Están especificados breakpoints y comportamiento responsive?
☐ ¿Las animaciones/transiciones están especificadas?
```

---

## Score de Evaluación del Output del Cerebro #3

| Categoría | Peso | Criterio |
|-----------|------|---------|
| Sistema de tokens definido | 25% | Presente y coherente |
| Estados de componentes completos | 20% | Mínimo 5 estados por componente interactivo |
| Accesibilidad (contraste WCAG AA) | 20% | 100% de textos verificados |
| Diseño mobile presente | 15% | Al menos 2 breakpoints |
| Especificación de handoff | 10% | Nomenclatura clara + especificaciones |
| Tipografía con sistema | 5% | Escala con ratio + máx 2 familias |
| Grid definido | 5% | Sistema de columnas por breakpoint |

**APROBACIÓN:**
- Score > 80%: APPROVE — Pasa a Cerebro #4
- Score 60-80%: CONDITIONAL — Pasa con notas de corrección
- Score < 60%: REJECT — Requiere revisión antes de continuar

---

## Preguntas de Auto-Evaluación del Cerebro #3

Antes de entregar cualquier output, el Cerebro #3 se pregunta:

1. ¿El Frontend puede implementar esto sin tomar decisiones de diseño por su cuenta?
2. ¿Si el color primario cambia mañana, cuántos archivos/componentes hay que modificar? (respuesta correcta: 1 — el token)
3. ¿Qué pasa cuando no hay datos? ¿Cuando hay un error? ¿Cuando carga? ¿Lo diseñé?
4. ¿Un usuario con baja visión puede usar este diseño?
5. ¿Un usuario zurdo en el metro con un teléfono de 5.5" puede completar la tarea principal?
6. ¿Este diseño es coherente con el output del Cerebro #2 (UX Research)?
7. ¿Hay algo en este diseño que contradiga los principios del Cerebro #1 (Product Strategy)?

---

## Conexión con otros Cerebros

| Cerebro | Relación con el Output del #3 |
|---------|-------------------------------|
| Cerebro #2 (UX Research) | INPUT: wireframes, journey maps, arquitectura de información. El #3 los convierte en interfaz visual. Si hay contradicción, escalar al humano. |
| Cerebro #4 (Frontend) | OUTPUT: components con estados, tokens, grid, especificaciones. El #4 implementa exactamente lo que el #3 entrega. |
| Cerebro #7 (Growth & Data) | EVALUADOR: el #7 mide si el diseño entregado produce los resultados esperados (conversión, engagement, retención). Si no, retroalimenta al #3. |

---

## Registro de Precedentes del Cerebro #3

*(Se actualizan con cada conflicto resuelto)*

```yaml
precedents: []
# Formato a usar cuando se registren:
# - id: "PREC-3XX"
#   date: "YYYY-MM-DD"
#   conflict_between: ["brain-03-ui-design", "brain-04-frontend"]
#   issue: "descripción"
#   resolution: "qué se decidió"
#   rule_created: "regla que aplica a futuras situaciones"
```
