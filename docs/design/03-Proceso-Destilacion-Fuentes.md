# Proceso de Destilación de Fuentes — MasterMind Framework

## Objetivo

Definir **cómo extraer el conocimiento esencial** de cada fuente (libro, video, documento) para ingestarlo en un cerebro. No se carga el libro completo. Se destilan principios, frameworks, patrones, y criterios de decisión.

---

## Principio Fundamental

> **Destila principios, no información masiva.**
> Un cerebro alimentado con 5 libros completos tiene ruido.
> Un cerebro alimentado con los 50 principios destilados de esos 5 libros tiene criterio.

---

## Tipos de Fuentes y Tratamiento

| Tipo | Formato Original | Proceso de Destilación | Output |
|------|-----------------|----------------------|--------|
| **Libro** | PDF, EPUB, físico | Lectura → Extracción → Ficha | Ficha Fuente Maestra (.md) |
| **Video/Charla** | YouTube, curso online | Visualización → Notas → Ficha | Ficha Fuente Maestra (.md) |
| **Artículo/Blog** | URL, texto | Lectura → Síntesis → Ficha | Ficha Fuente Maestra (.md) |
| **Documentación técnica** | Web, PDF | Extracción de patrones → Ficha | Ficha Fuente Maestra (.md) |

**Todas las fuentes terminan en el mismo formato:** Ficha de Fuente Maestra (ver plantilla en `04-Plantilla-Ficha-Fuente-Maestra.md`).

---

## Proceso de Destilación (Paso a Paso)

### Paso 1: Identificar qué buscar

Antes de leer/ver la fuente, definir:

- ¿Qué **habilidad** del cerebro cubre esta fuente?
- ¿Qué tipo de conocimiento necesito extraer?
  - Principios fundamentales
  - Frameworks o metodologías
  - Patrones recurrentes
  - Criterios de decisión (trade-offs)
  - Anti-patrones (qué NO hacer)
  - Casos reales (ejemplos)

### Paso 2: Consumir la fuente con foco

No se lee "todo el libro". Se buscan específicamente:

**Para LIBROS:**
- Tabla de contenido → identificar capítulos relevantes
- Introducción y conclusión → capturar tesis principal
- Capítulos clave → extraer frameworks y principios
- Ignorar: anécdotas extendidas, contexto histórico irrelevante, repeticiones

**Para VIDEOS:**
- Primeros 2 minutos → ¿cuál es la promesa?
- Buscar momentos de "framework" → cuando el experto estructura una idea
- Buscar momentos de "criterio" → cuando dice "la mayoría hace X pero debería hacer Y"
- Ignorar: introducciones largas, promociones, contenido de relleno

**Para ARTÍCULOS:**
- Leer completo (suelen ser cortos)
- Extraer la idea central y las recomendaciones prácticas

### Paso 3: Extraer en las 6 categorías

De cada fuente, extraer y organizar en:

```
1. PRINCIPIOS FUNDAMENTALES
   Lo que el experto considera verdades universales de su campo.
   Formato: Afirmación clara + contexto breve.

2. FRAMEWORKS Y METODOLOGÍAS
   Procesos estructurados que el experto propone.
   Formato: Nombre del framework + pasos + cuándo usarlo.

3. MODELOS MENTALES
   Formas de pensar que el experto recomienda.
   Formato: Nombre del modelo + cómo aplicarlo.

4. CRITERIOS DE DECISIÓN
   Cómo el experto resuelve trade-offs.
   Formato: "Cuando [situación], prioriza [A] sobre [B] porque [razón]"

5. ANTI-PATRONES
   Lo que el experto dice que NO se debe hacer.
   Formato: "No hagas [X] porque [consecuencia]"

6. CASOS Y EJEMPLOS REALES
   Ejemplos que ilustran los principios en acción.
   Formato: Empresa/situación → decisión → resultado
```

### Paso 4: Validar la extracción

Antes de crear la ficha, verificar:

- [ ] ¿Cada principio extraído es accionable (se puede aplicar)?
- [ ] ¿Los frameworks tienen pasos claros?
- [ ] ¿Los criterios de decisión son específicos, no genéricos?
- [ ] ¿Se identificó al menos 1 anti-patrón?
- [ ] ¿Hay al menos 1 caso real?
- [ ] ¿El conocimiento extraído cubre la habilidad objetivo?

### Paso 5: Crear la Ficha de Fuente Maestra

Usar la plantilla `04-Plantilla-Ficha-Fuente-Maestra.md`.

### Paso 6: Cargar en NotebookLM

- Subir la Ficha como fuente al cuaderno del cerebro correspondiente
- Verificar que NotebookLM puede hacer preguntas sobre el contenido
- Probar 3 consultas de prueba para validar retrieval

---

## Ejemplo Aplicado: Destilación de "Inspired" de Marty Cagan

### Paso 1: Habilidades objetivo
- H1: Visión de negocio
- H3: Roadmap y priorización
- H5: Comunicación y stakeholders

### Paso 3: Extracción

**Principios Fundamentales:**
- Los mejores equipos de producto hacen discovery y delivery en paralelo, no en secuencia
- El rol del PM es descubrir un producto que sea valioso, usable, factible, y viable para el negocio
- Los outputs (features) no son lo mismo que outcomes (resultados)

**Frameworks:**
- Product Discovery: 4 riesgos a validar (valor, usabilidad, factibilidad, viabilidad)
- Opportunity Assessment: responder antes de construir si hay mercado real
- Empowered Teams: equipos con autonomía para resolver problemas, no para ejecutar features

**Criterios de Decisión:**
- Cuando debas elegir: prioriza riesgo de valor sobre riesgo técnico
- Cuando stakeholders presionen: muestra datos de discovery, no opiniones
- Cuando el roadmap esté lleno: prioriza outcomes sobre outputs

**Anti-patrones:**
- No ser un "feature team" (equipo que solo ejecuta lo que otros deciden)
- No confundir product manager con project manager
- No hacer roadmaps de features; hacer roadmaps de problemas a resolver

**Caso Real:**
- Netflix: equipos empoderados que prueban hipótesis continuamente, no esperan aprobación ejecutiva para cada cambio

---

## Calidad mínima de una Ficha

Una ficha se considera completa cuando tiene:

| Sección | Mínimo requerido |
|---------|-----------------|
| Principios | 3 o más |
| Frameworks | 1 o más |
| Modelos mentales | 1 o más |
| Criterios de decisión | 2 o más |
| Anti-patrones | 1 o más |
| Casos reales | 1 o más |

Si una fuente no alcanza estos mínimos, probablemente no es lo suficientemente rica para ser fuente maestra y debería ser complementaria.
