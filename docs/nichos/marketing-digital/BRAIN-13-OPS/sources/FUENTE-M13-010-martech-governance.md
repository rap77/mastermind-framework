---
source_id: "FUENTE-M13-010"
brain: "brain-marketing-13-ops"
niche: "marketing-digital"
title: "Marketing Technology Governance: Continuous Optimization and Lifecycle Management"
author: "Scott Brinker / Frans Riemersma"
expert_id: "EXP-M13-010"
type: "blog_series"
language: "en"
year: 2023
isbn: null
url: "https://chiefmartec.com/technology-governance/"
skills_covered: ["H1", "H3", "H5", "H7"]
distillation_date: "2026-03-12"
distillation_quality: "complete"
loaded_in_notebook: false
version: "1.0.0"
last_updated: "2026-03-12"
changelog:
  - version: "1.0.0"
    date: "2026-03-12"
    changes:
      - "Ficha creada con destilación completa"
status: "active"

habilidad_primaria: "Governance del stack de marketing technology: optimización continua, lifecycle management"
habilidad_secundaria: "Vendor management, tool rationalization, MarTech governance board, cost optimization"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — La governance del MarTech es lo que evita que el stack se convierta en un Frankenstein de herramientas no integradas. Brinker y Riemersma documentan los procesos de revisión trimestral, optimización, y offboarding que deben ser parte de marketing ops."
---

# FUENTE-M13-010: Marketing Technology Governance (Brinker/Riemersma)

## Tesis Central

> **"El stack de marketing es un organismo vivo. Las herramientas se agregan, se reemplazan, se deprecian. Sin governance — un proceso sistemático de revisión y optimización — el stack se pudre: herramientas obsoletas, integraciones rotas, costos excesivos. La governance es la disciplina de mantener el stack saludable."**

---

## 1. Principios Fundamentales

### El ciclo de vida de una herramienta MarTech

Toda herramienta pasa por fases:

1. **Evaluation:** Assessing options, selecting vendor
2. **Onboarding:** Implementation, training, adoption
3. **Peak Usage:** Maximum value extraction (meses 6-24)
4. **Decline:** Necesidad decrease, mejor opción aparece, vendor degrada
5. **Sunset:** Offboarding, migration, decommission

**El error:** Muchas empresas se quedan en fase 4 (decline) por años por inercia, pagando por herramientas que ya no aportan valor.

*Fuente: Brinker, "Tool Lifecycle" (chiefmartec.com, 2023)*

### Los 5 pecados capitales del MarTech sin governance

1. **Shadow IT:** Marketing compra herramientas sin ops knowledge
2. **Feature creep:** Vendors agregan features que nadie pidió
3. **Integration debt:** Nuevas herramientas sin plan de integración
4. **Shelfware accumulation:** Herramientas pagadas pero no usadas
5. **Vendor lock-in:** Imposible migrar porque el data está atrapado

*Fuente: Riemersma, "MarTech Sins" (stackmaven.com, 2023)*

---

## 2. Frameworks y Metodologías

### Framework: Quarterly MarTech Review

Brinker recomienda una revisión trimestral del stack:

**Q1 Review (Enero): Budget Alignment**
- [ ] ¿Qué herramientas se usaron activamente?
- [ ] ¿Cuáles no se usaron en Q4?
- [ ] ¿Hay nuevas necesidades de negocio no cubiertas?
- [ ] Output: Lista de herramientas a decommission, nuevas a evaluar

**Q2 Review (Abril): Integration Health**
- [ ] ¿Qué integraciones están fallando?
- [ ] ¿Hay data gaps entre sistemas?
- [ ] ¿Nuevos vendors tienen integraciones disponibles?
- [ ] Output: Plan de mejoras de integración

**Q3 Review (Julio): Vendor Performance**
- [ ] ¿Vendors están cumpliendo SLAs?
- [ ] ¿Hay features prometidas no entregadas?
- [ ] ¿Precios aumentaron sin valor añadido?
- [ ] Output: Lista de vendors a reevaluar

**Q4 Review (Octubre): Strategic Planning**
- [ ] ¿Stack alinea con planes del año siguiente?
- [ ] ¿Qué tendencias (AI, privacy) afectan el stack?
- [ ] Presupuesto del próximo año
- [ ] Output: Roadmap de MarTech para Año+1

*Fuente: Brinker, "Quarterly Review Framework" (chiefmartec.com, 2023)*

### Framework: Tool Rationalization Matrix

Categorizar herramientas en 4 cuadrantes:

```
                  ALTO USO
                      |
Keep & Optimize    |   Core (Must-Have)
                    |   - Mantener y optimizar
____________________|_______________________
                    |
Retire (Shelfware)  |   Evaluate
                    |   - ¿Necesario?
                    |   - ¿Alternativa mejor?
BAJO USO            |
```

- **Keep & Optimize:** Alto uso, alto valor → optimizar costos, features
- **Core (Must-Have):** Críticas para el negocio → invertir más
- **Evaluate:** Bajo uso pero alto potencial → revisar si falta adoption
- **Retire (Shelfware):** Bajo uso, bajo valor → decommission

*Fuente: Riemersma, "Rationalization Framework" (stackmaven.com, 2023)*

### Framework: Decommission Process

Cuando se decide eliminar una herramienta:

**PASO 1: Data Assessment**
- ¿Qué data vive en esta herramienta?
- ¿Hay historial que necesitemos preservar?
- ¿Hay integraciones que dependen de esta data?

**PASO 2: Migration Plan**
- ¿A qué herramienta migrar el data?
- ¿Export formats disponibles?
- ¿Mapping de campos entre sistemas?

**PASO 3: Integration Updates**
- ¿Qué otras herramientas se integran con esta?
- ¿Qué pasa con esos integrations?
- ¿Notificar a los stakeholders del cambio?

**PASO 4: Communication**
- Notificar a usuarios internos con timeline
- Documentar por qué se elimina (si no, volverán a pedirlo)
- Ofrecer training en la herramienta reemplazante

**PASO 5: Final Cutoff**
- Cancelar suscripción
- Eliminar accesos
- Archivar data por compliance (7 años en algunos casos)

*Fuente: Brinker, "Decommission Checklist" (chiefmartec.com, 2023)*

---

## 3. Modelos Mentales

### "El costo de ownership es mayor que el costo de suscripción"

El precio mensual de la herramienta es solo 30-50% del TCO (Total Cost of Ownership):
- 20-30%: Implementación y setup
- 10-20%: Training y adoption
- 10-20%: Maintenance e integraciones
- 5-10%: Decommission eventual

**Regla:** Calcular TCO de 3 años antes de buy.

*Fuente: Brinker, "TCO Reality" (chiefmartec.com, 2023)*

### "El MarTech stack es un portafolio, no una colección"

Igual que un portafolio de inversiones, el stack debe balancearse:
- Herramientas core (estabilidad, vendors sólidos)
- Herramientas experimentales (innovación, riesgo más alto)
- Cash cows (estable, no necesitan mucha inversión)
- Stars (alto potencial, invertir más)

*Fuente: Riemersma, "Stack Portfolio" (stackmaven.com, 2023)*

---

## 4. Criterios de Decisión

### Cuándo sunset (reemplazar) una herramienta

- **Vendor discontinuó la herramienta:** Inmediatamente migrar
- **Cost increase >20% sin valor añadido:** Evaluar alternativas
- **Adoption <30% de usuarios target:** Training failed o tool no needed
- **Competitor ofrece 2x features al mismo precio:** Strong consideración
- **Soporte degraded:** Response time >48h crítico, tickets sin resolver

*Fuente: Brinker, "Sunset Triggers" (chiefmartec.com, 2023)*

---

## 5. Anti-patrones

### Anti-patrón: Governance sin ownership

Tener un proceso de revisión trimestral sin un owner claro de cada herramienta significa que la revisión no se cumple. Cada herramienta debe tener un owner (persona responsable) que responde por su value y cost.

*Fuente: Brinker, "Tool Ownership" (chiefmartec.com, 2023)*

### Anti-patrón: Premature optimization

Optimizar el stack antes de que tenga suficiente data (6-12 meses de uso) lleva a decisiones basadas en ansiedad, no evidencia. Dejar que la herramienta se use antes de juzgar.

*Fuente: Riemersma, "Patience in Evaluation" (stackmaven.com, 2023)*

### Anti-patrón: Ignorar el vendor roadmap

Los vendors lanzan nuevas features constantemente. Ignorar el roadmap significa perder oportunidad de features que podrían reemplazar integraciones custom costosas.

*Fuente: Brinker, "Vendor Roadmap Monitoring" (chiefmartec.com, 2023)*
