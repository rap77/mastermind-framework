# Método de Selección de Expertos — MasterMind Framework

## Objetivo

Definir un proceso riguroso y replicable para elegir qué profesionales expertos mundiales alimentan cada cerebro, garantizando que se cubran **todas las habilidades necesarias sin dejar gaps**.

---

## Criterios de Selección Obligatorios

Un experto debe cumplir **mínimo 4 de los 6 criterios** para ser incluido:

| # | Criterio | Descripción | Cómo se verifica |
|---|----------|-------------|-----------------|
| C1 | **Reconocimiento mundial** | Es referente en su campo a nivel internacional | Publicaciones citadas, conferencias internacionales, premios |
| C2 | **Obra publicada accesible** | Tiene libros, cursos, o contenido estructurado disponible | ISBN verificable, curso en plataforma reconocida, canal activo |
| C3 | **Experiencia práctica demostrable** | Ha aplicado sus conocimientos en empresas/proyectos reales | Casos documentados, empresas nombradas, resultados medibles |
| C4 | **Cobertura de habilidad específica** | Cubre al menos 1 habilidad del knowledge-map del cerebro | Mapeo directo habilidad → experto |
| C5 | **Actualización reciente** | Ha publicado contenido relevante en los últimos 5 años | Última publicación verificable |
| C6 | **Conocimiento destilable** | Su conocimiento puede extraerse en principios, frameworks, y patrones accionables | Revisión de contenido: tiene estructura clara, no solo narrativa |

---

## Proceso de Selección (Paso a Paso)

### Paso 1: Mapear habilidades del cerebro

Del `knowledge-map.md` del cerebro, listar todas las habilidades requeridas.

### Paso 2: Investigación inicial

Para cada habilidad, buscar:
- Los 5-10 autores más citados en esa área
- Los libros más vendidos/recomendados
- Las conferencias y charlas más vistas
- Las comunidades profesionales de referencia

### Paso 3: Evaluar contra los 6 criterios

Para cada candidato, llenar esta matriz:

| Candidato | C1 | C2 | C3 | C4 | C5 | C6 | Score | ¿Incluir? |
|-----------|----|----|----|----|----|----|-------|-----------|
| {Nombre} | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | 5/6 | Sí |
| {Nombre} | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | 3/6 | No |

### Paso 4: Verificar cobertura completa

Cruzar la lista de expertos seleccionados contra el knowledge-map:
- ¿Toda habilidad tiene al menos 1 experto asignado?
- ¿Las habilidades críticas tienen al menos 2 expertos (redundancia)?
- ¿Hay gaps sin cubrir?

### Paso 5: Cerrar gaps

Si hay habilidades sin experto:
1. Ampliar búsqueda a otros idiomas/regiones
2. Considerar expertos emergentes (menor reconocimiento pero alto C3 y C6)
3. Buscar fuentes alternativas (papers académicos, documentación oficial)
4. Documentar el gap y el plan de cierre

### Paso 6: Documentar en experts-directory.md

Llenar la ficha de cada experto seleccionado usando la plantilla del documento `01-Plantilla-Cerebro.md`.

---

## Reglas Adicionales

- **Mínimo 4, máximo 8 expertos por cerebro.** Menos de 4 genera gaps. Más de 8 genera ruido y redundancia.
- **Diversidad de perspectivas:** No seleccionar expertos que digan exactamente lo mismo. Buscar complementariedad.
- **Priorizar practitioners sobre teóricos:** Un experto que ha construido productos > un académico que solo investiga.
- **Los expertos no se eligen por popularidad sino por cobertura de habilidades.** Un autor menos conocido puede cubrir un gap que ningún bestseller cubre.
- **Cada experto debe tener al menos 1 fuente maestra procesable** (libro con ISBN, video con URL, o documento accesible).

---

## Ejemplo Aplicado: Cerebro #1 (Product Strategy)

### Habilidades a cubrir:

| # | Habilidad | Nivel |
|---|-----------|-------|
| H1 | Visión de negocio y definición de problema | Experto |
| H2 | Research de mercado y validación | Avanzado |
| H3 | Roadmap estratégico y priorización | Experto |
| H4 | Métricas (KPIs, OKRs) | Avanzado |
| H5 | Comunicación y gestión de stakeholders | Avanzado |
| H6 | Pensamiento sistémico | Avanzado |
| H7 | Comprensión técnica básica | Intermedio |
| H8 | Product-Market Fit y economía unitaria | Experto |

### Matriz de evaluación aplicada:

| Experto | C1 | C2 | C3 | C4 (habilidades) | C5 | C6 | Score | Decisión |
|---------|----|----|----|----|----|----|-------|----------|
| Marty Cagan | ✅ | ✅ | ✅ | H1,H3,H5,H7 | ✅ | ✅ | 6/6 | ✅ Incluido |
| Teresa Torres | ✅ | ✅ | ✅ | H2,H4 | ✅ | ✅ | 6/6 | ✅ Incluido |
| Melissa Perri | ✅ | ✅ | ✅ | H1,H3,H8 | ✅ | ✅ | 6/6 | ✅ Incluido |
| Eric Ries | ✅ | ✅ | ✅ | H2,H8 | ❌ | ✅ | 5/6 | ✅ Incluido |
| John Doerr | ✅ | ✅ | ✅ | H4 | ✅ | ✅ | 6/6 | ✅ Incluido |
| Donella Meadows | ✅ | ✅ | ❌ | H6 | ❌ | ✅ | 4/6 | ✅ Incluido |

### Verificación de cobertura:

| Habilidad | Expertos asignados | ¿Cubierta? |
|-----------|-------------------|------------|
| H1 | Cagan, Perri | ✅ |
| H2 | Torres, Ries | ✅ |
| H3 | Cagan, Perri | ✅ |
| H4 | Torres, Doerr | ✅ |
| H5 | Cagan | ✅ (1 solo, considerar agregar) |
| H6 | Meadows | ✅ |
| H7 | Cagan | ✅ |
| H8 | Perri, Ries | ✅ |

**Resultado: 0 gaps. Todas las habilidades cubiertas.**
