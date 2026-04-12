# Pattern: Niche-Agnostic Brain System

**Problem:** Hardcoded niche context in 7 brain agents makes system difficult to adapt to new domains (e.g., vehicles → real estate → products).

**Solution:** Centralized domain configuration (JSON) + Dynamic context loading script.

## Architecture

```
.claude/
├── domain-config.json          # Central configuration (1 source of truth)
├── load-domain-context.sh       # Script: JSON → Markdown
└── domain-context.md           # Generated: Brains read this
```

## domain-config.json Structure

```json
{
  "project": { "name", "description", "core_value" },
  "business_domain": { "type", "model", "target_market" },
  "niche": { "current", "name", "description" },
  "user_personas": [ { "role", "description", "goals", "pains" } ],
  "outcome_metrics": [ { "name", "target", "description" } ],
  "tech_stack": { "frontend": {...}, "backend": {...} },
  "current_milestone": { "name", "status", "current_phase" }
}
```

## How It Works

1. **Edit domain-config.json** — Change niche (vehicles → real estate)
2. **Run load-domain-context.sh** — Generates domain-context.md
3. **Brains read domain-context.md** — Dynamic context loading

## Benefits

| Aspect | Hardcoded (Old) | Config-Driven (New) |
|--------|-----------------|---------------------|
| Change niche | Edit 7 brains (~20 min) | Edit 1 JSON (~2 min) |
| Error risk | High (copy-paste) | Low (JSON validation) |
| Maintenance | Difficult | Easy |
| Version control | 7 files change | 1 file changes |

## Usage Example

**Change from Vehicles to Real Estate:**
```json
{
  "niche": {
    "current": "real_estate",
    "name": "Real Estate",
    "description": "Venta de propiedades en Zonaprop"
  },
  "user_personas": [
    {
      "role": "agente_inmobiliario",
      "description": "Publica propiedades en Zonaprop"
    }
  ]
}
```

Then run:
```bash
.claude/load-domain-context.sh
```

Brains automatically adapt to new niche.

## When to Use

**Use this pattern when:**
- System needs to support multiple niches/domains
- Frequent domain changes expected
- Multiple projects share same brain architecture
- Reducing maintenance overhead is priority

**Don't use when:**
- Single domain forever (hardcoded is simpler)
- Domain change is extremely rare (<1x per year)

## Implementation Notes

- Script uses `jq` or Python (fallback) to parse JSON
- Generated Markdown format is brain-friendly (easy to read)
- Error handling: Creates default config if missing
- Timestamp in generated file shows freshness

## Discovered In

- **Project:** ProSell SaaS brain system port
- **Date:** 2026-04-10
- **User insight:** "No se puede hacer agnóstico al nicho?" → Led to this pattern
