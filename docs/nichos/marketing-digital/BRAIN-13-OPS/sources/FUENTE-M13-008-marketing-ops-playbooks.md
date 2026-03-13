---
source_id: "FUENTE-M13-008"
brain: "brain-marketing-13-ops"
niche: "marketing-digital"
title: "Marketing Operations Playbooks: Documentation, Processes, and Scaling"
author: "Marketing Ops Community"
expert_id: "EXP-M13-008"
type: "guide"
language: "en"
year: 2023
isbn: null
url: "https://www.marketingops.com/"
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

habilidad_primaria: "Documentación de procesos, playbooks y runbooks para marketing operations"
habilidad_secundaria: "SOPs, escalabilidad de equipos, handoffs, SLAs, training programs"
capa: 2
capa_nombre: "Frameworks Operativos"
relevancia: "ALTA — La documentación de procesos es lo que permite que el marketing escale. Sin playbooks, cada nuevo miembro del equipo reinventa el proceso y cada proceso único depende de una sola persona (bus factor)."
---

# FUENTE-M13-008: Marketing Operations Playbooks

## Tesis Central

> **"Si algo no está documentado, no existe como proceso escalable. La tacit knowledge (lo que está en la cabeza del experto) no se escala. Convertir tacit knowledge en explicit documentation (playbooks, runbooks, SOPs) es la función más importante de marketing ops."**

---

## 1. Principios Fundamentales

### Tacit vs. Explicit Knowledge

**Tacit Knowledge:**
- Está en la cabeza de la persona experta
- Difícil de transferir
- Se pierde si la persona se va
- No escala (single point of failure)

**Explicit Knowledge:**
- Está documentado
- Fácil de transferir
- Permanece aunque la persona se vaya
- Escala infinitamente

Marketing Ops es la disciplina de convertir tacit → explicit.

*Fuente: MarketingOps.com, "Knowledge Management" (2023)*

### Los 4 tipos de documentación de Marketing Ops

1. **SOP (Standard Operating Procedure)**
   - Procedimientos paso a paso, repetitivos
   - Ejemplo: "Cómo crear una campaña de email en HubSpot"

2. **Playbook**
   - Guía estratégica con opciones y criterios de decisión
   - Ejemplo: "Cómo decidir qué canal usar para cada campaña"

3. **Runbook**
   - Procedimientos de respuesta a incidentes
   - Ejemplo: "Qué hacer si el email server cae"

4. **Cheat Sheet**
   - Referencia rápida, one-pager
   - Ejemplo: "HTML tags permitidos en email"

*Fuente: MarketingOps.com, "Documentation Types" (2023)*

---

## 2. Frameworks y Metodologías

### Framework: SOP Template Standard

Un SOP efectivo debe tener:

```
TITLE: [Acción específica]
OWNER: [Quién es responsable del proceso]
LAST UPDATED: [Fecha]

PURPOSE:
└── ¿Por qué existe este proceso? ¿Qué outcome logra?

PREREQUISITES:
└── Qué herramientas, acceso, o info se necesita antes

STEP-BY-STEP:
1. [Action]
   └── Detail con screenshot si es complejo
2. [Action]
   └── Detail

TROUBLESHOOTING:
└── Qué hacer si algo falla en el proceso

EXAMPLES:
└── Ejemplo de output exitoso
```

*Fuente: MarketingOps.com, "SOP Template" (2023)*

### Framework: Playbook para Campaign Launch

**Pre-launch (2 semanas antes):**
- [ ] Brief de campaña aprobado
- [ ] Creative assets (images, copy) listos
- [ ] Landing page construida y testeada
- [ ] Tracking configurado (UTM params, GA4 goals)
- [ ] Budget aprobado

**Launch (día 0):**
- [ ] QA de todos los links
- [ ] Test send de email
- [ ] Campaign schedule activado
- [ ] Monitoring configurado

**Post-launch (48 horas):**
- [ ] Check deliverability
- [ ] Check basic metrics (open rate, click rate)
- [ ] Optimization temprana si es necesario

**Post-campaign (1 semana después):**
- [ ] Report completo
- [ ] Learnings documentados
- [ ] Propuesta de mejoras para siguiente

*Fuente: MarketingOps.com, "Campaign Launch Playbook" (2023)*

### Framework: SLAs entre Marketing y Sales

Service Level Agreement típico:

| SLA | Marketing → Sales | Sales → Marketing |
|-----|-------------------|-------------------|
| **MQL handoff** | Contactar dentro de 24h | Pasar lead qualified |
| **Feedback** | Feedback sobre % de closure semanal | Actualizar lead score |
| **Data quality** | Datos limpios y completos en CRM | Reportar data issues en 48h |
| **Campaign planning** | Invitar a planning quarterly | Input en objetivos trimestrales |

**Reunión mensual:** Revisar SLAs, ajustar según realidad.

*Fuente: MarketingOps.com, "Sales-Marketing SLA" (2023)*

---

## 3. Modelos Mentales

### "La documentación viva se actualiza o muere"

La documentación que no se actualiza pierde credibilidad. Si el proceso cambió pero el doc no, el equipo deja de usarlo y vuelve a tacit knowledge.

**Regla:** Cada proceso documentado debe tener owner y fecha de última revisión. Revisar trimestralmente.

*Fuente: MarketingOps.com, "Doc Maintenance" (2023)*

### "Friction in documentation = friction in adoption"

Si el SOP es de 50 pasos con screenshots de hace 3 años, nadie lo va a seguir. La documentación debe ser lo más simple posible, y lo más visual posible (screenshots, GIFs, videos).

*Fuente: MarketingOps.com, "Usable Documentation" (2023)*

---

## 4. Criterios de Decisión

### Qué documentar primero

Priorizar según impacto × frecuencia:

```
ALTA PRIORIDAD (Impacto alto, frecuencia alta):
- Campaign launch process
- Lead handoff marketing → sales
- Reporting mensual estándar

MEDIA PRIORIDAD:
- Herramientas usadas semanalmente
- Procesos de QA de creativos
- Integraciones troubleshooting

BAJA PRIORIDAD (Impacto bajo, frecuencia baja):
- Procesos raros (migración de datos, setup nuevo vendor)
- Herramientas usadas anualmente
```

*Fuente: MarketingOps.com, "Doc Prioritization" (2023)*

---

## 5. Anti-patrones

### Anti-patrón: Documentar sin consultar a quien hace el trabajo

Marketing Ops a veces documenta procesos observando desde afuera sin entender el "por qué". El resultado: documentación que describe el proceso pero no la lógica.

**Regla:** El experto en el proceso debe ser el primary author o reviewer del doc.

*Fuente: MarketingOps.com, "Doc Creation" (2023)*

### Anti-patrón: Documentación sin training

Tener un playbook perfecto que nadie leyó es tan inútil como no tener playbook. La documentación debe ser parte del onboarding y training continuo.

*Fuente: MarketingOps.com, "Training Integration" (2023)*

### Anti-patrón: Todo en formatos pesados

Un PDF de 80 páginas que nadie va a leer. Dividir en chunks pequeños, cada uno en su propia página/doc, con searchability. Wiki (Notion, Confluence) > PDF.

*Fuente: MarketingOps.com, "Format Best Practices" (2023)*
