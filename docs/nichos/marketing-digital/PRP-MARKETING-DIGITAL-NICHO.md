# PRP-MARKETING-001: Nicho Marketing Digital y Redes Sociales

## Objetivo
Crear el nicho **Marketing Digital y Redes Sociales** para el MasterMind Framework, con 16 cerebros especializados y ~100+ expertos world-class destilados.

## Especificación Técnica

### Estructura de Archivos
```
docs/
└── nichos/
    └── marketing-digital/
        ├── PROPUESTA-16-CEREBROS.md    ✅ (creado)
        ├── BRAINS-MARKETING.yaml        (pendiente)
        └── sources/                     (pendiente)
            ├── BRAIN-01-STRATEGY/
            │   ├── FUENTE-001-april-dunford-positioning.md
            │   ├── FUENTE-002-seth-godin-marketing.md
            │   └── ...
            ├── BRAIN-02-BRAND/
            ├── BRAIN-03-CONTENT/
            ├── BRAIN-16-GROWTH-PARTNER/
            └── ...

mastermind_cli/
└── config/
    └── brains-marketing.yaml           (pendiente, 16 brains)

agents/
└── brains/
    ├── marketing-01-strategy.md        (pendiente)
    ├── marketing-02-brand.md
    ├── ...
    └── marketing-16-growth-partner.md
```

### Expertos de Habla Hispana (~30+ incluidos)

Expertos clave latinos/españoles en los cerebros:

- **Margarita Pasos** (México) - #1, #4, #9, #14 - Estrategia, Social, Email, Influencers
- **Jesús Tronchoni** (España) - #6, #7, #8, #11 - SEM, SEO, Link Building, Analytics
- **Patrick Campbell** (hispano hablante) - #10, #16 - Retention, Pricing
- **Sergi Silva** (España) - #1 - Positioning
- **Nuria Vilanova** (España) - #1 - Brand Strategy
- **Fernando Del Vecchio** (Argentina) - #2 - Brand Design
- **Patricia Soto** (México) - #3, #9 - Copywriting, Email
- **Lidia García** (España) - #4, #5 - LinkedIn Organic & Paid
- **César Sandoval** (México) - #4, #5, #16 - Twitter, Creativos, Partnerships
- **Alejandro Magallanes** (México) - #6, #11 - SEM, Data Visualization
- **Germán Rondón** (Venezuela) - #8 - SEO Content
- **Ramón Gavira** (España) - #12 - CRO
- **Ignacio Alamillo** (España) - #9, #13 - Email Automation, Marketing Ops
- **Ana Fernández** (España) - #15 - Community Strategy
- **Lorena Martínez** (México) - #15 - Community Management
- **Sergio Rama** (España) - #5, #16 - Meta Ads, Agency Growth
- **Juan Pablo Marichal** (Chile) - #13, #16 - Automation, Agency Growth

**Total: 17+ expertos de habla hispana identificados** (más serán agregados durante la fase de investigación)

### 16 Cerebros del Nicho

| ID | Nombre | NotebookLM | System Prompt | Expertos (~8-10 cada uno) |
|----|--------|------------|---------------|---------------------------|
| M1 | Marketing Strategy & Positioning | pendiente | agents/brains/marketing-01-strategy.md | April Dunford, Seth Godin, Elena Verna, Hormozi, Geoffrey Moore, Marty Neumeier, Kyle Poyar, Christopher Lochhead |
| M2 | Brand Identity & Design | pendiente | agents/brains/marketing-02-brand.md | Sagi Haviv, Debbie Millman, Alina Wheeler, Brian Collins, David Aaker, Marty Neumeier |
| M3 | Content Strategy & Copywriting | pendiente | agents/brains/marketing-03-content.md | Joanna Wiebe, Joe Pulizzi, Donald Miller, Andy Crestodina, Amy Posner, Neville Medhora, Brian Dean |
| M4 | Social Media Organic | pendiente | agents/brains/marketing-04-social-organic.md | Jasmine Star, Rachel Pedersen, Justin Welsh, Katelyn Bourgoin, Brianne Fleming, Codie Sanchez, Jonah Berger |
| M5 | Social Media Paid | pendiente | agents/brains/marketing-05-social-paid.md | Dennis Yu, Nicholas Kusmich, Molly Pittman, Ernie San, AJ Wilcox, Tom Breeze, Jesse Kazemi |
| M6 | Search PPC (Google/Bing) | pendiente | agents/brains/marketing-06-search-ppc.md | Perry Marshall, Mike Rhodes, Frederick Vallaeys, Larry Kim, Oli Gardner, Hanapin experts |
| M7 | SEO Technical | pendiente | agents/brains/marketing-07-seo-technical.md | Aleyda Solis, Brian Dean, Barry Schwartz, Cyrus Shepard, Annie Cushing, Marie Haynes, Rand Fishkin |
| M8 | SEO Content & Link Building | pendiente | agents/brains/marketing-08-seo-content.md | Andy Crestodina, Jon Cooper, Lily Ray, Ross Hudgens, Neil Patel, Stuart Davidson, Joy Hawkins |
| M9 | Email Marketing & Automation | pendiente | agents/brains/marketing-09-email.md | Ann Handley, Ryan Deiss, Val Geisler, Jepsen Crame, Joanna Wiebe (email), Return Path experts |
| M10 | Push, SMS & Retention | pendiente | agents/brains/marketing-10-retention.md | Postscript team, TatianaPHONE, ProfitWell (Patrick Campbell), Casey Accurso, Baremetrics, Rob Wu |
| M11 | Marketing Analytics & Data | pendiente | agents/brains/marketing-11-analytics.md | Avinash Kaushik, Simo Ahava, Peep Laja, Ronny Kohavi, Neil Patel, Mark Jeffery |
| M12 | CRO | pendiente | agents/brains/marketing-12-cro.md | Peep Laja (ConversionXL), Oli Gardner, Brian Bui, Russell Brunson, Huyen Tue, Optimizely team |
| M13 | Marketing Automation & Ops | pendiente | agents/brains/marketing-13-ops.md | Scott Brinker, Carlos Hidalgo, Zapier experts, Marketo team, HubSpot experts, Stack Mavin |
| M14 | Influencer & Partnerships | pendiente | agents/brains/marketing-14-influencer.md | Neal Schaffer, Joe Gagliese, Shawn Collins, Li Jin, Pat Flynn, Brianne Fleming |
| M15 | Community Building | pendiente | agents/brains/marketing-15-community.md | CMX team, David Spinks, Brianne Fleming, Reddit/Discord experts, GoPro team, Influitive |
| M16 | Growth Partner (Evaluator) | pendiente | agents/brains/marketing-16-growth-partner.md | Blair Enns, Carl Goulds, Marcel Petitpas, Gainsight experts, Patrick Campbell, agency growth specialists |

## Plan de Implementación

### Fase 1: Estructura y Configuración (2 horas)
- [ ] Crear `mastermind_cli/config/brains-marketing.yaml`
- [ ] Crear estructura de directorios `docs/nichos/marketing-digital/sources/`
- [ ] Actualizar `mastermind_cli/config/brains.yaml` para soportar multi-nicho

### Fase 2: System Prompts (4 horas)
- [ ] Crear 16 system prompts base en `agents/brains/marketing-*.md`
- [ ] Cada prompt debe incluir:
  - Rol y responsabilidades
  - Frameworks operativos del experto
  - Modelos mentales clave
  - Criterios de decisión
  - Mecanismo de retroalimentación

### Fase 3: Fuentes Maestras (40+ horas)
- [ ] Para cada cerebro (~10 expertos × 16 cerebros = ~160 fuentes):
  - [ ] Investigar expertos principales (libros, cursos, podcasts, newsletters)
  - [ ] Crear FUENTE-*.md con formato YAML front matter
  - [ ] Destilar contenido en 5 secciones (principios, frameworks, modelos, criterios, anti-patrones)
  - [ ] Validar calidad de destilación

### Fase 4: Carga en NotebookLM (8 horas)
- [ ] Crear notebook para cada cerebro (16 notebooks)
- [ ] Cargar fuentes (~10 por cerebro)
- [ ] Configurar notebook con: `[CEREBRO] {Nombre} - Marketing Digital`
- [ ] Obtener notebook_id para cada cerebro

### Fase 5: Integración y Testing (4 horas)
- [ ] Actualizar `brains-marketing.yaml` con notebook_ids
- [ ] Integrar en orquestador (soporte multi-nicho)
- [ ] Testing con briefs reales de agencia de marketing
- [ ] Validar calidad de outputs

## Tareas por Hacer

### Inmediatas (esta sesión)
1. ✅ Validar estructura de 16 cerebros
2. ✅ Crear PROPUESTA-16-CEREBROS.md
3. ✅ Crear este PRP
4. [ ] Commitear cambios
5. [ ] Crear `brains-marketing.yaml` con estructura base

### Próximos Pasos (siguiente sesión)
1. Crear system prompts para los 16 cerebros
2. Investigar y crear primeras 10 fuentes maestras
3. Crear notebook de prueba para Brain #1 (Strategy)
4. Testing de flujo completo

## Estimaciones

| Tarea | Estimado |
|-------|----------|
| Estructura y Config | 2 horas |
| System Prompts | 4 horas |
| Fuentes Maestras | 40-60 horas |
| NotebookLM Setup | 8 horas |
| Integración | 4 horas |
| Testing | 4 horas |
| **Total** | **62-82 horas (~2-3 semanas)** |

## Éxito

- [ ] Nicho Marketing Digital funcional en el framework
- [ ] 16 cerebros con knowledge destilado
- [ ] Capaz de atender briefs de agencia de marketing digital
- [ ] Modelo replicable para futuros nichos (E-commerce, Fintech, etc.)

---

**Status:** 🟡 En Planeación
**Creado:** 2026-03-09
**Última actualización:** 2026-03-09
