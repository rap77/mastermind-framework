---
id: FUENTE-208
cerebro: 02-ux-research
titulo: Continuous Discovery Habits
autor: Teresa Torres
tipo: libro
isbn: 978-1736633304
edicion: 1st Edition
año: 2021
capa: frameworks + modelos-mentales
experto: Teresa Torres
habilidad: Discovery continuo y Opportunity Solution Tree
tags:
- continuous-discovery
- opportunity-solution-tree
- assumption-testing
- weekly-interviews
- product-thinking
- experiments
version_ficha: '1.0'
fecha_creacion: '2026-02-24'
source_id: FUENTE-208
brain: brain-software-02-ux-research
niche: software-development
title: Continuous Discovery Habits
author: Teresa Torres
type: libro
year: 2021
expert_id: EXP-208
language: en
skills_covered:
- U6
- U8
distillation_date: '2026-02-24'
distillation_quality: complete
loaded_in_notebook: false
version: 1.0.0
last_updated: '2026-02-24'
changelog:
- version: 1.0.0
  date: '2026-02-24'
  changes:
  - Destilación inicial completa
  - Campos estándar de versioning agregados
status: active
---


# FUENTE-208 — Continuous Discovery Habits
**Teresa Torres | Product Talk LLC, 2021**

---

## 1. Por qué esta fuente es indispensable para el Cerebro #2

Torres resuelve el problema que ninguna otra fuente de esta lista aborda directamente: cómo integrar el UX research en el ciclo de trabajo semanal de un equipo de producto, de forma sostenible y sin necesitar un researcher full-time dedicado. Su método convierte el discovery de usuario de "evento especial" a "hábito permanente" — lo que cambia fundamentalmente cómo el Cerebro #2 opera en el tiempo.

---

## 2. El Problema Central

El research tradicional de UX tiene un problema de frecuencia: se hace en fases, con mucho espacio entre iteraciones. El resultado es que los equipos toman decisiones de diseño basadas en research desactualizado o en suposiciones sin validar.

Torres propone cambiar la unidad de tiempo de "proyecto de research" a "hábito semanal".

---

## 3. El Ciclo de Discovery Continuo

### El ritmo mínimo viable de Torres:
- **1 entrevista por semana** con un usuario o cliente real
- Puede ser el PM, el designer, o un engineer — lo que importa es la consistencia
- 30-60 minutos por sesión
- En equipos pequeños: el mismo researcher puede hacer 2-3 semanales

**Por qué funciona:**
- Después de 12 semanas, el equipo tiene 12+ entrevistas acumuladas
- Los patrones emergen naturalmente
- El equipo desarrolla "empatía muscular" — intuición real del usuario, no proyección

---

## 4. El Opportunity Solution Tree (OST)

El OST es la contribución más importante de Torres al campo. Es un framework visual para mapear la relación entre objetivos, oportunidades, soluciones, y experimentos.

### Estructura del OST:

```
[OUTCOME DESEADO]
        │
        ├── [Oportunidad 1]
        │       ├── [Solución 1A]
        │       │       └── [Experimento 1A-1]
        │       └── [Solución 1B]
        │
        ├── [Oportunidad 2]
        │       └── [Solución 2A]
        │               └── [Experimento 2A-1]
        │
        └── [Oportunidad 3]
```

### Definiciones:

**Outcome:** El resultado de negocio/usuario que el equipo quiere lograr (recibido del Cerebro #1)
*Ejemplo: "Aumentar la retención en los primeros 30 días de uso"*

**Oportunidad:** Una necesidad del usuario, pain point, o deseo descubierto en research
*Ejemplo: "Los usuarios no entienden el valor del producto en su primera sesión"*
→ Las oportunidades vienen de entrevistas, no del equipo

**Solución:** Una feature, cambio de diseño, o intervención que aborda la oportunidad
*Ejemplo: "Tour interactivo guiado en el onboarding"*
→ Las soluciones las genera el equipo

**Experimento:** Una prueba rápida para validar que la solución aborda la oportunidad
*Ejemplo: "Prototipo de onboarding de 3 pasos, testear con 5 usuarios"*

### Por qué el OST es poderoso:

**Sin OST (modo típico):** Feature → ¿funcionó? → siguiente feature
**Con OST:** Outcome → Oportunidades → Soluciones múltiples → Experimento → Aprendizaje

El OST fuerza al equipo a considerar múltiples soluciones para cada oportunidad antes de ejecutar, lo que reduce el sesgo hacia la primera idea.

---

## 5. Assumption Mapping (Torres)

Antes de ejecutar un experimento, Torres recomienda mapear las suposiciones que deben ser verdaderas para que la solución funcione.

### Tipos de suposiciones:

**Suposiciones de deseabilidad:** ¿El usuario quiere esto?
**Suposiciones de usabilidad:** ¿Puede el usuario usarlo sin fricción?
**Suposiciones de factibilidad:** ¿Podemos construirlo?
**Suposiciones de viabilidad:** ¿Tiene sentido de negocio?

### Mapa de suposiciones:

```
                    ALTA IMPORTANCIA
                           ↑
  Testear primero  │  Testear inmediatamente
  (crítica + baja  │  (crítica + alta
   certeza)        │   incertidumbre)
                   │
ALTA CERTEZA ──────┼────── BAJA CERTEZA
                   │
  Ignorar por      │  Monitorear
  ahora            │  (baja importancia +
                   │   baja certeza)
                           ↓
                    BAJA IMPORTANCIA
```

**Proceso:**
1. Listar todas las suposiciones necesarias para que la solución funcione
2. Ubicar cada suposición en el mapa
3. Testear primero las del cuadrante "crítica + alta incertidumbre"
4. El experimento tiene como objetivo reducir la incertidumbre de la suposición más crítica

---

## 6. Entrevistas de Discovery (Torres)

Torres adapta el método de entrevistas al contexto de discovery continuo. No son entrevistas de usabilidad ni de prototipo — son entrevistas de "experiencia reciente".

### Estructura de entrevista de Torres:

**Warm-up (5 min):**
- Contexto del usuario: qué hace, cuál es su rol respecto al producto
- No hablar del producto todavía

**Story collection (20-30 min):**
- "Cuéntame sobre la última vez que [hiciste X]"
- Objetivo: obtener una historia completa y específica de un evento reciente
- Explorar el contexto, el proceso, las herramientas usadas, los momentos de fricción
- Seguir los hilos del usuario, no el guión

**Síntesis (5-10 min):**
- "¿Hay algo más de esa experiencia que no te pregunté?"
- Confirmar comprensión de los puntos clave

**Cierre:**
- "¿Puedo contactarte de nuevo si tengo preguntas?"

### Lo que Torres NO recomienda:
- Mostrar el producto en entrevistas de discovery
- Pedir feedback de features en entrevistas de discovery
- Hacer preguntas sobre características o funcionalidades deseadas

---

## 7. Story Mapping de Oportunidades

Torres propone que después de cada sesión de entrevistas, el equipo mapee las oportunidades descubiertas en el OST.

**Proceso post-entrevista:**
1. Identificar las necesidades, pain points, y deseos mencionados
2. Formularlos como oportunidades (desde la perspectiva del usuario, no del equipo)
3. Ubicarlos en el OST debajo del outcome correspondiente
4. Identificar qué oportunidades aparecen con mayor frecuencia
5. Priorizar las oportunidades más frecuentes + más cercanas al outcome deseado

---

## 8. Experimentos Rápidos (Torres)

Torres clasifica los experimentos por costo y confiabilidad:

| Tipo de Experimento | Costo | Confiabilidad | Cuándo usar |
|---|---|---|---|
| Entrevista con concepto | Muy bajo | Media | Validar si la oportunidad es real |
| Prototipo en papel | Bajo | Media-baja | Validar dirección de solución |
| Prototipo clickeable | Medio | Media-alta | Validar usabilidad de la solución |
| Feature flag / A/B test | Alto | Alta | Validar impacto en el outcome |
| Concierge / Wizard of Oz | Bajo | Media | Validar demanda antes de construir |

**Regla de Torres:** Empezar con el experimento de menor costo que reduzca la incertidumbre suficiente para avanzar. No sobrevaluar la "confiabilidad perfecta".

---

## 9. El Ritmo del Discovery Continuo en el Mastermind

Torres define el ritmo semanal ideal de un equipo que practica discovery continuo:

| Actividad | Frecuencia | Quién |
|---|---|---|
| Entrevista de usuario | 1-3 por semana | PM, Designer, o Engineer rotando |
| Actualizar OST | Semanalmente post-entrevista | PM + Designer |
| Priorizar oportunidades | Quincenalmente | Equipo completo |
| Generar y votar soluciones | Por ciclo de sprint | Equipo completo |
| Diseñar experimento | Antes de codificar | Designer + PM |
| Revisar suposiciones | Antes de sprint | PM |

---

## 10. Conexión con el Cerebro #1

Torres es el puente natural entre el Cerebro #1 (Product Strategy) y el Cerebro #2:

- El **outcome** del OST proviene del Cerebro #1 (propuesta de valor, OKRs, Jobs-to-be-Done)
- Las **oportunidades** emergen del Cerebro #2 (entrevistas de usuario)
- Las **soluciones** son input para el Cerebro #3 (UI Design) y Cerebro #4 (Frontend)
- Los **experimentos** se miden con el Cerebro #7 (Growth & Data)

---

## 11. Aplicación directa en el flujo del Mastermind

**Aplica FUENTE-208 para:**
- Estructurar el ciclo semanal de discovery del equipo
- Construir el OST como herramienta central de priorización de oportunidades
- Convertir insights de entrevistas en oportunidades mapeadas al outcome del negocio
- Diseñar experimentos antes de comprometerse a construir features completas
- Mapear suposiciones críticas de cualquier feature antes de diseñarla

**Pregunta que activa esta fuente:** "¿Cómo convertimos el research en un hábito, no en un evento?"

---

## 12. Conexiones con otras fuentes del Cerebro #2

- **FUENTE-204 (Young):** Torres adapta el método de entrevistas de Young a un ciclo semanal
- **FUENTE-207 (Fitzpatrick):** Las reglas de entrevista de Fitzpatrick aplican directamente a las sesiones de Torres
- **FUENTE-205 (Hall):** Hall define cuándo usar qué método; Torres define la cadencia operativa de uso
