---
id: FUENTE-203
cerebro: 02-ux-research
titulo: Don't Make Me Think, Revisited
autor: Steve Krug
tipo: libro
isbn: 978-0321965516
edicion: 3rd Edition
año: 2014
capa: base-conceptual + frameworks
experto: Steve Krug
habilidad: Simplificación UX y testing pragmático
tags:
- cognitive-load
- scanning
- web-usability
- guerrilla-testing
- simplicity
- conventions
version_ficha: '1.0'
fecha_creacion: '2026-02-24'
source_id: FUENTE-203
brain: brain-software-02-ux-research
niche: software-development
title: Don't Make Me Think, Revisited
author: Steve Krug
type: libro
year: 2014
expert_id: EXP-203
language: en
skills_covered:
- U2
- U3
- U7
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



# FUENTE-203 — Don't Make Me Think, Revisited
**Steve Krug | New Riders, 2014 (3rd Ed.)**

---

## 1. Por qué esta fuente es indispensable para el Cerebro #2

Krug traduce los principios de Norman y Nielsen al lenguaje de equipos reales con recursos limitados. Su aportación central es doble: (1) el principio del mínimo esfuerzo cognitivo como norte de diseño, y (2) el testing de usabilidad accesible para cualquier equipo. Es la fuente más accionable del Cerebro #2 para equipos que no tienen un UX researcher full-time.

---

## 2. El Principio Central

> **"Don't make me think."**

El principio: cada vez que el usuario se detiene a preguntarse "¿qué hace esto?" o "¿dónde estoy?", la experiencia falló. El objetivo del diseño es eliminar todos los signos de interrogación que aparecen en la cabeza del usuario.

**El costo de cada signo de interrogación:**
- Consume carga cognitiva
- Aumenta la fatiga de uso
- Incrementa la tasa de abandono
- Destruye la confianza en el producto

---

## 3. Conceptos Maestros

### 3.1 Cómo leen los usuarios (realmente)
Los usuarios NO leen páginas — las escanean. Buscan lo que coincide con su tarea actual e ignoran el resto.

**Comportamiento real del usuario:**
- Escanea hasta encontrar algo razonablemente bueno (no lo óptimo)
- Hace clic en el primer link que parece relevante
- Si se equivoca, presiona Back sin leer el error
- No lee instrucciones — hace prueba y error

**Implicación de diseño:** Diseñar para el escaneo, no para la lectura. Jerarquía visual clara. Párrafos cortos. Headers descriptivos. Bullets donde corresponda.

### 3.2 Satisficing
Los usuarios no optimizan — "satisfacen" (combinación de satisfy + suffice). Toman la primera opción que parece razonablemente buena, no la mejor.

**Implicación:** El diseño no debe asumir que el usuario leerá todas las opciones antes de elegir. La primera opción visible tiene una ventaja injusta. Las opciones más importantes deben ir primero y ser más prominentes.

### 3.3 Convenciones UX — Por qué no innovar en lo básico
Las convenciones son los patrones de interacción que los usuarios aprendieron en otros productos. Violarlas genera fricción incluso si la alternativa es "mejor" en abstracto.

**Convenciones que Krug recomienda respetar siempre:**
- Logo en esquina superior izquierda (vuelve al home)
- Navegación principal en la parte superior o lateral izquierda
- Links subrayados o en color diferente
- Botón de búsqueda a la derecha del campo de búsqueda
- Carrito de compras en la esquina superior derecha

**Regla de Krug:** "Si vas a romper una convención, asegúrate de que el beneficio sea tan obvio y grande que valga el costo de aprendizaje."

### 3.4 Jerarquía Visual Clara
El usuario debe poder entender la estructura y jerarquía de la página en menos de 2 segundos de escaneo.

**Checklist de jerarquía visual:**
- [ ] ¿Es obvio cuál es el elemento más importante de la página?
- [ ] ¿Están agrupados los elementos relacionados?
- [ ] ¿El tamaño relativo refleja la importancia relativa?
- [ ] ¿Hay contraste suficiente entre niveles de jerarquía?
- [ ] ¿Está claro qué es clickeable y qué no?

### 3.5 Ruido vs Información
Krug introduce el concepto de "happy talk" y ruido visual que debe eliminarse:

**Happy talk (eliminar):**
- Texto introductorio que no dice nada ("Bienvenido a nuestra plataforma...")
- Instrucciones obvias ("Haga clic en el botón para continuar")
- Descripciones de features que el usuario no pidió

**Regla de la mitad:** Krug recomienda tomar cualquier bloque de texto y reducirlo a la mitad. Si la mitad sigue funcionando, reducir a la mitad nuevamente. El texto que sobrevive es el que debe estar.

### 3.6 Diseño de Navegación
La navegación debe responder en todo momento a 3 preguntas:
1. ¿Dónde estoy?
2. ¿Qué hay aquí?
3. ¿A dónde puedo ir?

**Elementos de navegación mínimos:**
- Indicador de ubicación actual (breadcrumb o estado activo en menú)
- Navegación principal siempre visible
- Nombre de la página actual claramente visible
- Logo clickeable que regresa al home

### 3.7 La Importancia del Trunk Test
Krug propone el "Trunk Test": imagina que llegaste a una página sin ver ninguna otra parte del sitio. ¿Puedes responder estas preguntas?

1. ¿Qué sitio/app es este?
2. ¿En qué página estoy?
3. ¿Cuáles son las secciones principales de este sitio?
4. ¿Qué opciones tengo en este nivel?
5. ¿Dónde estoy en el esquema del sitio?
6. ¿Cómo puedo buscar?

**Uso del Trunk Test en el #2:** Aplicarlo a cualquier pantalla nueva que llegue del Cerebro #3 antes de aprobarla.

---

## 4. Testing de Usabilidad según Krug

### 4.1 Filosofía del "Guerrilla Testing"
Krug democratizó el testing de usabilidad. Su argumento: hacer testing imperfecto regularmente vale infinitamente más que hacer testing perfecto raramente (o nunca).

**Formato mínimo viable de testing:**
- 3 usuarios por ronda (no 5, no 8 — 3 es suficiente para encontrar los problemas mayores)
- 1-2 horas de sesión total incluyendo análisis
- 1 moderador + 1 observador (mínimo)
- Puede hacerse en café, en remoto, donde sea

### 4.2 Protocolo de Sesión de Testing (Krug simplificado)

**Antes (5 min):**
> "Vamos a ver algunas páginas del sitio. No estás siendo evaluado tú — estamos evaluando el diseño. No hay respuestas incorrectas. Por favor piensa en voz alta."

**Durante la tarea:**
- No ayudar NUNCA aunque el usuario esté frustrado
- Anotar dónde se detiene, dónde duda, qué dice
- Registrar lo que hace, no lo que dice que haría

**Preguntas permitidas:**
- "¿Qué estás pensando en este momento?"
- "¿Qué esperabas que pasara?"
- NO: "¿Te gustó?" / "¿Qué mejorarías?"

### 4.3 Análisis Post-Testing (Krug)
No hacer análisis estadístico — hacer lista de problemas por prioridad.

**Proceso:**
1. Listar todos los problemas observados
2. Identificar los 3 problemas más críticos (los que bloquearon el flujo completo)
3. Iterar diseño enfocado en esos 3
4. No intentar resolver todo — resolver lo crítico y volver a testear

### 4.4 Testing Remoto No Moderado
Krug en la 3ra edición añade herramientas de testing remoto:
- UserTesting.com para sesiones asíncronas
- Lookback.io para moderadas
- Maze para testing de prototipos sin moderador

---

## 5. Accesibilidad como Usabilidad

Krug argumenta que la accesibilidad no es una feature adicional — es la prueba más exigente de usabilidad. Si funciona para alguien con discapacidad visual o motora, funciona mejor para todos.

**Checklist mínimo de accesibilidad (Krug):**
- [ ] ¿Todas las imágenes tienen alt text descriptivo?
- [ ] ¿Se puede navegar todo con teclado?
- [ ] ¿El contraste de color supera 4.5:1 (WCAG AA)?
- [ ] ¿Los formularios tienen labels explícitos (no solo placeholder)?
- [ ] ¿Los videos tienen subtítulos?

---

## 6. Mobile UX (Adición de la 3ra Edición)

Krug adapta sus principios al contexto mobile:

**Diferencias críticas en mobile:**
- La pantalla pequeña hace el "don't make me think" aún más urgente
- El usuario está en contexto de distracción (movilidad, multitarea)
- Los dedos son menos precisos que el cursor — targets mínimo 44x44px
- La carga cognitiva extra de pantallas pequeñas cuesta más

**Principio mobile de Krug:** "Todo lo que ya era difícil en desktop, en mobile es imposible. Diseñar mobile primero revela qué es realmente esencial."

---

## 7. Señales de Alarma — Checklist del #2

Cualquier "sí" en esta lista es una violación del principio de Krug:

- [ ] ¿El usuario tuvo que leer para entender cómo interactuar?
- [ ] ¿Hubo un momento de duda visible ("¿dónde está...?")?
- [ ] ¿El usuario hizo clic en algo incorrecto en el flujo principal?
- [ ] ¿Hay texto que explica cómo usar la UI?
- [ ] ¿La navegación requiere memorizar dónde está algo?
- [ ] ¿El usuario preguntó "¿ya terminé?"?

---

## 8. Aplicación directa en el flujo del Mastermind

**Aplica FUENTE-203 para:**
- Trunk Test en cada pantalla nueva antes de aprobar
- Organizar rondas de guerrilla testing de 3 usuarios cuando hay prototipos
- Reducir "happy talk" y ruido visual en cualquier UI review
- Verificar que la jerarquía visual es escaneable en < 2 segundos

**Pregunta que activa esta fuente:** "¿Este diseño obliga al usuario a pensar?"

---

## 9. Conexiones con otras fuentes del Cerebro #2

- **FUENTE-201 (Norman):** Krug es Norman aplicado al contexto web/app con pragmatismo
- **FUENTE-202 (Nielsen):** Krug simplifica el testing de Nielsen para equipos sin recursos
- **FUENTE-204 (Young):** Mientras Young profundiza en empatía, Krug provee el testing rápido para validar
