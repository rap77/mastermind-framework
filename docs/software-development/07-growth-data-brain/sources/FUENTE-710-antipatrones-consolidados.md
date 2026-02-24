---
source_id: "FUENTE-710"
brain: "brain-software-07-growth-data"
niche: "software-development"
title: "Anti-patrones Consolidados de los 6 Cerebros — Compilación Interna"
author: "MasterMind Framework (auto-generated)"
expert_id: "N/A"
type: "internal_compilation"
language: "es"
generated_from: "anti-patrones de fuentes maestras de cerebros 01-06"
skills_covered: ["HR1", "HR2", "HR3", "HR4", "HR5", "HR6"]
version: "1.0.0"
last_updated: "2026-02-23"
changelog:
  - "v1.0.0: Template inicial — se auto-genera con mastermind brain compile-radar --brain 07"
status: "template"
distillation_date: "2026-02-23"
distillation_quality: "template_only"
loaded_in_notebook: false
auto_generated: true
generate_command: "mastermind brain compile-radar --brain 07"
---

# FUENTE-710: Anti-patrones Consolidados

## Propósito

Compilación de TODOS los anti-patrones extraídos de las fuentes maestras de los cerebros 01-06. El Cerebro #7 usa este documento para detectar rápidamente cuándo un output cae en un error conocido.

**Comando para regenerar:** `mastermind brain compile-radar --brain 07`

**Cuándo regenerar:** Cada vez que se agreguen o actualicen fuentes maestras de cualquier cerebro.

---

## Anti-patrones por Cerebro

### Cerebro #1 — Product Strategy

> *Compilado de: FUENTE-001 a FUENTE-010*

| ID | Anti-patrón | Señal | Severidad |
|----|-------------|-------|-----------|
| AP-101 | Feature factory / Build trap | Medir éxito por features lanzadas, no por impacto | CRÍTICA |
| AP-102 | Roadmap de feature requests | Roadmap dictado por ventas/clientes sin validación | ALTA |
| AP-103 | PM como camarero de stakeholders | PM ejecuta pedidos sin cuestionar el "por qué" | ALTA |
| AP-104 | Discovery como proyecto puntual | Hacer discovery al inicio y nunca más | MEDIA |
| AP-105 | OKRs como outputs | Key Results son features ("lanzar X") en vez de outcomes ("retención +5%") | ALTA |
| AP-106 | Espacio de soluciones sin explorar oportunidades | Saltar directamente a soluciones sin mapear el opportunity space | ALTA |
| AP-107 | Validar solo con stakeholders internos | "Validamos con el equipo" en vez de con usuarios reales | CRÍTICA |
| AP-108 | Ignorar el riesgo de viabilidad de negocio | Producto que nadie compra porque no se evaluó willingness-to-pay | ALTA |
| AP-109 | Celebrating launches instead of outcomes | La cultura premia el lanzamiento, no el impacto | MEDIA |
| AP-110 | Assumption stacking | Múltiples suposiciones no validadas apiladas como base de una decisión | CRÍTICA |

### Cerebro #2 — UX Research

| ID | Anti-patrón | Señal | Severidad |
|----|-------------|-------|-----------|
| AP-201 | Leading questions en entrevistas | "¿No crees que sería mejor si...?" en vez de preguntas abiertas | ALTA |
| AP-202 | Investigar para confirmar, no para descubrir | Buscar datos que confirmen la hipótesis del equipo | CRÍTICA |
| AP-203 | Sample size de 1-2 usuarios | Conclusiones basadas en anécdotas, no en patrones | ALTA |
| AP-204 | Preguntar a usuarios del segmento equivocado | Entrevistar usuarios que no son el target | ALTA |
| AP-205 | Confundir lo que dicen con lo que hacen | Los usuarios dicen una cosa y hacen otra | MEDIA |

### Cerebro #3 — UI/UX Design

| ID | Anti-patrón | Señal | Severidad |
|----|-------------|-------|-----------|
| AP-301 | Diseño por tendencia sin función | Usar glassmorphism/neumorphism porque "está de moda" | MEDIA |
| AP-302 | Ignorar estados edge | No diseñar: vacío, error, loading, permisos, offline | ALTA |
| AP-303 | Estética sobre claridad | El diseño es bonito pero el usuario no sabe qué hacer | ALTA |
| AP-304 | No testear con usuarios reales | "Se ve bien" no es validación | ALTA |
| AP-305 | Accessibility como afterthought | Diseñar sin considerar contraste, tamaños, screen readers | MEDIA |

### Cerebro #4 — Frontend Development

| ID | Anti-patrón | Señal | Severidad |
|----|-------------|-------|-----------|
| AP-401 | Performance como afterthought | Bundle de 5MB, LCP > 5s, "después lo optimizamos" | ALTA |
| AP-402 | Ignorar mobile | Desktop-first sin responsive design | ALTA |
| AP-403 | Over-engineering de componentes | Sistema de componentes de 50 abstracciones para 3 pantallas | MEDIA |
| AP-404 | No manejar errores de red | La app se rompe cuando la conexión es lenta | ALTA |
| AP-405 | Copy-paste en vez de componentes reutilizables | Duplicación de código que genera inconsistencia | MEDIA |

### Cerebro #5 — Backend Development

| ID | Anti-patrón | Señal | Severidad |
|----|-------------|-------|-----------|
| AP-501 | No rate limiting en APIs públicas | Vulnerable a DDoS y abuse | CRÍTICA |
| AP-502 | Queries N+1 | Loop de queries que destruye performance | ALTA |
| AP-503 | Secrets en código | API keys, passwords en repos, env files commiteados | CRÍTICA |
| AP-504 | Single point of failure | Un solo servidor, sin redundancia, sin backup | CRÍTICA |
| AP-505 | No logging | Cuando algo falla, nadie sabe por qué | ALTA |
| AP-506 | Arquitectura astronaut | Microservicios para un MVP con 100 usuarios | MEDIA |
| AP-507 | No validar inputs | SQL injection, XSS, y otros ataques por inputs no sanitizados | CRÍTICA |

### Cerebro #6 — QA & DevOps

| ID | Anti-patrón | Señal | Severidad |
|----|-------------|-------|-----------|
| AP-601 | "Después escribimos los tests" | Tests que nunca se escriben porque no hay "después" | ALTA |
| AP-602 | Deploy manual del viernes a las 5pm | Sin CI/CD, sin rollback, en el peor momento | CRÍTICA |
| AP-603 | No monitoring en producción | Los usuarios reportan los problemas antes que el equipo | ALTA |
| AP-604 | Un solo environment | Desarrollar, testear, y producción en el mismo lugar | ALTA |
| AP-605 | Tests que no testean nada | Tests que siempre pasan, 100% coverage pero 0% de utilidad | MEDIA |

---

## Tabla de Severidades

| Severidad | Acción del #7 | Ejemplos |
|-----------|--------------|----------|
| **CRÍTICA** | REJECT inmediato si se detecta | AP-101, AP-107, AP-110, AP-501, AP-503, AP-504, AP-507, AP-602 |
| **ALTA** | CONDITIONAL — debe corregirse antes de aprobar | AP-102, AP-103, AP-105, AP-106, AP-108, AP-201-204, AP-302-304, AP-401-404, AP-502, AP-505-506, AP-601, AP-603-604 |
| **MEDIA** | Nota en el reporte — no bloquea aprobación pero se recomienda corregir | AP-104, AP-109, AP-205, AP-301, AP-305, AP-403, AP-405, AP-605 |

## Estadísticas

- **Total de anti-patrones catalogados:** 37
- **Críticos:** 8 (rechazo automático)
- **Altos:** 21 (bloquean aprobación)
- **Medios:** 8 (recomendación)

---

## Cómo Usa el #7 este Documento

1. Recibe output del Cerebro X
2. Consulta los anti-patrones del Cerebro X en este documento
3. Para cada anti-patrón, busca la "señal" en el output
4. Si encuentra una señal de severidad CRÍTICA → REJECT
5. Si encuentra señales de severidad ALTA → CONDITIONAL con instrucciones
6. Si encuentra señales de severidad MEDIA → Nota en el reporte

**Nota:** Este documento es complementario al bias-catalog.yaml. Los anti-patrones son errores de dominio. Los sesgos son errores de pensamiento. Ambos deben verificarse.
