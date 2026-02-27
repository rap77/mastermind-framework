---
source_id: "FUENTE-303"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Mobile First"
author: "Luke Wroblewski"
expert_id: "EXP-303"
type: "book"
language: "en"
year: 2011
isbn: "978-1-937557-02-7"
url: "https://abookapart.com/products/mobile-first"
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
status: "active"

# Metadatos específicos del Cerebro #3
habilidad_primaria: "Responsive Design & Mobile UI"
habilidad_secundaria: "Priorización de contenido y funcionalidad"
capa: 2
capa_nombre: "Frameworks — Diseño Responsive y Priorización"
relevancia: "ALTA — Define el enfoque mental correcto para diseñar en la era multi-dispositivo"
---

# FUENTE-303 — Mobile First
## Luke Wroblewski | El Enfoque que Cambió el Diseño Web

---

## Tesis Central

> Diseñar primero para móvil no es una restricción; es una disciplina. Te obliga a descubrir qué importa de verdad, porque en móvil no hay espacio para lo que no importa.

La filosofía "Mobile First" no es sobre hacer versiones móviles; es sobre repensar el orden del proceso de diseño para que la prioridad de contenido y funcionalidad esté clara desde el inicio.

---

## 1. PRINCIPIOS FUNDAMENTALES

**P1 — La restricción revela la esencia**
Cuando solo puedes mostrar 3 cosas en pantalla, descubres cuáles son las 3 más importantes. Diseñar desde desktop permite esconder la indecisión con espacio. Diseñar desde móvil obliga claridad.

**P2 — Mobile-first no es mobile-only**
El objetivo es diseñar para la experiencia más restringida primero, luego expandir. No es abandonar desktop; es no depender de él para tomar decisiones de prioridad.

**P3 — Los usuarios móviles no son usuarios de segunda clase**
En 2010 esto era controversial; hoy es dato: más del 60% del tráfico web es móvil. Diseñar móvil como "versión reducida" de desktop produce experiencias de segunda clase para la mayoría de usuarios.

**P4 — Contexto móvil ≠ contexto desktop**
El usuario en móvil puede estar: caminando, esperando, con una sola mano, con sol en la pantalla, en contexto de prisa. El diseño debe acomodar el peor escenario de uso, no el ideal.

**P5 — Las capacidades móviles son ventajas, no limitaciones**
Geolocalización, cámara, notificaciones push, touch, sensores de movimiento: los dispositivos móviles tienen capacidades que el desktop no. Mobile-first también significa pensar cómo aprovecharlas.

---

## 2. FRAMEWORKS Y METODOLOGÍAS

### Framework 1: El Proceso Mobile-First

```
PASO 1: INVENTARIO DE CONTENIDO Y FUNCIONES
  → Lista todo lo que el producto necesita mostrar/hacer
  → Sin pensar en pantallas ni layouts todavía

PASO 2: PRIORIZACIÓN BRUTAL
  → Clasifica cada elemento: Esencial / Importante / Secundario / Prescindible
  → En móvil: solo Esenciales e Importantes aparecen Above the fold
  → Los Secundarios requieren interacción (accordion, tab, scroll)
  → Los Prescindibles: ¿por qué existen?

PASO 3: DISEÑAR LA VERSIÓN MÓVIL (320-375px)
  → Una columna, flujo vertical
  → Navegación colapsada o simplificada
  → Cada acción con target mínimo de 44x44px (Apple) / 48x48px (Google)
  → Formularios con inputs apropiados para móvil

PASO 4: DISEÑAR LA VERSIÓN TABLET (768px)
  → Aprovechar espacio adicional con 2 columnas donde tenga sentido
  → Navegación puede expandirse parcialmente

PASO 5: DISEÑAR LA VERSIÓN DESKTOP (1024-1440px+)
  → Añadir columnas, paneles laterales, información adicional
  → La estructura ya está validada; es expansión, no rediseño

PASO 6: VALIDAR QUE EL DESKTOP NO AÑADIÓ RUIDO
  → ¿Todo lo nuevo en desktop tiene justificación?
  → ¿La prioridad establecida en móvil se mantiene en desktop?
```

### Framework 2: Grid Responsive Estándar

```
MOBILE (320-767px)
  → 4 columnas
  → Gutter: 16px
  → Margin: 16-24px

TABLET (768-1023px)
  → 8 columnas
  → Gutter: 24px
  → Margin: 24-48px

DESKTOP (1024-1440px)
  → 12 columnas
  → Gutter: 24-32px
  → Margin: Fijo o max-width centrado

LARGE SCREEN (1440px+)
  → 12 columnas con max-width contenedor
  → Generalmente max-width: 1280px o 1440px
  → Fondos pueden extenderse a full-width
```

### Framework 3: Patrones de Navegación Mobile-First

```
PATRÓN 1 — Hamburger + Drawer
  Cuándo: Más de 5 items de navegación principal
  Pro: Máximo espacio para contenido
  Contra: Menor descubribilidad; el usuario no sabe qué hay sin abrir

PATRÓN 2 — Tab Bar (Bottom Navigation)
  Cuándo: 3-5 secciones principales de alta frecuencia
  Pro: Siempre visible, accesible con pulgar
  Contra: Máximo 5 items; no escala

PATRÓN 3 — Top Navigation Bar (visible)
  Cuándo: 3-4 secciones principales
  Pro: Familiar, descriptivo
  Contra: Ocupa espacio vertical valioso en móvil

PATRÓN 4 — Priority+ Navigation
  Cuándo: Número variable de items (breadcrumbs, filtros, tags)
  Cómo: Muestra los más importantes; el resto en "más" o scroll horizontal

REGLA GENERAL: En móvil, el pulgar debe poder alcanzar todas las acciones
principales sin reposicionar el agarre.
```

### Framework 4: Touch Targets y Accesibilidad en Móvil

```
TAMAÑOS MÍNIMOS DE TARGETS TÁCTILES:
  Apple HIG: 44x44pt mínimo
  Google Material: 48x48dp mínimo
  WCAG 2.5.5 (AAA): 44x44px

ESPACIADO ENTRE TARGETS:
  Mínimo 8px entre targets táctiles adyacentes

ZONAS DE CONFORT DEL PULGAR (teléfono promedio ~5.5"):
  Verde (fácil): Franja horizontal baja de la pantalla
  Amarillo (estiramiento): Franja media
  Rojo (difícil): Esquinas superiores

IMPLICACIÓN DE DISEÑO:
  → Acciones primarias (CTA, siguiente): zona verde
  → Navegación secundaria: zona amarilla
  → Acciones destructivas (eliminar): zona roja (fricción intencional)
```

---

## 3. MODELOS MENTALES

**MM1 — "¿Qué pasa si quito el 50% del espacio?"**
Antes de finalizat cualquier layout, imagina que tienes la mitad del espacio. ¿Qué se cae primero? Eso que se cae primero es lo de menor prioridad. ¿Estás cómodo con eso?

**MM2 — "El usuario con una sola mano"**
Diseña pensando en alguien que tiene el teléfono en una mano y no puede usar la otra. ¿Puede completar las tareas principales? Las acciones críticas deben estar en la zona del pulgar.

**MM3 — "Desktop es la extensión, no la base"**
Cuando pienses en desktop, piénsalo como "¿qué puedo agregar ahora que tengo más espacio?" No como "¿qué debo quitar para móvil?" El primer enfoque construye coherencia; el segundo produce experiencias degradadas.

**MM4 — "Contexto de uso real"**
Antes de diseñar, pregunta: ¿Cuándo, dónde y cómo usa el usuario este producto? Si la respuesta incluye "mientras camina" o "con una mano", el diseño debe acomodar eso. Si la respuesta es "sentado en escritorio con tiempo", puedes ser más complejo.

---

## 4. CRITERIOS DE DECISIÓN

**CD1 — ¿Mostrar u ocultar en móvil?**
Mostrar si: el usuario necesita esta información para completar su tarea principal.
Ocultar (en accordion/tab/scroll) si: es información de soporte o contexto secundario.
Eliminar si: no impacta ninguna decisión del usuario. Si no sabes cuál de las tres aplica, es señal de que la función no está bien definida.

**CD2 — ¿Bottom navigation o hamburger?**
Bottom navigation cuando: son 3-5 secciones de alta frecuencia de uso, la app es mobile-first por naturaleza.
Hamburger cuando: hay más de 5 secciones, algunas son de acceso poco frecuente, el espacio vertical es crítico.
Nunca: bottom nav + hamburger en la misma app (confusión de sistema de navegación).

**CD3 — ¿Cuándo un patrón de desktop es válido en móvil?**
Un patrón de desktop es válido en móvil cuando: el contexto de uso es igual, el usuario tiene el mismo tiempo y atención, la tarea es la misma. En caso contrario, rediseña el patrón para el contexto móvil.

**CD4 — ¿Diseño nativo vs. web en móvil?**
Web (responsive/PWA): cuando la experiencia es principalmente de contenido y descubrimiento.
Nativo (iOS/Android): cuando la experiencia requiere rendimiento alto, acceso a hardware, o notificaciones push como core del producto.
Los criterios de diseño de Wroblewski aplican a ambos, pero los patrones de navegación difieren.

---

## 5. ANTI-PATRONES

**AP1 — "Desktop shrink"**
Síntoma: tomar el diseño desktop y escalarlo para que quepa en móvil.
Consecuencia: texto ilegible, targets imposibles de tocar, navegación horizontal no intuitiva.
Corrección: Rediseñar el flujo desde cero para móvil, no comprimir el desktop.

**AP2 — "Funciones ocultas sin señal"**
Síntoma: funcionalidad importante escondida en menú hamburger sin ninguna pista visual de que existe.
Consecuencia: usuarios que no descubren funciones clave; métricas de uso engañosas.
Corrección: Las funciones de uso frecuente deben ser visibles. La visibilidad en móvil debe ganarse, no asumir que el usuario va a explorar.

**AP3 — "El formulario de escritorio en móvil"**
Síntoma: formulario con 8 campos visibles, dropdowns sin adaptar al teclado, fecha sin date picker nativo.
Consecuencia: abandono de formulario en móvil.
Corrección: Formularios en móvil necesitan: un campo visible a la vez cuando sea posible, inputs que activen el teclado correcto (type=email, tel, number), date pickers nativos.

**AP4 — "Hover como única señal de interactividad"**
Síntoma: tooltips, menus y estados que solo se activan con hover del mouse.
Consecuencia: en móvil no hay hover; la función es inaccesible.
Corrección: Todo estado de hover debe tener un equivalente táctil (tap para mostrar, long press, swipe).

**AP5 — "El carousel forzado"**
Síntoma: contenido puesto en carousel automático (autoplay) en móvil.
Consecuencia: el usuario pierde control de qué ve y cuándo; el contenido después del primero tiene near-zero engagement.
Corrección: En móvil, scroll vertical > carousel para contenido de igual jerarquía.

---

## 6. CASOS Y EJEMPLOS REALES

**Caso 1: The Boston Globe — Primer sitio de noticias completamente responsive**
Situación: Rediseño de uno de los periódicos más importantes de EE.UU. con audiencia multi-dispositivo.
Decisión: Adoptar Mobile First como filosofía de rediseño; definir prioridad de contenido en móvil antes de diseñar desktop.
Resultado: Referente que demostró que Mobile First era viable para contenido editorial complejo. Forzó editorial a definir qué historias eran realmente importantes (beneficio colateral).

**Caso 2: Google Search en móvil**
Situación: La simplicidad de la búsqueda de Google en desktop (una caja) era fácil de implementar. El desafío era los resultados.
Decisión: En móvil, los resultados priorizan la respuesta directa (featured snippets, knowledge panels) sobre los links de página. La jerarquía visual se rediseñó desde cero.
Resultado: En móvil, el usuario consigue la respuesta sin clic en muchos casos; mayor satisfacción, diferente modelo de negocio (implicación de diseño con consecuencias de producto).

**Caso 3: E-commerce — Reducción del abandono en checkout móvil**
Situación: Una tienda online con 70% de tráfico móvil pero 80% de conversiones en desktop.
Diagnóstico: El checkout era el desktop shrink, con 12 campos visibles, inputs incorrectos y sin progreso visible.
Solución Mobile First: Checkout en 3 pasos, un paso visible a la vez, inputs nativos, progress bar siempre visible, CTA en zona del pulgar.
Resultado: Conversión en móvil subió 40%; brecha desktop/móvil se redujo a 15%.

---

## Conexión con el Cerebro #3

| Habilidad del Cerebro #3 | Aporte de esta fuente |
|--------------------------|----------------------|
| Diseñar para múltiples dispositivos coherentemente | Framework de proceso Mobile First completo |
| Tomar decisiones de prioridad de contenido | Modelo mental de restricción como herramienta |
| Diseñar navegación en móvil | Patrones de navegación con criterios de selección |
| Accesibilidad táctil | Framework de touch targets y zonas del pulgar |

## Preguntas que el Cerebro #3 puede responder con esta fuente

1. ¿Cuál es el orden correcto para diseñar versiones responsive?
2. ¿Qué contenido/funciones debo priorizar en la versión móvil?
3. ¿Qué patrón de navegación es correcto para este producto móvil?
4. ¿Los touch targets de esta pantalla cumplen los estándares?
5. ¿Cómo adapto este formulario de desktop para móvil?
