---
id: FUENTE-210
cerebro: 02-ux-research
titulo: 'Laws of UX: Using Psychology to Design Better Products & Services'
autor: Jon Yablonski
tipo: libro + sitio-web
isbn: 978-1492055310
url_complementaria: https://lawsofux.com
edicion: 1st Edition
año: 2020
capa: base-conceptual + criterios-decision
experto: Jon Yablonski
habilidad: Psicología aplicada al diseño de interacción
tags:
- psychology
- cognitive-laws
- hick
- fitts
- miller
- jakob
- peak-end
- zeigarnik
- doherty
- gestalt
- serial-position
version_ficha: '1.0'
fecha_creacion: '2026-02-24'
source_id: FUENTE-210
brain: brain-software-02-ux-research
niche: software-development
title: 'Laws of UX: Using Psychology to Design Better Products & Services'
author: Jon Yablonski
type: libro + sitio-web
year: 2020
expert_id: EXP-210
language: en
skills_covered:
- U3
- U5
distillation_date: '2026-02-24'
distillation_quality: complete
loaded_in_notebook: true
version: 1.0.1
last_updated: '2026-02-25'
changelog:
- version: 1.0.0
  date: '2026-02-24'
  changes:
  - Destilación inicial completa
  - Campos estándar de versioning agregados
- version: 1.0.1
  date: '2026-02-25'
  changes:
  - 'Cargada en NotebookLM (Cerebro #2 UX Research)'
  - 'Notebook ID: ea006ece-00a9-4d5c-91f5-012b8b712936'
status: active
---



# FUENTE-210 — Laws of UX
**Jon Yablonski | O'Reilly Media, 2020 + lawsofux.com**

---

## 1. Por qué esta fuente es indispensable para el Cerebro #2

Yablonski compila y hace accionables las leyes psicológicas que fundamentan el comportamiento del usuario en interfaces digitales. Es la síntesis más eficiente del conocimiento psicológico relevante para UX — cada ley tiene respaldo empírico y aplicación directa. Para el Cerebro #2, esta fuente es el "catálogo de argumentos psicológicos" que justifica o refuta decisiones de diseño antes de que lleguen al Cerebro #3.

---

## 2. Las Leyes Maestras del Cerebro #2

A continuación, las leyes más críticas con definición, fundamento, y aplicación directa:

---

### LEY 1 — Ley de Hick
**"El tiempo para tomar una decisión aumenta con el número y complejidad de las opciones disponibles."**

**Origen:** William Edmund Hick (1952), derivada de teoría de información.
**Fórmula:** T = b × log₂(n + 1) donde n = número de opciones

**Aplicación en UX:**
- Reducir opciones en puntos de decisión crítica
- Dividir tareas complejas en pasos secuenciales más simples
- No presentar todas las features simultáneamente — progressive disclosure
- En e-commerce: menos opciones de filtro → más conversiones (paradoja de la elección)

**Cuándo viola esta ley el diseño:**
- Menús con > 7 opciones en el mismo nivel
- Formularios con más de 3-4 campos en la vista inicial
- Dashboards con > 5 acciones primarias disponibles simultáneamente
- Onboarding que presenta todas las features en una sola pantalla

**Pregunta del #2:** ¿Cuántas opciones tiene el usuario en el peor punto de decisión del flujo?

---

### LEY 2 — Ley de Fitts
**"El tiempo para llegar a un target es función de la distancia al target y su tamaño."**

**Origen:** Paul Fitts (1954), modelo matemático de movimiento motor.
**Fórmula:** T = a + b × log₂(2D/W) donde D = distancia, W = anchura del target

**Aplicación en UX:**
- Botones de acción más grande = más fácil de clickear = menos error
- Los elementos de uso frecuente deben estar más cerca del cursor/pulgar
- Los elementos peligrosos (borrar, desactivar) deben ser más pequeños y estar alejados
- Las esquinas de la pantalla son puntos de alta accesibilidad (el cursor se detiene ahí)

**Benchmarks de tamaño mínimo:**
- Desktop: 44x44px mínimo para elementos interactivos
- Mobile: 44x44px según Apple HIG, 48x48dp según Google Material Design
- Para usuarios con dificultad motora: mínimo 60x60px

**Cuándo viola esta ley el diseño:**
- CTAs principales pequeños o en posición periférica
- Botones de "Cancelar" y "Confirmar" del mismo tamaño y muy próximos
- Targets touch < 44px en mobile

**Pregunta del #2:** ¿Los elementos más importantes son los más grandes y fáciles de alcanzar?

---

### LEY 3 — Ley de Miller
**"El número mágico es 7 ± 2: la capacidad de la memoria de trabajo es de 5-9 elementos."**

**Origen:** George Miller (1956), psicología cognitiva.
**Actualización:** Cowan (2001) redujo el número a 4 ± 1 para unidades no relacionadas.

**Aplicación en UX:**
- No presentar más de 5-7 ítems de navegación simultáneamente
- Dividir listas largas en grupos de 5-7
- Agrupar información relacionada (chunking) para reducir carga cognitiva
- Números de teléfono, tarjetas, y códigos se formatean en grupos (chunking)

**Chunking en práctica:**
```
Sin chunking: 4155551234 → difícil de recordar
Con chunking: (415) 555-1234 → 3 grupos memorables
```

**Cuándo viola esta ley el diseño:**
- Navegación principal con > 7 ítems sin agrupamiento
- Formularios con > 5-7 campos visibles simultáneamente sin separadores
- Listas de opciones sin categorización cuando superan 7 elementos

---

### LEY 4 — Ley de Jakob
**"Los usuarios pasan la mayor parte del tiempo en OTROS sitios, por lo que esperan que tu sitio funcione igual que los que ya conocen."**

**Origen:** Jakob Nielsen (observación empírica a partir de investigación de usabilidad).

**Aplicación en UX:**
- Respetar convenciones establecidas por los productos líderes del mercado
- El costo de innovar en interacción base = curva de aprendizaje del usuario
- Si vas a romper una convención, el beneficio debe ser masivo y obvio

**Convenciones por contexto:**
| Contexto | Convención establecida |
|---|---|
| E-commerce | Carrito arriba derecha, checkout en pasos |
| SaaS | Sidebar de navegación izquierda, top bar con perfil |
| Mobile apps | Tab bar inferior, hamburger menú |
| Forms | Submit button al final, labels arriba del campo |
| Search | Campo de búsqueda con ícono de lupa a la derecha |

**Cuándo romper una convención (raramente):**
- Cuando la convención existente crea un problema de usabilidad documentado
- Cuando el producto tiene una propuesta de valor fundamentalmente diferente
- Cuando tienes research que demuestra que los usuarios aceptan el cambio

---

### LEY 5 — Peak-End Rule
**"Las personas juzgan una experiencia basándose principalmente en cómo se sintieron en su punto más intenso y en su final, no en el promedio de todos los momentos."**

**Origen:** Daniel Kahneman, Barbara Fredrickson (1993), psicología cognitiva.

**Aplicación en UX:**
- Diseñar picos positivos deliberados en los momentos de máxima intensidad emocional
- El final del flujo (confirmación, éxito, cierre) es desproporcionadamente importante
- Un peak negativo (error, pérdida de datos, falla de pago) contamina toda la experiencia

**Momentos pico en productos digitales:**
- Primer logro significativo del usuario (primer proyecto creado, primera venta)
- Momento de pago/compromiso financiero
- Error crítico o pérdida de trabajo
- Completar onboarding

**Momentos finales críticos:**
- Confirmación de compra
- Completar una tarea importante
- Cierre de sesión o salida del flujo
- Mensaje de error (si este es el último momento, contamina todo)

**Implicación directa:** Una app con UX promedio pero con un final memorable puede ser recordada mejor que una con UX excelente y un final apagado.

---

### LEY 6 — Efecto de Posición Serial
**"Los usuarios recuerdan mejor el primer y el último elemento de una lista."**

**Origen:** Hermann Ebbinghaus (1885), curva del olvido.
**Componentes:** Efecto de primacía (primer elemento) + Efecto de recencia (último elemento)

**Aplicación en UX:**
- Las opciones más importantes van primero o al final de las listas
- El elemento del medio de una lista de opciones es el menos recordado
- En navegación: los items más críticos van primero y/o al final
- En formularios de opción múltiple: opciones "ni neutral ni extremo" van al final

**Ejemplo de aplicación:**
- Pricing tables: el plan recomendado va al extremo (primero o último), no en el medio
- Call-to-actions en email: el CTA principal va al inicio Y al final

---

### LEY 7 — Ley de Tesler (Conservación de la Complejidad)
**"Para cualquier sistema existe una cantidad de complejidad inherente que no puede ser eliminada — solo puede ser transferida."**

**Origen:** Larry Tesler (Apple, Xerox PARC).

**Aplicación en UX:**
- Simplificar la UI para el usuario inevitablemente complejiza el sistema o el desarrollo
- La pregunta es: ¿quién debe cargar con la complejidad? (¿el usuario o el equipo de desarrollo?)
- La respuesta correcta casi siempre es: el equipo de desarrollo carga con la complejidad para que el usuario no tenga que hacerlo

**Ejemplos de transferencia de complejidad:**
- Autocompletar → El sistema complejiza la base de datos, el usuario no escribe
- Guardar automáticamente → El sistema maneja el estado, el usuario no presiona Ctrl+S
- Sugerir formato → El sistema valida, el usuario no memoriza formatos

**Trampa frecuente:** Simplificar la UI eliminando opciones que el usuario necesita (complejidad real, no aparente) en lugar de eliminar complejidad innecesaria.

---

### LEY 8 — Efecto de Usabilidad Estética
**"Los usuarios creen que los diseños estéticamente agradables funcionan mejor."**

**Origen:** Masaaki Kurosu y Kaori Kashimura (1995), replicado por Tractinsky.

**Aplicación en UX:**
- La percepción de calidad de un producto está influenciada por su apariencia visual
- Diseños poco atractivos generan mayor tolerancia cero a problemas de usabilidad
- La inversión en UI polish tiene ROI en percepción de confianza y calidad

**Implicación crítica:** Un producto feo con buena usabilidad será percibido como menos usable que uno bonito con usabilidad equivalente. La estética no es superficial — es funcional para la percepción del usuario.

---

### LEY 9 — Efecto Zeigarnik
**"Las personas recuerdan mejor las tareas incompletas que las completadas."**

**Origen:** Bluma Zeigarnik (1927), psicología cognitiva.

**Aplicación en UX:**
- Progress bars y completion metrics generan tensión psicológica que motiva a completar
- Los estados incompletos (perfil al 60%, steps pendientes) son más motivadores que los completados
- Gamification basada en progreso aprovecha directamente el efecto Zeigarnik

**Ejemplos de aplicación:**
- LinkedIn: "Tu perfil está al 73% completo"
- Duolingo: streaks y progress tracking
- E-commerce: "Te faltan $20 para envío gratis"
- Onboarding: checklist de configuración inicial

**Advertencia:** El efecto Zeigarnik puede generar ansiedad si los elementos incompletos son demasiados o irrelevantes. Usar con moderación y solo con tareas de alta relevancia para el usuario.

---

### LEY 10 — Ley de Prägnanz (Gestalt)
**"Las personas percibirán e interpretarán imágenes ambiguas de la forma más simple posible."**

**Origen:** Principios de la Gestalt (Wertheimer, Köhler, Koffka, 1920s).

**Las 5 leyes de Gestalt más usadas en UX:**

| Ley | Principio | Aplicación |
|---|---|---|
| **Proximidad** | Elementos cercanos se perciben como grupo | Agrupar elementos relacionados con espacio |
| **Similitud** | Elementos similares se perciben como grupo | Color y forma consistentes por categoría |
| **Continuidad** | La mente prefiere líneas y curvas continuas | Flows de lectura y navegación visual |
| **Cierre** | La mente completa formas incompletas | Íconos minimalistas, progress indicators |
| **Figura-Fondo** | La mente distingue elementos del contexto | Contraste, overlays, modales |

---

## 3. Checklist de Leyes — Para Revisión de Diseño

Usar este checklist en revisiones de prototipos o diseños antes de aprobar:

| Ley | Pregunta de verificación | ¿Cumple? |
|---|---|---|
| Hick | ¿El punto de máxima decisión tiene < 7 opciones? | ☐ |
| Fitts | ¿Los CTAs principales son > 44px y están bien posicionados? | ☐ |
| Miller | ¿La información está agrupada en chunks de < 7 elementos? | ☐ |
| Jakob | ¿Se respetan las convenciones del mercado para este tipo de producto? | ☐ |
| Peak-End | ¿El momento de mayor éxito del usuario tiene un diseño memorable? | ☐ |
| Serial Position | ¿Las opciones más importantes van al inicio o al final? | ☐ |
| Tesler | ¿La complejidad inherente fue transferida al sistema, no al usuario? | ☐ |
| Estética | ¿El diseño visual genera confianza en la primera impresión? | ☐ |
| Zeigarnik | ¿Hay indicadores de progreso para tareas incompletas relevantes? | ☐ |
| Gestalt | ¿Los elementos relacionados están agrupados visualmente? | ☐ |

---

## 4. Aplicación directa en el flujo del Mastermind

**Aplica FUENTE-210 para:**
- Justificar o refutar decisiones de diseño con argumentos psicológicos
- Ejecutar el checklist de 10 leyes en cualquier prototipo antes de aprobar
- Priorizar simplificación vs innovación en features específicas (Ley de Jakob + Ley de Tesler)
- Diseñar los momentos clave del flujo (Peak-End Rule + Efecto Zeigarnik)

**Pregunta que activa esta fuente:** "¿Hay una ley psicológica que respalda o contradice esta decisión de diseño?"

---

## 5. Conexiones con otras fuentes del Cerebro #2

- **FUENTE-201 (Norman):** Las leyes de Hick, Fitts y Miller cuantifican los principios conceptuales de Norman
- **FUENTE-202 (Nielsen):** Las leyes proveen el fundamento psicológico de las heurísticas de Nielsen
- **FUENTE-206 (Walter):** El Peak-End Rule es la justificación psicológica del diseño de "momentos humanos" de Walter
- **Todas las fuentes:** Laws of UX actúa como el catálogo de argumentos para justificar o refutar cualquier recomendación del Cerebro #2
