---
source_id: "FUENTE-314"
brain: "brain-software-03-ui-design"
niche: "software-development"
title: "Color in UI Design — Guía Consolidada de Psicología del Color y Sistemas"
author: "Compilación: Josef Albers (Interaction of Color) + Material Design Color System + UX Color Research"
expert_id: "EXP-314"
type: "guide"
language: "es"
year: 2024
url: "https://m3.material.io/styles/color/system"
skills_covered: ["H2", "H4"]
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
      - "Cubre gap de Psicología del Color no documentado en v1.0"
status: "active"

# Metadatos específicos del Cerebro #3
habilidad_primaria: "Psicología del Color & Color Systems para UI"
habilidad_secundaria: "Paletas Semánticas, Emoción & Comunicación Visual"
capa: 1
capa_nombre: "Base Conceptual — Color"
relevancia: "CRÍTICA — El color es la primera variable visual que el usuario procesa"
---

# FUENTE-314 — Color in UI Design
## Psicología del Color + Color Systems para Interfaces

---

## Tesis Central

> El color es el elemento visual más potente y más peligroso del diseño de interfaces. Comunica emoción antes que lógica, establece jerarquía sin palabras, y puede reforzar o destruir la confianza del usuario en segundos. Un sistema de color bien diseñado es invisible; un sistema roto grita.

La primera pregunta de color no es "¿qué colores me gustan?" sino "¿qué debe sentir y entender el usuario cuando ve esta interfaz?"

---

## Principios Fundamentales

### Principio 1 — El Color Tiene Semántica, no Solo Estética

Los colores comunican significados que el usuario ya aprendió antes de abrir tu producto.

**Asociaciones culturales occidentales (contexto digital):**
| Color | Asociaciones positivas | Asociaciones negativas | Uso en UI |
|-------|----------------------|----------------------|-----------|
| Azul | Confianza, seguridad, calma, tecnología | Frialdad, distancia | Fintech, SaaS B2B, salud |
| Verde | Éxito, salud, crecimiento, dinero | — | Estados de éxito, salud, finanzas |
| Rojo | Urgencia, energía, pasión | Error, peligro, deuda | Alertas, errores, CTAs de alta urgencia |
| Naranja | Energía, creatividad, accesibilidad | Impulsivo, barato | CTAs secundarios, notificaciones |
| Amarillo | Optimismo, atención, calor | Advertencia, ansiedad | Warnings, highlights |
| Morado | Lujo, creatividad, innovación | Misterio, rareza | Tech premium, creativos |
| Negro | Sofisticación, poder, elegancia | Muerte, opresión | Productos premium, editorial |
| Blanco | Limpieza, simplicidad, espacio | Vacío, frío | Fondos, espacios negativos |

**Advertencia:** Las asociaciones culturales varían. Rojo = suerte en China. Blanco = duelo en algunas culturas asiáticas. En productos globales, verificar el contexto cultural del mercado objetivo.

### Principio 2 — La Regla 60-30-10

La distribución clásica de color en cualquier composición:

```
60% — Color dominante/fondo
      → El color de la mayoría del espacio en la interfaz
      → Generalmente neutro (blanco, gris claro, dark)
      → Define el "ambiente" del producto

30% — Color secundario
      → Superficies, cards, navegación
      → Puede ser un neutro levemente tonalizado
      → Complementa sin competir

10% — Color de acento
      → CTAs, links, estados activos, highlights
      → EL color de marca
      → Su rareza lo hace poderoso; si está en todo, pierde fuerza
```

**Error común:** Usar el color de marca como fondo. El color de marca debe ser el 10%, no el 60%. Cuando es fondo, deja de tener poder de atención.

### Principio 3 — La Teoría de Albers: el Color es Relativo

El mismo color parece diferente dependiendo del contexto. Un gris sobre blanco parece oscuro; el mismo gris sobre negro parece claro.

**Implicaciones para UI:**
- Verificar el contraste siempre en contexto (no en aislamiento)
- El color de texto sobre fondo de color puede necesitar ajuste aunque el hex sea el mismo
- Los colores de "marca" establecidos en branding no siempre funcionan igual en pantalla digital

### Principio 4 — La Paleta Funcional (más allá del brand color)

Una paleta de UI completa incluye:

```
COLOR PRIMARIO (brand)
  → Primary: el color de acción
  → Primary-container: fondo suave del mismo matiz (para chips, tags, badges)
  → On-primary: texto/íconos sobre primary
  → On-primary-container: texto/íconos sobre primary-container

COLOR SECUNDARIO
  → Para elementos de soporte que no compiten con primary

COLOR TERCIARIO
  → Tercer color para destacar categorías o elementos especiales

COLORES NEUTROS
  → Background: fondo principal
  → Surface: cards, sheets, modals
  → Surface-variant: variación de surface
  → Outline: bordes y separadores

COLORES DE ESTADO (semánticos, no de marca)
  → Error: rojo (nunca el color de marca)
  → Warning: amarillo/naranja
  → Success: verde
  → Info: azul

CADA COLOR tiene sus versiones "on-" (para texto encima) y "-container" (versión pastel para fondos)
```

### Principio 5 — Temperatura y Peso Visual del Color

**Temperatura:**
- Colores cálidos (rojo, naranja, amarillo) parecen avanzar hacia el usuario
- Colores fríos (azul, verde, morado) parecen retroceder

**Aplicación en jerarquía visual:**
- Los elementos importantes pueden tener color cálido o saturado para "avanzar"
- Los fondos y elementos secundarios usan colores fríos o neutros para "retroceder"

**Peso visual:**
- Los colores oscuros pesan más visualmente
- Los colores saturados pesan más que los desaturados
- Un pequeño elemento oscuro/saturado equilibra un área grande clara/desaturada

---

## Framework — Construcción de Paleta para UI

### Paso 1: El Color Primario

Partiendo del color de marca, generar la escala tonal:

```
ESCALA TONAL (Material Design 3 approach):
  Tono 0:   Negro puro (#000000)
  Tono 10:  Muy oscuro (para fondos dark, text on containers)
  Tono 20:  Oscuro (primary en dark mode)
  Tono 30:  Oscuro-medio
  Tono 40:  PRIMARY EN LIGHT MODE
  Tono 50:  Medio
  Tono 60:  Medio-claro
  Tono 70:  Claro
  Tono 80:  PRIMARY EN DARK MODE (claro, menos saturado)
  Tono 90:  Muy claro (primary-container en light mode)
  Tono 95:  Casi blanco
  Tono 99:  Casi blanco puro
  Tono 100: Blanco puro

→ Herramienta: Material Theme Builder (m3.material.io/theme-builder)
→ O en Figma: Plugin "Material Theme Builder"
```

### Paso 2: La Paleta Neutral

Los neutros no son grises puros. Los mejores neutrales están levemente tonalizados con el color primario (≈5% de saturación del primario).

```
NEUTRAL CORRECTAMENTE TONALIZADO:
  Si primario es azul → neutros con leve tono frío/azulado
  Si primario es rojo-naranja → neutros con leve tono cálido

Resultado: La interfaz se siente cohesiva y "diseñada", no ensamblada.
```

### Paso 3: Los Colores de Estado

**Nunca usar el color primario como color de error o éxito.** Los colores de estado son semánticos y universales:

```
Error:   Rojo. Matiz recomendado: #B00020 (light) / #CF6679 (dark)
Success: Verde. Matiz recomendado: #1B5E20 (light) / #4CAF50 (dark)
Warning: Ámbar. Matiz recomendado: #E65100 (light) / #FFB74D (dark)
Info:    Azul. Solo si el primario no es azul. Si el primario es azul,
         usar un azul levemente diferente o un cyano.
```

### Paso 4: Verificación de Contraste

Para cada combinación texto/fondo en la paleta:

```
herramienta: who.is/color/contrast-checker
            webaim.org/resources/contrastchecker/

VERIFICAR:
☐ color.on-primary sobre color.primary: ≥ 4.5:1
☐ color.on-background sobre color.background: ≥ 4.5:1
☐ color.on-surface sobre color.surface: ≥ 4.5:1
☐ color.on-error sobre color.error: ≥ 4.5:1
☐ color.on-primary-container sobre color.primary-container: ≥ 4.5:1
☐ Texto secundario (muted): ≥ 4.5:1 (aunque sea texto pequeño)
☐ Placeholder text: ≥ 4.5:1 (error común: placeholders con bajo contraste)
```

---

## Modelos Mentales

### "El Color que Grita Pierde su Voz"

Si el color de acento está en 30% de la interfaz, ya no es acento — es ruido. La atención del usuario se distribuye igual en todo y el llamado a la acción pierde efectividad.

El color de acento (primario, el de marca) debería hacer al usuario pensar "¿debo hacer clic aquí?". Para que eso funcione, debe ser raro.

### "El Neutro es el Héroe Invisible"

Los mejores diseños tienen 70-80% de colores neutros perfectamente elegidos. Los neutros son la estructura; el color es la decoración. Cuando los neutros están bien, el color de acento brilla. Cuando los neutros están mal (demasiado fríos, demasiado cálidos, sin cohesión), el acento no puede salvarlos.

### "Nunca Confíes en Tu Monitor"

Los colores se ven diferente en distintos monitores (sRGB vs P3), en móvil vs desktop, bajo luz solar vs interior. Los colores calibrados en un monitor Apple Display P3 pueden verse lavados en un monitor económico.

**Regla práctica:** Verificar la paleta en al menos 3 dispositivos diferentes antes de aprobarla.

---

## Criterios de Decisión

### ¿Cuántos colores en una pantalla?

```
Fondos y superficies: 2-3 colores neutros
Color de marca (acento): 1 color (máximo 2 si hay secundario)
Estados (error, éxito, warning): Solo cuando aplica
→ Total percibido: 3-4 colores distintos por pantalla (excluir neutrales)
→ Si hay más: revisar si todos son necesarios
```

### ¿Cuándo usar color en texto?

```
✅ Links (siempre con underline también)
✅ Estados activos en navegación
✅ Datos positivos/negativos en dashboards (+ verde, - rojo)
❌ Texto de contenido general (afecta legibilidad y parece spam)
❌ Texto de UI sin función específica
```

---

## Anti-Patrones de Color

**ACO-01 — Color primario como fondo principal**
La marca azul como fondo de toda la interfaz → el azul pierde poder de acción y la interfaz se vuelve visualmente agotadora.

**ACO-02 — Grises sin tonalizar**
Neutrales de gris puro (#808080) junto a primarios de color producen interfaces frías e incoherentes. Los grises deben tener leve tono del primario.

**ACO-03 — 4+ colores de acento en una pantalla**
Cada color de acento compite por atención. El resultado: el usuario no sabe qué es lo más importante.

**ACO-04 — Mismo color para error y para acción primaria**
Si el CTA y el estado de error son el mismo rojo, el usuario aprende a ignorar el rojo o siente ansiedad al ver el CTA.

**ACO-05 — Colores de estado solo como fondo sin texto explicativo**
Un fondo rojo sin texto que explique qué falló es inaccesible para usuarios con daltonismo y ambiguo para todos.

**ACO-06 — Placeholder text con bajo contraste**
Los placeholders grises claros casi siempre fallan el test de contraste WCAG 4.5:1. Son texto, no decoración.

---

## Conexión con el Cerebro #3

| Habilidad del Cerebro #3 | Aporte de esta fuente |
|--------------------------|----------------------|
| Construcción de paleta | Framework completo: primario, neutros, estados, escalas tonales |
| Semántica del color | Qué comunica cada color y cuándo usarlo |
| Regla 60-30-10 | Distribución correcta de color en composición |
| Integración con dark mode | Base para entender FUENTE-311 |
| Contraste y accesibilidad | Checklist de verificación de contraste por token |

## Preguntas que el Cerebro #3 puede responder con esta fuente

1. ¿Este color de marca transmite la emoción correcta para este producto?
2. ¿Cuántos colores de acento debería tener esta interfaz?
3. ¿Cómo construyo la escala tonal de este color primario?
4. ¿Por qué los neutrales se ven "apagados" junto al primario?
5. ¿El color de éxito debe ser el mismo en toda la plataforma?
6. ¿Cómo distribuyo el color en esta pantalla para que el CTA tenga más impacto?
