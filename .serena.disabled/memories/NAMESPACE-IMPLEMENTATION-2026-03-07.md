# Namespace Implementation - 2026-03-07

## Fecha
2026-03-07

## Implementación Completada ✅

**Commit:** daf6b7f

Todos los recursos de Claude Code ahora usan namespace `mm:` para evitar conflictos con otros proyectos.

## Cambios Realizados

### 1. Estructura de Carpetas

```
.claude/
├── commands/
│   └── mm/                    # Namespace para slash commands
│       ├── ask-product.md     # → /mm:ask-product
│       ├── ask-ux.md          # → /mm:ask-ux
│       ├── ask-design.md      # → /mm:ask-design
│       ├── ask-frontend.md    # → /mm:ask-frontend
│       ├── ask-backend.md     # → /mm:ask-backend
│       ├── ask-qa.md          # → /mm:ask-qa
│       ├── ask-growth.md      # → /mm:ask-growth
│       ├── ask-all.md         # → /mm:ask-all
│       ├── ask-ui-docs.md     # → /mm:ask-ui-docs
│       ├── project-health-check.md  # → /mm:project-health-check
│       ├── audit.md           # → /mm:audit
│       ├── lite-prd-generator.md    # → /mm:lite-prd-generator
│       ├── prd-clarifier.md   # → /mm:prd-clarifier
│       ├── generate-prp.md    # → /mm:generate-prp
│       ├── execute-prp.md     # → /mm:execute-prp
│       ├── improve-prompt.md  # → /mm:improve-prompt
│       ├── ux-spec-to-prompt.md  # → /mm:ux-spec-to-prompt
│       └── explore-first.md   # → /mm:explore-first
│
├── hooks/
│   └── mm/                    # Namespace para hooks (pendiente)
│
└── agents/
    └── mm/                    # Namespace para agentes (pendiente)
```

### 2. Comandos Disponibles

**Consulta de Cerebros:**
- `/mm:ask-product` - Consulta cerebro Producto
- `/mm:ask-ux` - Consulta cerebro UX Research
- `/mm:ask-design` - Consulta cerebro UI Design
- `/mm:ask-frontend` - Consulta cerebro Frontend
- `/mm:ask-backend` - Consulta cerebro Backend
- `/mm:ask-qa` - Consulta cerebro QA/DevOps
- `/mm:ask-growth` - Consulta cerebro Growth/Data
- `/mm:ask-all` - Consulta TODOS los cerebros
- `/mm:ask-ui-docs` - Genera documentación de design system

**Gestión de Proyectos:**
- `/mm:project-audit` - Análisis completo de 7 cerebros
- `/mm:audit` - Alias rápido de project-audit

**PRDs y Especificaciones:**
- `/mm:lite-prd-generator` - Convierte idea en PRD
- `/mm:prd-clarifier` - Refina PRD existente
- `/mm:generate-prp` - Crea PRP
- `/mm:execute-prp` - Ejecuta PRP

**Mejora de Prompts:**
- `/mm:improve-prompt` - Transforma prompts genéricos
- `/mm:ux-spec-to-prompt` - Convierte specs UX en prompts

**Desarrollo:**
- `/mm:explore-first` - Explora código antes de implementar

### 3. Convención de Nombres

**Reglas:**
1. Usar nombres limpios sin prefijo en el archivo
   - ✅ `ask-product.md` → `/mm:ask-product`
   - ❌ `mm-ask-product.md` → `/mm:mm-ask-product` (redundante)

2. El namespace viene de la carpeta contenedora
   - `.claude/commands/mm/archivo.md` → `/mm:archivo`

3. Ser descriptivo pero conciso
   - ✅ `ask-product.md`
   - ❌ `ask-to-the-product-brain-about-something.md`

### 4. Documentación Creada

**Nuevo archivo:** `.claude/README.md`
- Explicación de la estructura de namespace
- Lista completa de comandos disponibles
- Instrucciones de instalación en proyectos externos
- Convención de nombres para nuevos recursos

**README.md actualizado:**
- Nueva sección "Claude Code Slash Commands"
- Lista de comandos /mm: organizados por categoría
- Instrucciones de instalación en proyectos externos

### 5. Git Tracking

- Todos los archivos movidos con `git mv` para preservar historial
- Git reconoce los movimientos como renames (100%)
- Commit con mensaje descriptivo del cambio

## Uso en Proyectos Externos

```bash
# Copiar todos los recursos mm:
cp -r /path/to/mastermind/.claude /path/to/your-project/

# O solo los comandos:
cp -r /path/to/mastermind/.claude/commands/mm /path/to/your-project/.claude/commands/
```

## Beneficios

1. **Identificación clara:** Todos los recursos de MasterMind son fácilmente identificables
2. **Sin conflictos:** Namespace `mm:` no colisiona con otros proyectos
3. **Organización:** Carpetas separadas para commands, hooks, agents
4. **Escalabilidad:** Fácil agregar nuevos recursos siguiendo la convención

## Próximos Pasos (Opcional)

Cuando necesites agregar hooks o agentes específicos de MasterMind:

1. Crear archivos en `.claude/hooks/mm/` o `.claude/agents/mm/`
2. Usar nombres limpios sin prefijo `mm-`
3. El namespace se agrega automáticamente por la carpeta contenedora
