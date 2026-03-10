---
source_id: "FUENTE-302"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Refactoring UI"
author: "Adam Wathan & Steve Schoger"
expert_id: "EXP-302"
type: "book"
language: "en"
year: 2019
isbn: "N/A"
url: "https://www.refactoringui.com"
skills_covered: ["H1", "H2", "H3"]
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
habilidad_primaria: "UI Visual Practical — Tomar decisiones de diseño sin teoría excesiva"
habilidad_secundaria: "Design decisions & Visual Hierarchy"
capa: 1
capa_nombre: "Base Conceptual — Principios Visuales Aplicados"
relevancia: "CRÍTICA — El libro más práctico y aplicable de UI; llena el gap entre teoría y decisiones reales"
---

# FUENTE-302 — Refactoring UI
## Adam Wathan & Steve Schoger | UI Design Práctico sin Exceso de Teoría

---

## Tesis Central

> Los diseñadores que no son diseñadores de formación cometen errores predecibles y corregibles. Estos no son errores de talento; son errores de criterio. Con los criterios correctos, cualquiera puede producir interfaces profesionales.

La mayoría de los problemas de UI vienen de las mismas 10-15 causas. Identificarlas y saber cómo corregirlas es más valioso que años de teoría del color.

---

## 1. PRINCIPIOS FUNDAMENTALES

**P1 — Empieza en escala de grises**
Sin color, los problemas de jerarquía se vuelven visibles. Si el diseño no funciona en grises, el color no lo va a salvar. Agrega color al final para reforzar jerarquía, no para crearla.

**P2 — Menos elementos visibles de lo que piensas**
El instinto del novato es poner más: más borders, más sombras, más colores, más texto. El instinto del experto es quitar: menos fronteras, más espacio, menos colores diferentes.

**P3 — La jerarquía es el único trabajo del diseñador**
Toda decisión de diseño (tamaño, peso, color, espacio) existe para comunicar importancia relativa. Si el usuario no sabe qué es lo más importante en 3 segundos, el diseño falló.

**P4 — No uses el color para crear jerarquía; úsalo para acentuarla**
Color = emoción y marca. Jerarquía = tamaño, peso, contraste, espacio. Mezclarlos causa interfaces donde todo "grita" pero nada se comunica.

**P5 — Los sistemas de diseño no se crean al principio; se descubren**
Empieza diseñando interfaces reales. Los patrones que se repiten se convierten en el sistema. Crear el sistema primero suele producir un sistema desconectado de la realidad del producto.

---

## 2. FRAMEWORKS Y METODOLOGÍAS

### Framework 1: Sistema de Jerarquía Visual — 3 niveles de énfasis

```
NIVEL 1 — Primario (1 elemento por pantalla / sección)
  → Peso: Bold / Extra Bold
  → Tamaño: Máximo de la escala
  → Color: Máximo contraste o color de acento

NIVEL 2 — Secundario (2-4 elementos)
  → Peso: Medium / Semibold
  → Tamaño: Intermedio
  → Color: Contraste moderado (70-80% del texto primario)

NIVEL 3 — Terciario / Decorativo (resto)
  → Peso: Regular
  → Tamaño: Mínimo legible
  → Color: Bajo contraste, gris (50-60% del texto primario)
```

**Regla de oro:** Si al mirar el diseño en escala de grises no puedes identificar los 3 niveles en 3 segundos, el diseño necesita más contraste entre niveles.

### Framework 2: Escala de Espaciado Fija (No inventes medidas)

Usar una escala con proporciones predefinidas elimina el "¿cuántos píxeles de margen?" de cada decisión:

```
Escala base 4px:
  2px  — Micro (separaciones internas)
  4px  — XXS
  8px  — XS (items en lista)
  12px — SM
  16px — MD (padding estándar de componente)
  24px — LG
  32px — XL
  48px — 2XL
  64px — 3XL (separaciones entre secciones)
  96px — 4XL (secciones grandes)
  128px — 5XL
```

**Regla:** Solo usa números de esta escala. Nunca 13px, 22px, 37px. Si un elemento "necesita" 13px, usa 12px o 16px. La escala fuerza coherencia.

### Framework 3: Sistema de Color Funcional

```
CATEGORÍAS DE COLOR EN UN PRODUCTO

Marca / Accent (1-2 colores)
  → Botones primarios, links, highlights
  → No usar en más del 10% de la interfaz

Neutros (7-9 tonos de gris)
  → Texto, fondos, borders, separadores
  → El 85% de la interfaz vive en neutros

Semánticos (4 colores fijos)
  → Success (verde): confirmaciones, estados completados
  → Warning (amarillo/naranja): alertas no críticas
  → Error (rojo): errores, destrucción, peligro
  → Info (azul): información neutral
```

**Regla:** Si tienes más de 5 colores distintos visibles en una pantalla, hay un problema de consistencia.

### Framework 4: Tipografía en Producto Digital — Decisiones Clave

```
ESCALA TIPOGRÁFICA MÍNIMA (en px para web):
  12px — Caption, helper text, timestamps
  14px — Body small, labels
  16px — Body, párrafos principales (mínimo recomendado)
  18px — Body large, lead text
  20px — Heading small (h4, h5)
  24px — Heading medium (h3)
  30px — Heading large (h2)
  36-48px — Display / Hero (h1)

PESOS RECOMENDADOS (sin exceder 3 pesos en un producto):
  400 — Regular: cuerpo de texto
  500/600 — Medium/Semibold: labels, subheadings, UI elements
  700 — Bold: headings, CTAs, énfasis crítico

REGLA LINE-HEIGHT:
  Headings: 1.1 - 1.3 (texto corto, tamaño grande)
  Body: 1.5 - 1.7 (texto largo, lectura cómoda)
  UI Labels: 1.2 - 1.4 (una sola línea)
```

---

## 3. MODELOS MENTALES

**MM1 — "De lejos, ¿qué llama la atención primero?"**
Test de squint (entrecerrar ojos): mira el diseño borroso. Lo que sigue visible = lo que tiene más peso visual. ¿Es lo correcto? Si no, ajusta jerarquía, no estética.

**MM2 — "El espacio en blanco no es espacio desperdiciado"**
El espacio en blanco es el respiradero del diseño. Cuando algo se siente "apretado", la respuesta casi siempre es más espacio, no menos contenido. El espacio crea jerarquía y relación entre elementos.

**MM3 — "¿Este borde es necesario?"**
Borders sirven para separar elementos. Pero el espacio y el fondo también separan. Antes de agregar un border, pregunta: ¿puede el espacio o un fondo diferente hacer este trabajo? Menos borders = más limpio.

**MM4 — "Sombras con propósito"**
Una sombra comunica elevación (z-index conceptual). Usa sombras pequeñas para elementos interactivos, sombras medianas para dropdowns/cards, sombras grandes para modals. Nunca uses la misma sombra para todo.

**MM5 — "El diseño sin datos reales es una mentira"**
Diseña con el peor caso: el nombre más largo, el texto más corto, la imagen faltante, el número con 6 dígitos. El diseño bonito con datos ideales es trampa; el diseño bueno con datos reales es profesionalismo.

---

## 4. CRITERIOS DE DECISIÓN

**CD1 — ¿Cuándo usar color en texto?**
Usa color en texto SOLO cuando: el color comunica estado (error = rojo, success = verde), el texto es un link interactivo, o es un elemento de acento muy específico. El resto del texto va en neutros de alto contraste.

**CD2 — ¿Cuándo agregar sombra vs. fondo diferente?**
Sombra: cuando el elemento "flota" sobre el contenido (modal, dropdown, tooltip, card interactiva).
Fondo diferente: cuando el elemento es parte del layout (sidebar, header, card de contenido).
No combines ambos en el mismo elemento sin razón.

**CD3 — Tamaño de fuente en móvil**
El mínimo absoluto de texto legible en móvil es 16px. Texto de UI (labels, helpers) puede bajar a 14px. Nunca menos de 12px para nada visible. Los sistemas que escalan de 14px en desktop a 16px en móvil se comportan al revés de lo correcto.

**CD4 — ¿Cuándo aumentar padding vs. reducir contenido?**
Cuando algo se ve apretado, el primer instinto debe ser aumentar padding. Solo reduce contenido si hay una razón de UX para ello (el contenido realmente no aporta). La restricción de espacio es una restricción de información, no de diseño.

**CD5 — ¿Cuánto énfasis tiene cada elemento?**
Si más del 30% de los elementos en una pantalla son "importantes", ninguno lo es. Reserva los tratamientos de alto énfasis (color de acento, bold, tamaño grande) para máximo 1-3 elementos por pantalla.

---

## 5. ANTI-PATRONES

**AP1 — "El arcoíris de colores"**
Síntoma: cada sección tiene un color diferente, sin sistema.
Consecuencia: la interfaz grita, el usuario no sabe dónde mirar.
Corrección: Limitar a 1-2 colores de acento + 7 tonos de gris + 4 colores semánticos.

**AP2 — "Texto gris sobre gris"**
Síntoma: texto de baja jerarquía en gris muy claro sobre fondo blanco o gris claro.
Consecuencia: accesibilidad rota (WCAG falla), usuario no puede leer.
Corrección: Verificar siempre contraste mínimo 4.5:1 para texto normal, 3:1 para texto grande.

**AP3 — "El border que todo lo rodea"**
Síntoma: cada card, sección y grupo tiene un border de 1px.
Consecuencia: la interfaz se ve pesada y compartimentada.
Corrección: Usar espacio y fondos para separar; reservar borders para inputs y separadores explícitos.

**AP4 — "El centrado absoluto"**
Síntoma: todo el texto, incluyendo bloques de texto largo, está centrado.
Consecuencia: dificulta la lectura; los párrafos centrados son incómodos de leer.
Corrección: Centrar solo texto corto (títulos, labels). Alinear a la izquierda cualquier texto de más de 2 líneas.

**AP5 — "La tipografía de exhibición para todo"**
Síntoma: se usa la fuente display/decorativa en botones, labels, body text.
Consecuencia: ilegibilidad, mezcla de registros visuales.
Corrección: Las fuentes display son para headings grandes. El cuerpo necesita una fuente diseñada para legibilidad a tamaño pequeño.

**AP6 — "Diseño sin estados"**
Síntoma: el diseño solo muestra el estado ideal; no hay loading, error, empty, disabled.
Consecuencia: el desarrollador inventa estos estados; el resultado es inconsistente.
Corrección: Para cada pantalla o componente interactivo, entregar los 5 estados: default, hover, active, disabled, error/empty.

---

## 6. CASOS Y EJEMPLOS REALES

**Caso 1: El rediseño del botón**
Situación: Un botón primario se veía "apagado" aunque tenía el color de marca correcto.
Diagnóstico (Schoger): El color de fondo era muy saturado pero el texto blanco no tenía suficiente contraste. La sombra era idéntica a todos los demás elementos.
Corrección: Texto blanco con peso semibold, sombra específica del color de marca (no gris genérico), padding aumentado 4px en vertical.
Resultado: El botón "vive" en la pantalla sin cambiar el color de marca.

**Caso 2: Dashboard que se sentía amateur**
Situación: Un developer diseñó su propio dashboard SaaS; los datos eran buenos pero el diseño se veía "hecho por un developer".
Diagnóstico: Sin jerarquía, todos los números del mismo tamaño, cards con borders en todos lados, colores aleatorios.
Solución aplicada: Quitar todos los borders internos → usar fondos de card en gris muy claro. Un solo número grande por card (el KPI principal). Texto secundario en gris #6. Color de acento solo en el número más importante.
Resultado: El mismo layout con el mismo código, transformado a profesional con cambios solo de estilos.

**Caso 3: Escala de grises como proceso de diseño**
Situación: Equipo de producto pedía diseños en escala de grises antes de ver color final.
Resultado: El 80% de los problemas de jerarquía se detectaban y resolvían en escala de grises. El color final se agregaba en horas, no días. Menos iteraciones en la fase de color.

---

## Conexión con el Cerebro #3

| Habilidad del Cerebro #3 | Aporte de esta fuente |
|--------------------------|----------------------|
| Tomar decisiones visuales rápidas y justificadas | Frameworks de jerarquía, color, tipografía |
| Evitar los errores comunes de UI | Catálogo de 6 anti-patrones con correcciones |
| Producir diseños profesionales sin exceso de herramientas | Criterios concretos y accionables |
| Handoff a Frontend (Cerebro #4) | Sistemas de espaciado y tipografía que un dev puede implementar |

## Preguntas que el Cerebro #3 puede responder con esta fuente

1. ¿Por qué este diseño se ve amateur y cómo lo corrijo?
2. ¿Qué nivel de jerarquía tiene cada elemento en esta pantalla?
3. ¿Cómo construyo un sistema de color que funcione?
4. ¿Cuánto padding debería tener este componente?
5. ¿Cómo hago que este botón se vea más prominente sin cambiar el color de marca?
