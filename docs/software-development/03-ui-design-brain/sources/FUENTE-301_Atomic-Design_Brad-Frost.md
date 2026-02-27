---
source_id: "FUENTE-301"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Atomic Design"
author: "Brad Frost"
expert_id: "EXP-301"
type: "book"
language: "en"
year: 2016
isbn: "978-0-692-81080-5"
url: "https://atomicdesign.bradfrost.com"
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

# Metadatos específicos del Cerebro #3 (mantenidos para compatibilidad)
habilidad_primaria: "Design Systems & Component Architecture"
habilidad_secundaria: "Scalable UI & Handoff"
capa: 1
capa_nombre: "Base Conceptual — Design Systems"
relevancia: "CRÍTICA — Define cómo estructurar interfaces escalables desde el átomo hasta la página"
---

# FUENTE-301 — Atomic Design
## Brad Frost | Metodología de Design Systems

---

## Tesis Central

> Los interfaces de usuario son combinaciones de componentes. Si diseñas los componentes correctamente, el sistema se construye solo. No diseñes páginas; diseña sistemas de componentes.

El error más costoso en UI es diseñar pantallas sin pensar en los ladrillos que las componen. Atomic Design propone una jerarquía de 5 niveles que asegura coherencia, reutilización y escalabilidad.

---

## 1. PRINCIPIOS FUNDAMENTALES

**P1 — La interfaz es química, no arte**
Los componentes de UI se combinan como átomos y moléculas. Un botón solo (átomo) tiene poco valor; un botón + campo de texto (molécula) resuelve un problema. La belleza emerge de la composición, no de piezas individuales bonitas.

**P2 — Consistencia > Originalidad en sistemas**
En un producto digital, la variación visual injustificada crea ruido cognitivo. Cada variante de un componente debe justificarse por una necesidad funcional diferente, no por preferencia estética.

**P3 — El patrón es el producto**
Documentar los componentes es tan importante como crearlos. Un componente sin documentación es conocimiento que muere con el diseñador que lo creó.

**P4 — Mobile-first by default**
Diseñar primero para la pantalla más pequeña fuerza prioridad de contenido. Lo que funciona en móvil siempre puede escalar; lo contrario no.

**P5 — Nomenclatura compartida = colaboración real**
Cuando diseñadores, desarrolladores y stakeholders usan el mismo nombre para los mismos elementos, la fricción de handoff desaparece.

---

## 2. FRAMEWORKS Y METODOLOGÍAS

### Framework Central: Los 5 Niveles de Atomic Design

```
ÁTOMOS → MOLÉCULAS → ORGANISMOS → PLANTILLAS → PÁGINAS
```

**Nivel 1 — Átomos**
- Definición: Elementos HTML básicos que no pueden dividirse sin perder función
- Ejemplos: botón, campo de texto, ícono, etiqueta, color, tipografía, espaciado
- Regla: Un átomo tiene una sola responsabilidad
- En Figma/código: Variables de diseño, tokens, componentes base

**Nivel 2 — Moléculas**
- Definición: Grupos simples de átomos que funcionan juntos como unidad
- Ejemplos: campo de búsqueda (input + botón), card de perfil (avatar + nombre + rol)
- Regla: Una molécula hace una cosa bien
- En Figma/código: Componentes compuestos simples

**Nivel 3 — Organismos**
- Definición: Secciones complejas de UI formadas por moléculas y/o átomos
- Ejemplos: navbar (logo + navegación + CTA), formulario de login, card grid
- Regla: Un organismo es una sección reconocible de la interfaz
- En Figma/código: Secciones reutilizables entre páginas

**Nivel 4 — Plantillas**
- Definición: Estructura de página sin contenido real; skeleton funcional
- Ejemplos: layout de dashboard, estructura de landing page, flujo de checkout
- Regla: La plantilla prueba que los componentes encajan antes de poner contenido real
- En Figma: Frames con Auto Layout que muestran la estructura

**Nivel 5 — Páginas**
- Definición: Plantillas con contenido real; lo que el usuario ve
- Propósito: Validar que el sistema funciona con datos reales (texto largo, imagen faltante, error state)
- Regla: Las páginas revelan los edge cases del sistema

### Framework: Design System Checklist (antes de lanzar un sistema)

```
FUNDAMENTOS
☐ Paleta de color definida con tokens (primary, secondary, semantic, neutral)
☐ Escala tipográfica (heading 1-6, body, caption, label)
☐ Escala de espaciado (4px / 8px / 16px / 24px / 32px / 48px / 64px)
☐ Grid system definido (columnas, gutters, breakpoints)
☐ Iconografía unificada (una sola librería, mismo peso visual)

ÁTOMOS
☐ Botones (primary, secondary, ghost, destructive, disabled, loading)
☐ Inputs (text, password, search, date, disabled, error, success)
☐ Badges y etiquetas
☐ Avatares
☐ Dividers y separadores

MOLÉCULAS
☐ Form fields (label + input + helper text + error message)
☐ Cards base
☐ Navigation items
☐ Notifications / Toast

ORGANISMOS
☐ Header / Navbar
☐ Sidebar / Navigation
☐ Forms completos
☐ Data tables
☐ Modals y Drawers

ESTADOS
☐ Empty states (sin datos)
☐ Loading states (skeleton, spinners)
☐ Error states (con mensajes accionables)
☐ Success states
```

---

## 3. MODELOS MENTALES

**MM1 — "¿Es esto un átomo o una molécula?"**
Antes de crear un componente nuevo, pregunta: ¿Este elemento puede dividirse? ¿Tiene una sola responsabilidad? Si la respuesta a la primera es sí y a la segunda es no, está en el nivel equivocado.

**MM2 — "El sistema antes que la pantalla"**
Cuando diseñes un dashboard nuevo, no empieces por el dashboard. Empieza por los componentes que necesitará. El dashboard se arma en minutos si los componentes ya existen.

**MM3 — "Content-first, structure always"**
Las plantillas revelan verdades que las páginas con Lorem Ipsum ocultan. Diseña con contenido real desde el inicio: nombres de 3 palabras, títulos de 12 palabras, listas con 1 item y con 50.

**MM4 — "Un cambio en el átomo cambia todo"**
Si cambias el color del botón primario en el token, cambia en toda la interfaz. Esto es poder cuando el sistema está bien construido; es terror cuando no lo está. Nunca edites instancias; siempre edita el componente maestro.

---

## 4. CRITERIOS DE DECISIÓN

**CD1 — Crear componente nuevo vs. adaptar existente**
Cuando una variante es diferente en propósito (no solo en estética), crea un componente nuevo.
Cuando la diferencia es solo visual (tamaño, color), usa props del componente existente.
Señal de alerta: si tienes más de 5 variantes sin documentación, el sistema se está fragmentando.

**CD2 — Cuándo usar un Design System externo vs. crear el propio**
Usa Material Design / Shadcn / Ant Design cuando: el tiempo es crítico, el equipo es pequeño, el producto es interno.
Crea tu propio sistema cuando: la identidad de marca es diferenciadora, el producto tiene interacciones únicas, el equipo escala >5 diseñadores.
Nunca mezcles dos sistemas base sin una capa de abstracción propia.

**CD3 — Nivel de abstracción correcto**
Demasiado granular (todo son átomos): el sistema es inflexible y difícil de usar.
Demasiado genérico (todo son organismos): el sistema no se puede reutilizar.
Regla práctica: si un componente se usa en 3+ lugares distintos, merece su propio slot en el sistema.

**CD4 — Cuándo documentar un componente**
Todo componente que vaya a tocar otro diseñador o desarrollador necesita documentación mínima: propósito, variantes, estados, cuándo usarlo y cuándo NO usarlo.

---

## 5. ANTI-PATRONES

**AP1 — "Diseñar pantallas, no sistemas"**
Síntoma: cada pantalla nueva empieza desde cero, los componentes se parecen pero no son los mismos.
Consecuencia: inconsistencia, deuda de diseño exponencial, handoff caótico.
Corrección: Antes de diseñar una pantalla nueva, auditar qué componentes ya existen.

**AP2 — "El botón del infierno"**
Síntoma: existen 12 variantes de botón con diferencias mínimas y sin documentación de cuándo usar cada una.
Consecuencia: el desarrollador elige aleatoriamente, el producto pierde coherencia.
Corrección: Reducir a máximo 5 variantes justificadas funcionalmente.

**AP3 — "Lorem Ipsum como diseño"**
Síntoma: se aprueba diseño con texto de relleno y luego hay sorpresas con el contenido real.
Consecuencia: layouts rotos, truncamientos inesperados, edge cases no contemplados.
Corrección: Usar siempre contenido real o contenido representativo con variaciones extremas.

**AP4 — "Design System muerto"**
Síntoma: el design system existe pero nadie lo actualiza, hay componentes desactualizados.
Consecuencia: los diseñadores lo ignoran y empiezan a crear componentes propios.
Corrección: Asignar ownership explícito del sistema; tratarlo como producto, no como entregable.

**AP5 — "Sistemas sin estados"**
Síntoma: los componentes solo muestran el estado ideal; no tienen loading, error, empty, disabled.
Consecuencia: los desarrolladores inventan los estados y el resultado es inconsistente.
Corrección: Todo componente interactivo requiere mínimo 5 estados: default, hover, active, disabled, error.

---

## 6. CASOS Y EJEMPLOS REALES

**Caso 1: Airbnb Design Language System**
Situación: Airbnb tenía inconsistencias de UI en web, iOS y Android.
Decisión: Implementar Atomic Design con "Design Language System" (DLS) y un equipo dedicado.
Resultado: Reducción del 80% en tiempo de diseño de nuevas features; coherencia entre plataformas. Los componentes se documentaron con casos de uso y anti-casos.

**Caso 2: Shopify Polaris**
Situación: Cientos de tiendas usando el admin de Shopify; necesidad de coherencia sin perder velocidad.
Decisión: Design system open source con componentes, tokens, guías de escritura y principios.
Resultado: Polaris se convirtió en estándar para apps del App Store de Shopify; los partners pueden construir interfaces coherentes sin necesitar diseñadores.

**Caso 3: Brad Frost en sitio web de consulta — Problema de atomicidad**
Situación: Un cliente quería "un botón ligeramente diferente para esta sección".
Decisión: En lugar de crear variante nueva, analizar si la diferencia era funcional o estética.
Resultado: La diferencia era estética; se usó el mismo componente con una prop de tamaño. Evitó fragmentación del sistema.

---

## Conexión con el Cerebro #3

| Habilidad del Cerebro #3 | Aporte de esta fuente |
|--------------------------|----------------------|
| Crear sistemas de diseño escalables | Framework completo de 5 niveles |
| Handoff limpio a Frontend (Cerebro #4) | Nomenclatura compartida, componentes documentados |
| Coherencia visual en todo el producto | Tokens y átomos como single source of truth |
| Velocidad de diseño en iteraciones | Sistema construido = pantallas nuevas en minutos |

## Preguntas que el Cerebro #3 puede responder con esta fuente

1. ¿Cómo estructuro los componentes de este diseño para que sea escalable?
2. ¿Qué nivel de Atomic Design es este elemento?
3. ¿Qué estados debe tener este componente?
4. ¿Cuándo creo un componente nuevo vs. adapto uno existente?
5. ¿Cómo organizo el design system en Figma?
