---
source_id: "FUENTE-M13-009"
brain: "brain-marketing-13-ops"
niche: "marketing-digital"
title: "Marketing Operations en Empresas B2B: Procesos, Stack y Tecnología para el Mercado Hispanohablante"
author: "Juan Pablo Marichal"
expert_id: "EXP-M13-009"
type: "blog_series"
language: "es"
year: 2023
isbn: null
url: "https://www.juanpablomarichal.com/marketing-operations/"
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

habilidad_primaria: "Marketing operations adaptado al mercado hispanohablante: B2B, agencias, SaaS"
habilidad_secundaria: "Stack selection hispano, procesos LATAM/Chile, equipos distribuidos"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — Juan Pablo Marichal es el referente de marketing operations en Chile y LATAM. Su experiencia con empresas B2B y agencias en el mercado hispano aporta contextos culturales y regionales que no existen en la literatura anglosajona."
---

# FUENTE-M13-009: Marketing Operations en Empresas B2B (Juan Pablo Marichal)

## Tesis Central

> **"El marketing operations en LATAM tiene desafíos únicos: equipos distribuidos en múltiples países, presupuestos más ajustados, y un vendor landscape diferente al de EEUU/Europa. Adaptar las mejores prácticas globales a la realidad local es la clave del éxito."**

---

## 1. Principios Fundamentales

### Contexto del Marketing Ops en LATAM

Marichal identifica particularidades:

1. **Equipos distribuidos:** Un mismo equipo ops soporta marketing en Chile, México, Colombia, Argentina
2. **Vendor landscape diferente:** En LATAM, herramientas como Localyx (Brasil), Despegar, MercadoLibre tienen APIs propias
3. **Presupuestos más ajustados:** El ROI de MarTech se mide más estrictamente; shelfware no es opción
4. **Regulación heterogénea:** Cada país tiene su propia ley de privacidad (Chile: Ley de Protección de Datos, Brasil: LGPD, etc.)
5. **Máis relación personal:** La vendor relationship en LATAM depende más del contacto humano que en EEUU

*Fuente: Marichal, "Marketing Ops LATAM" (2023)*

### El desafío de los teams remotos distributed

Con equipos en Santiago, Buenos Aires, México DF, y Bogotá:

**Desafíos:**
- Timezones (Chile -2 a México, Colombia -5 a Chile)
- Culturas laborales diferentes
- Comunicación async-heavy

**Soluciones:**
- Overlap de 2-3 horas entre todos los timezones
- Documentación en español (language = inclusión)
- Playbooks específicos para async communication
- Reunión semanal de team sync síncrona

*Fuente: Marichal, "Distributed Teams" (2023)*

---

## 2. Frameworks y Metodologías

### Framework: Stack MarTech para B2B LATAM

Stack optimizado para empresas B2B hispanas:

```
CORE CRM:
├── HubSpot (SaaS B2B) o Salesforce (enterprise)
└── Pipedrive (SMB, presupuesto ajustado)

AUTOMATION:
├── HubSpot Workflows (si usan HubSpot CRM)
└── ActiveCampaign (presupuesto bajo)

EMAIL:
├── SendGrid (transactional)
└── Mailchimp/Klaviyo (marketing)

COMMUNICATION:
├── Slack (team comms - estándar)
└── WhatsApp Business (LATAM específico)

ANALYTICS:
├── GA4 (web)
└── Looker Studio (dashboards)

LOCAL (LATAM-specific):
├── MercadoLibre (e-commerce en ciertos países)
└── Integraciones con pasarelas locales (Transbank, MercadoPago)
```

*Fuente: Marichal, "Stack LATAM" (2023)*

### Framework: SLA entre Marketing y Ops en Agencias

En agencias hispanas, la relación marketing → ops es crítica:

**Marketing (Agency side) solicita:**
- Campañas lanzadas en 48h de brief completo
- Reports completos antes del día 5 de cada mes
- Creativos adaptados para cada país

**Ops (Agency side) compromete:**
- Deliverability >95%
- Uptime de sistemas >99.5%
- Resolución de incidentes críticos en <4 horas

**Reunión quincenal:** Revisar SLAs, ajustar expectativas.

*Fuente: Marichal, "Agency Ops SLA" (2023)*

### Framework: Hiring para Marketing Ops en LATAM

Perfiles que Marichal busca para su equipo:

1. **Marketing Ops Generalist**
   - Conocimiento de CRM + Automation + Analytics
   - English fluido (para leer docs)
   - Experiencia en B2B SaaS

2. **Data Analyst (Marketing)**
   - SQL + Excel avanzado
   - GA4 + Looker Studio
   - Mentalidad de curiosity en datos

3. **Marketing Technologist**
   - Technical background (APIs, integraciones)
   - Understanding de marketing needs
   - Bilingual para comunicarse con vendors

**Challenge:** En Chile/Argentina, estos perfiles son escasos y costosos. La retención es clave.

*Fuente: Marichal, "Hiring Ops" (2023)*

---

## 3. Modelos Mentales

### "En LATAM, la relación personal con el vendor es un diferenciador"

Marichal nota que en EEUU, la relación vendor-cliente es transaccional. En LATAM, tener un contacto directo en el vendor (WhatsApp, email personal) puede hacer la diferencia en support prioritario.

**Implicación:** No subestimar el valor de construir relaciones con vendors.

*Fuente: Marichal, "Vendor Relationships LATAM" (2023)*

### "El presupuesto limitado obliga a ser más estratégicos"

Con budgets 30-50% menores que en EEUU, las empresas B2B LATAM no pueden permitirse MarTech bloat. Cada herramienta debe tener ROI justificado documentado.

**Beneficio:** Las stacks LATAM tienden a ser más simples y menos redundantes.

*Fuente: Marichal, "Budget Constraints" (2023)*

---

## 4. Criterios de Decisión

### Cuándo usar herramienta global vs. local en LATAM

| Criterion | Global tool | Local tool |
|-----------|-------------|------------|
| **Core CRM/MA** | HubSpot/Salesforce (mejor soporte) | Solo si no hay alternativa |
| **Pasarelas de pago** | Stripe (SaaS global) | MercadoPago/Transbank (local es must) |
| **Ads** | Google/Meta ads (globales) | Local ads solo si domina el país |
| **Analytics** | GA4 (universal) | Local no needed |

**Regla:** Core systems = global; Payments y algunos Ads = local.

*Fuente: Marichal, "Global vs Local" (2023)*

---

## 5. Anti-patrones

### Anti-patrón: Copiar playbooks de EEUU sin adaptación

Un playbook de campaign planning de EEUU asume presupuestos, timelines, y recursos que no existen en la mayoría de empresas LATAM. Adaptar antes de implementar.

*Fuente: Marichal, "Copy-Paste Failure" (2023)*

### Anti-patrón: Ignorar la regulación de datos locale

Chile (Ley 19.628), Argentina (Ley de Protección de Datos Personales), y Brasil (LGPD) tienen requisitos específicos. Asumir que GDPR compliance es suficiente es un error.

*Fuente: Marichal, "Local Regulations" (2023)*

### Anti-patrón: No considerar el factor cultural

El messaging que funciona en EEUU puede ofender o simplemente no resonar en culturas latinas. El ops team debe validar no solo la técnica sino también el messaging cultural de las campañas.

*Fuente: Marichal, "Cultural Fit" (2023)*
